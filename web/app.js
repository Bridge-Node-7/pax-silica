(()=>{"use strict";
const $=(s,p=document)=>p.querySelector(s),$$=(s,p=document)=>[...p.querySelectorAll(s)];
const layers=[
["Critical Materials","Physical inputs used across semiconductors, electronics, magnets, energy systems, sensing, and advanced manufacturing.","Origin alone is insufficient. Capacity, quality, ownership, processing dependency, substitution, and application specifications remain material."],
["Processing & Manufacturing","Transforms feedstocks into engineered materials, chemicals, substrates, components, and industrial output.","A diversified source base can still share one processor, precursor, toolchain, energy source, or process dependency."],
["Semiconductors","Connects materials, fabrication, packaging, test, electronics, and the compute stack.","Fab geography does not establish independence from vulnerable gases, chemicals, equipment, packaging, firmware, or test capacity."],
["Energy & Infrastructure","Power, water, logistics, communications, ports, and physical infrastructure convert nominal capacity into usable capacity.","Industrial resilience depends on throughput, permits, transmission, continuity, utilities, and physical chokepoints."],
["Compute & Networks","Chips, storage, networking, data centers, cooling, connectivity, and trusted systems create accessible computing capacity.","Installed hardware is not equivalent to dependable compute without power, cooling, networks, security, utilization, and continuity."],
["AI & Software","Models, software, data, deployment systems, and services convert compute into economic and strategic applications.","Model access remains bounded by data, integration, evaluation, reliability, security, governance, skills, and application fitness."],
["Critical Systems","Defense, sensing, communications, space, energy, healthcare, transport, and other end uses create mission pull.","Upstream availability does not establish successful insertion, certification, reliability, procurement acceptance, or system performance."]
];
$$("[data-layer]").forEach((b,i)=>b.addEventListener("click",()=>{$$("[data-layer]").forEach(x=>x.setAttribute("aria-pressed","false"));b.setAttribute("aria-pressed","true");$("#layerTitle").textContent=layers[i][0];$("#layerFunction").textContent=layers[i][1];$("#layerEvidence").textContent=layers[i][2]}));
$$(".filters [data-region]").forEach(b=>b.addEventListener("click",()=>{$$(".filters [data-region]").forEach(x=>x.setAttribute("aria-pressed","false"));b.setAttribute("aria-pressed","true");const r=b.dataset.region;$$(".member").forEach(m=>m.hidden=!(r==="All"||m.dataset.region===r))}));
const sliders=$$(".control input"),labels=["Detect","Decide","Contract","Tooling","Qualify","Regulatory","Logistics","Ramp"],baseline=[3,5,14,30,75,20,10,45];
const prequalified=[1,3,7,12,25,18,8,35];let ttsMode="BASELINE";
function same(a,b){return a.every((v,i)=>v===b[i])}
function tts(){const v=sliders.map(s=>+s.value);v.forEach((n,i)=>$("#out"+i).textContent=n+"d");$("#ttsTotal").textContent=v.reduce((a,b)=>a+b,0);if(same(v,baseline))ttsMode="BASELINE";else if(same(v,prequalified))ttsMode="PREQUALIFIED";else ttsMode="MODIFIED";$("#ttsModelState").textContent=ttsMode;const mx=Math.max(...v),i=v.indexOf(mx);$("#largestDelay").textContent=labels[i].toUpperCase();$("#delayNote").textContent=(i===4?"Application qualification dominates the modeled state.":labels[i]+" dominates the modeled state.")}
sliders.forEach(s=>s.addEventListener("input",tts));$("#prequalify").addEventListener("click",()=>{prequalified.forEach((v,i)=>sliders[i].value=v);tts()});$("#resetTTS").addEventListener("click",()=>{baseline.forEach((v,i)=>sliders[i].value=v);tts()});tts();
const drawer=$("#drawer"),back=$("#backdrop"),close=$("#drawerClose");let prior=null;
const inertTargets=[$(".site-nav"),$("#main"),$(".bn7"),$(".footer")].filter(Boolean);
function setModalState(on){
  inertTargets.forEach(el=>{if(on)el.setAttribute("inert","");else el.removeAttribute("inert")});
  document.body.classList.toggle("drawer-open",on);
}
function drawerFocusables(){
  return $$('button:not([disabled]),a[href],input:not([disabled]),select:not([disabled]),textarea:not([disabled]),[tabindex]:not([tabindex="-1"])',drawer)
    .filter(el=>el.offsetParent!==null);
}
function openSource(id){
  const card=$("#source-"+id);if(!card)return;
  prior=document.activeElement;
  const title=$("h3",card),state=$(".state",card),dates=$(".evidence-dates",card),supports=$(".evidence-supports",card),note=$(".evidence-note",card),link=$("a",card);
  $("#drawerId").textContent=id;
  $("#drawerTitle").textContent=title?title.textContent:"Evidence source";
  $("#drawerState").textContent=state?state.textContent:"";
  $("#drawerDates").textContent=dates?dates.innerText.replace(/\n+/g," · "):"";
  $("#drawerSupports").textContent=supports?supports.textContent.replace(/^Supports:\s*/,""):"";
  $("#drawerNote").textContent=note?note.textContent:"";
  $("#drawerLink").href=link?link.href:"#";
  back.hidden=false;
  drawer.classList.add("open");
  drawer.setAttribute("aria-hidden","false");
  setModalState(true);
  close.focus();
}
function shut(){
  drawer.classList.remove("open");
  drawer.setAttribute("aria-hidden","true");
  back.hidden=true;
  setModalState(false);
  if(prior&&document.contains(prior))prior.focus();
}
$$(`[data-source]`).forEach(b=>b.addEventListener("click",()=>openSource(b.dataset.source)));
close.addEventListener("click",shut);
back.addEventListener("click",shut);
document.addEventListener("keydown",e=>{
  if(!drawer.classList.contains("open"))return;
  if(e.key==="Escape"){e.preventDefault();shut();return}
  if(e.key!=="Tab")return;
  const f=drawerFocusables();
  if(!f.length){e.preventDefault();close.focus();return}
  const first=f[0],last=f[f.length-1],active=document.activeElement;
  if(e.shiftKey&&active===first){e.preventDefault();last.focus()}
  else if(!e.shiftKey&&active===last){e.preventDefault();first.focus()}
});
const links=$$(".local a"),sections=$$(".section");if("IntersectionObserver"in window){const io=new IntersectionObserver(es=>{const e=es.filter(x=>x.isIntersecting).sort((a,b)=>b.intersectionRatio-a.intersectionRatio)[0];if(!e)return;links.forEach(a=>a.setAttribute("aria-current",String(a.hash==="#"+e.target.id)));const c=links.find(a=>a.getAttribute("aria-current")==="true");if(c)c.scrollIntoView({block:"nearest",inline:"nearest"})},{rootMargin:"-20% 0px -68% 0px",threshold:[0,.2,.5]});sections.forEach(s=>io.observe(s))}
})();
