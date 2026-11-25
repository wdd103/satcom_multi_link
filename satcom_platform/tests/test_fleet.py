import copy
import io
import shutil
import unittest
from pathlib import Path

import test_core
from satcom_platform import load_project, validate_project
from satcom_platform.config.fleet import clone_fleet, block, import_scene
from satcom_platform.web import create_app


class FleetTests(unittest.TestCase):
    def setUp(self):
        fixture=test_core.CoreTests()
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        self.project=fixture.project
        self.client=create_app(self.project).test_client()

    def test_clone_creates_tracks_devices_antennas_links_and_sensors(self):
        snap=self.client.get('/api/project').get_json()
        before=copy.deepcopy(snap)
        result=self.client.post('/api/fleet/clone',json={"scenario":snap['scenario'],"tables":snap['tables'],"source_id":"AC1","names":["AC2","AC3"],"lat_step":.1,"alt_step":100})
        self.assertEqual(result.status_code,200,result.get_json())
        data=result.get_json()
        self.assertEqual(len(data['scenario']['links']),8)
        self.assertEqual({s['aircraft_id'] for s in data['scenario']['sensors']},{'AC1','AC2','AC3'})
        self.assertEqual({r['aircraft_id'] for r in data['tables']['track']['rows']},{'AC1','AC2','AC3'})
        self.assertEqual(next(r['alt_m'] for r in data['tables']['track']['rows'] if r['aircraft_id']=='AC3'),'10200.0')
        self.assertEqual(len({r['device_id'] for r in data['tables']['devices']['rows']}),16)
        self.assertEqual(self.client.get('/api/project').get_json()['scenario'],before['scenario'])
        saved=self.client.post('/api/save',json={"scenario":data['scenario'],"tables":data['tables']})
        self.assertEqual(saved.status_code,200,saved.get_json())
        self.assertEqual(len(load_project(self.project).data['aircraft']),3)

    def test_duplicate_aircraft_ids_are_rejected_without_writing(self):
        snap=self.client.get('/api/project').get_json()
        response=self.client.post('/api/fleet/clone',json={"scenario":snap['scenario'],"tables":snap['tables'],"source_id":"AC1","names":["AC1"]})
        self.assertEqual(response.status_code,400)
        self.assertEqual(self.client.get('/api/project').get_json()['tables']['track'],snap['tables']['track'])

    def test_sensor_reference_and_mask_validation(self):
        config=load_project(self.project)
        config.data['sensors'][0]['enabled']=False
        self.assertIn('SENSOR_REFERENCE',{i.code for i in validate_project(config).issues})
        config.data['sensors'][0]['enabled']=True
        config.data['sensors'][0]['mask_file']='missing.bmsk'
        self.assertIn('ASSET_MISSING',{i.code for i in validate_project(config).issues})
        config.data['sensors'][0]['qw']=2
        self.assertIn('SENSOR_QUATERNION',{i.code for i in validate_project(config).issues})

    def test_mask_upload_is_content_addressed_and_not_auto_selected(self):
        before=self.client.get('/api/project').get_json()['scenario']
        content=b'stk.v.12.0\nBEGIN Exclusion\nEND Exclusion\n'
        response=self.client.post('/api/upload/mask',data={'file':(io.BytesIO(content),'Roof.bmsk')})
        self.assertEqual(response.status_code,200)
        path=response.get_json()['path']
        self.assertTrue((self.project/path).is_file())
        response2=self.client.post('/api/upload/mask',data={'file':(io.BytesIO(content),'Roof.bmsk')})
        self.assertEqual(response2.get_json()['path'],path)
        self.assertEqual(self.client.get('/api/project').get_json()['scenario'],before)
        invalid=self.client.post('/api/upload/mask',data={'file':(io.BytesIO(b'not a mask'),'bad.bmsk')})
        self.assertEqual(invalid.status_code,400)

    def test_native_block_parser_keeps_all_child_classes(self):
        config=load_project(self.project)
        template=config.resolve(config.data['aircraft'][0]['native_template']).read_text(encoding='utf-8')
        children=block(template,'SubObjects')[2]
        self.assertIn('Class Receiver',children)
        self.assertIn('Class Sensor',children)
        self.assertIn('Class Transmitter',children)
        self.assertTrue(children.rstrip().endswith('END SubObjects'))

    def test_import_preserves_mount_quaternion_and_mask_without_editing_source(self):
        config=load_project(self.project)
        folder=self.project/'source-scene'
        folder.mkdir()
        plane,sensor=config.data['aircraft'][0],config.data['sensors'][0]
        for key,name in (("native_template","AC1.ac"),("graphics_template","AC1.ac3"),("model_file","airliner.mdl")):
            shutil.copyfile(config.resolve(plane[key]),folder/name)
        for key,name in (("native_template","RoofAntennaMask.sn"),("graphics_template","RoofAntennaMask.sn3"),("mask_file","RoofAntennaMask.bmsk")):
            shutil.copyfile(config.resolve(sensor[key]),folder/name)
        graphic=folder/'AC1.ac3'
        graphic.write_text(graphic.read_text().replace('Air\\airliner.mdl','airliner.mdl'))
        scene=folder/'source.sc'
        scene.write_text('stk.v.12.0\nBEGIN Scenario\nClass Aircraft\nAC1\nEND Class\nEND Scenario\n')
        before={p.name:p.read_bytes() for p in folder.iterdir()}
        planes,sensors=import_scene(scene,self.project)
        self.assertEqual(planes[0]['visibility_sensor_id'],'RoofAntennaMask')
        self.assertAlmostEqual(sensors[0]['z_m'],-1.37)
        self.assertEqual(sensors[0]['qy'],1)
        self.assertTrue(sensors[0]['use_mask'])
        self.assertEqual({p.name:p.read_bytes() for p in folder.iterdir()},before)
