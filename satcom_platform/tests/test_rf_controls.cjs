// Check the real frontend handlers and save payload without browser dependencies.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const handlers = {};
const node = {style:{},classList:{add(){},remove(){},toggle(){}},addEventListener(){}};
const context = vm.createContext({
  document: {querySelector:()=>node,addEventListener:(name,handler)=>{(handlers[name]??=[]).push(handler)}},
  window: {addEventListener(){}}, structuredClone, setTimeout:()=>0, clearTimeout(){},
  fetch: ()=>new Promise(()=>{}),
});
vm.runInContext(fs.readFileSync(path.join(__dirname,'../src/satcom_platform/web_assets/app.js'),'utf8'),context);
vm.runInContext("state.draft={propagation:{}};state.tables={};state.snapshot=null",context);
const models = [
  ['rain_model','ITU_R_P618'], ['atmosphere_model','ITU_R_P676'],
  ['cloud_fog_model','ITU_R_P840'], ['tropo_scintillation_model','ITU_R_P618'],
];
for(const [key,model] of models){
  const event={target:{dataset:{rfModel:key,rfValue:model},checked:true}};
  for(const handler of handlers.change)handler(event);
  assert.equal(vm.runInContext(`state.draft.propagation.${key}`,context),model);
}
assert.equal(vm.runInContext('state.dirty',context),true);
const html=vm.runInContext('rfEnvironment()',context);
assert.equal((html.match(/role="switch"/g)||[]).length,4);
assert.equal((html.match(/checked/g)||[]).length,4);
const progressHtml=vm.runInContext("runProgress({state:'RUNNING',progress:{percent:63,label:'计算链路预算',completed:20,total:100,detail:'U1 → SAT2'}})",context);
assert.ok(progressHtml.includes('value="63"'));
assert.ok(progressHtml.includes('计算链路预算'));
assert.ok(progressHtml.includes('20 / 100'));
assert.equal(vm.runInContext('runProgress({})',context),'');
const failureHtml=vm.runInContext("runProgress({state:'FAILED',progress:{percent:63,label:'计算链路预算',completed:20,total:100}})",context);
assert.ok(failureHtml.includes('运行失败'));
for(const handler of handlers.change)handler({target:{dataset:{interferenceModel:'true'},checked:true}});
assert.equal(vm.runInContext('state.draft.propagation.downlink_interference_model',context),'COCHANNEL_AGGREGATE');
assert.equal(vm.runInContext('state.draft.propagation.doppler_compensation',context),'IDEAL');
assert.ok(vm.runInContext('interferenceSettings()',context).includes('checked'));
for(const handler of handlers.change)handler({target:{dataset:{interferenceModel:'true'},checked:false}});
assert.equal(vm.runInContext('state.draft.propagation.downlink_interference_model',context),'NONE');


vm.runInContext('api=async (url,payload)=>{globalThis.saved={url,payload};return {}};useSnapshot=()=>{};toast=()=>{}',context);
(async()=>{
  await vm.runInContext('save()',context);
  assert.equal(context.saved.url,'/api/save');
  for(const [key,model] of models)assert.equal(context.saved.payload.scenario.propagation[key],model);
  for(const [key,model] of models){
    for(const handler of handlers.change)handler({target:{dataset:{rfModel:key,rfValue:model},checked:false}});
    assert.equal(vm.runInContext(`state.draft.propagation.${key}`,context),'NONE');
  }
  assert.equal((vm.runInContext('rfEnvironment()',context).match(/checked/g)||[]).length,0);
  console.log('RF controls: four switches, save payload, and disable verified');
})().catch(error=>{console.error(error);process.exitCode=1});
