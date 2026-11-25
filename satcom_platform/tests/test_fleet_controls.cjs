const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const handlers = {};
const node = {style:{},classList:{add(){},remove(){},toggle(){}},addEventListener(){}};
const context = vm.createContext({document:{querySelector:()=>node,addEventListener:(name,fn)=>(handlers[name]??=[]).push(fn)},window:{addEventListener(){}},structuredClone,setTimeout:()=>0,clearTimeout(){},fetch:()=>new Promise(()=>{})});
const assets=path.join(__dirname,'../src/satcom_platform/web_assets');
for(const file of ['app.js','fleet.js'])vm.runInContext(fs.readFileSync(path.join(assets,file),'utf8'),context);
vm.runInContext(`state.snapshot={root:'test',mask_files:['assets/roof.bmsk']};state.tables={track:{rows:[{aircraft_id:'AC1'}]}};state.draft={aircraft:[{aircraft_id:'AC1',model_scale:1,visibility_sensor_id:'Roof'}],sensors:[{aircraft_id:'AC1',sensor_id:'Roof',enabled:true,use_mask:true,mask_file:'assets/roof.bmsk',z_m:-1.37,half_angle_deg:90}],links:[]};render=()=>{};`,context);
const html=vm.runInContext('fleet()',context);
for(const text of ['批量复制飞机','传感器与遮挡','assets/roof.bmsk','value="-1.37"','data-fleet-key="use_mask"'])assert.ok(html.includes(text),text);
for(const checked of [false,true]){
  for(const fn of handlers.change)fn({target:{dataset:{fleetKind:'sensors',fleetRow:'0',fleetKey:'use_mask'},type:'checkbox',checked}});
  assert.equal(vm.runInContext('state.draft.sensors[0].use_mask',context),checked);
}
for(const fn of handlers.input)fn({target:{dataset:{fleetKind:'sensors',fleetRow:'0',fleetKey:'z_m'},type:'number',value:'-2.5'}});
assert.equal(vm.runInContext('state.draft.sensors[0].z_m',context),-2.5);
vm.runInContext(`api=async(url,payload)=>{globalThis.saved={url,payload};return {}};useSnapshot=()=>{};toast=()=>{}`,context);
(async()=>{
  await vm.runInContext('save()',context);
  assert.equal(context.saved.url,'/api/save');
  assert.equal(context.saved.payload.scenario.sensors[0].use_mask,true);
  assert.equal(context.saved.payload.scenario.sensors[0].z_m,-2.5);
  const copy=vm.runInContext("fleetNewSensor('AC1',state.draft.sensors[0])",context);
  assert.equal(copy.sensor_id,'Roof_2');
  assert.equal(copy.mask_file,'assets/roof.bmsk');
  const index=fs.readFileSync(path.join(assets,'index.html'),'utf8');
  assert.ok(index.indexOf('src="/assets/app.js"')<index.indexOf('src="/assets/fleet.js"'));
  console.log('Fleet controls: rendering, mask toggles, mount edits, save and sensor copy verified');
})().catch(error=>{console.error(error);process.exitCode=1});
