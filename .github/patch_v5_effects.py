from pathlib import Path
import re
path=Path('sv-website-5.html')
s=path.read_text(encoding='utf-8')
if 'function startEffectSafetyGuard' not in s:
    marker='  function clearInjectedCustomEffects(){'
    helper=r'''

  // ============================================================
  // CUSTOM EFFECTS SAFETY GUARD
  // Third-party effects may animate their target, but they must never
  // replace, delete, or mutate unrelated page structure. Header/Footer and
  // authored layout properties are snapshotted before an effect executes and
  // restored if the effect touches them.
  // ============================================================
  var effectSafetyGuard = {active:false,observer:null,header:null,footer:null,main:null,nodes:[]};
  var EFFECT_PROTECTED_STYLE_PROPS = ['borderRadius','borderTopLeftRadius','borderTopRightRadius','borderBottomLeftRadius','borderBottomRightRadius','overflow','overflowX','overflowY','boxSizing','padding','paddingTop','paddingRight','paddingBottom','paddingLeft','margin','marginTop','marginRight','marginBottom','marginLeft'];
  function snapshotEffectSafetyNode(el){if(!el||!el.style)return null;var style={};EFFECT_PROTECTED_STYLE_PROPS.forEach(function(name){style[name]=el.style[name];});return {el:el,className:el.getAttribute('class'),id:el.getAttribute('id'),style:style};}
  function captureEffectSafetyBaseline(){stopEffectSafetyGuard();effectSafetyGuard.header=document.querySelector('header.site-header')||document.getElementById('navbar');effectSafetyGuard.footer=document.querySelector('footer.site-footer')||document.querySelector('footer');effectSafetyGuard.main=document.getElementById('main');effectSafetyGuard.nodes=[];[effectSafetyGuard.header,effectSafetyGuard.main,effectSafetyGuard.footer].forEach(function(root){if(!root)return;var nodes=[root].concat(Array.prototype.slice.call(root.querySelectorAll('*')));nodes.forEach(function(el){var snap=snapshotEffectSafetyNode(el);if(snap)effectSafetyGuard.nodes.push(snap);});});}
  function restoreEffectSafetyNode(snap){if(!snap||!snap.el)return;var el=snap.el;if(!document.documentElement.contains(el)){if(el===effectSafetyGuard.header&&document.body){var main=document.getElementById('main');if(main&&main.parentNode)main.parentNode.insertBefore(el,main);else document.body.insertBefore(el,document.body.firstChild);}else if(el===effectSafetyGuard.footer&&document.body)document.body.appendChild(el);else if(el===effectSafetyGuard.main&&document.body){var footer=document.querySelector('footer.site-footer')||document.querySelector('footer');if(footer&&footer.parentNode===document.body)document.body.insertBefore(el,footer);else document.body.appendChild(el);}}if(!document.documentElement.contains(el))return;if(snap.className===null)el.removeAttribute('class');else if(el.getAttribute('class')!==snap.className)el.setAttribute('class',snap.className);if(snap.id&&el.id!==snap.id)el.id=snap.id;EFFECT_PROTECTED_STYLE_PROPS.forEach(function(name){if(el.style[name]!==snap.style[name])el.style[name]=snap.style[name];});}
  function restoreEffectSafetyBaseline(){if(!effectSafetyGuard.active)return;effectSafetyGuard.nodes.forEach(restoreEffectSafetyNode);if(effectSafetyGuard.header&&document.body&&!document.documentElement.contains(effectSafetyGuard.header)){var main=document.getElementById('main');if(main&&main.parentNode)main.parentNode.insertBefore(effectSafetyGuard.header,main);else document.body.insertBefore(effectSafetyGuard.header,document.body.firstChild);}if(effectSafetyGuard.footer&&document.body&&!document.documentElement.contains(effectSafetyGuard.footer))document.body.appendChild(effectSafetyGuard.footer);}
  function startEffectSafetyGuard(){captureEffectSafetyBaseline();effectSafetyGuard.active=true;if(document.body){effectSafetyGuard.observer=new MutationObserver(function(){restoreEffectSafetyBaseline();});effectSafetyGuard.observer.observe(document.body,{subtree:true,childList:true,attributes:true,attributeFilter:['class','style','id']});}}
  function stopEffectSafetyGuard(){if(effectSafetyGuard.observer){try{effectSafetyGuard.observer.disconnect();}catch(e){}}effectSafetyGuard.observer=null;effectSafetyGuard.active=false;effectSafetyGuard.nodes=[];}
'''
    s=s.replace(marker,helper+'\n'+marker,1)
pat=re.compile(r'''  function injectCustomEffects\(effects\)\{.*?\n  \}\n\n  function persistCustomEffectsState''',re.S)
new=r'''  function injectCustomEffects(effects){
    startEffectSafetyGuard();
    clearInjectedCustomEffects();
    (effects||[]).forEach(function(effect,index){
      var code=String(effect&&effect.code!=null?effect.code:"");
      if(!code.trim())return;
      var container=document.createElement("div");
      container.id="ez-custom-effect-"+(index+1);
      container.setAttribute("data-ez-custom-effect",String(index+1));
      container.setAttribute("data-ez-effect-owner","v5");
      container.style.display="contents";
      container.innerHTML=code;
      $all("script",container).forEach(function(old){var script=document.createElement("script");Array.prototype.forEach.call(old.attributes,function(a){script.setAttribute(a.name,a.value);});script.textContent=old.textContent;old.parentNode.replaceChild(script,old);});
      document.body.appendChild(container);
      customCodeContainers.push(container);
    });
    setTimeout(function(){restoreEffectSafetyBaseline();},0);
  }

  function persistCustomEffectsState'''
s,count=pat.subn(new,s,count=1)
if count!=1: raise SystemExit('inject function not found')
old='''  function resetElementsToDefault(){\n    var main = document.getElementById("main");\n    if(!main || !ezPreEffectState) return;'''
newreset='''  function resetElementsToDefault(){\n    stopEffectSafetyGuard();\n    var main = document.getElementById("main");\n    if(!main || !ezPreEffectState) return;'''
if old not in s: raise SystemExit('reset marker not found')
s=s.replace(old,newreset,1)
path.write_text(s,encoding='utf-8')
print('patched V5 effects safety')
