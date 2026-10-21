(async function(){
  "use strict";

  // Version 5 embed loader.
  // Resolves the target page relative to this loader's own URL so the pair can
  // be hosted together in any directory without relying on an absolute path.

  var thisScript = document.currentScript;
  if(!thisScript){
    var all = document.querySelectorAll('script[src*="embed-loader-5.js"]');
    thisScript = all[all.length - 1];
  }

  var scriptSrc = (thisScript && thisScript.src) || '';
  var origin = '';
  var scriptBase = '';

  try{
    var scriptUrl = new URL(scriptSrc, window.location.href);
    origin = scriptUrl.origin;
    scriptBase = new URL('.', scriptUrl.href).href;
  }catch(e){}

  var qIndex = scriptSrc.indexOf('?');
  var hIndex = scriptSrc.indexOf('#');
  var queryPart = qIndex > -1 ? scriptSrc.slice(qIndex + 1, hIndex > qIndex ? hIndex : undefined) : '';
  var hashPart = hIndex > -1 ? scriptSrc.slice(hIndex + 1) : '';

  var params = new URLSearchParams(queryPart);
  var hashParams = new URLSearchParams(hashPart);

  // Settings payload is normally carried in the fragment so it is not sent
  // to the hosting server. Both #p= and #data= are supported for compatibility.
  var payload =
    hashParams.get('p') ||
    hashParams.get('data') ||
    params.get('p') ||
    params.get('data') ||
    '';

  // V5 embeds use gzip-compressed payloads (gz: prefix) to keep the script
  // snippet short enough for HTML editors such as Systeme.io.
  if(payload.indexOf('gz:') === 0 && typeof DecompressionStream === 'function'){
    try{
      var compressedBinary = atob(payload.slice(3));
      var compressedBytes = new Uint8Array(compressedBinary.length);
      for(var ci=0;ci<compressedBinary.length;ci++) compressedBytes[ci]=compressedBinary.charCodeAt(ci);
      var decompressedStream = new Blob([compressedBytes]).stream().pipeThrough(new DecompressionStream('gzip'));
      var jsonText = await new Response(decompressedStream).text();
      payload = btoa(unescape(encodeURIComponent(jsonText)));
    }catch(e){
      console.error('embed-loader-5.js: could not decompress the settings payload.', e);
      payload = '';
    }
  }

  // Resolve the target page from explicit page/file configuration first.
  var fileName =
    params.get('file') ||
    hashParams.get('file') ||
    (thisScript && thisScript.getAttribute('data-file')) ||
    '';

  var dataPage = (thisScript && thisScript.getAttribute('data-page')) || '';
  var explicitPage = params.get('page') || hashParams.get('page') || '';

  var pageUrl =
    explicitPage ||
    (/^https?:\/\//i.test(dataPage) ? dataPage : '') ||
    (fileName ? new URL(fileName.replace(/^\/+/, ''), scriptBase || origin + '/').href : '') ||
    (dataPage ? new URL(dataPage.replace(/^\/+/, ''), scriptBase || origin + '/').href : '') ||
    (scriptBase ? new URL('sv-website-5.html', scriptBase).href : '');

  if(!pageUrl){
    console.error('embed-loader-5.js: could not resolve the page URL.');
    return;
  }

  // Embedded/live pages should never expose the editor UI. Version 5 already
  // supports live=1 in the URL and applies its .ez-view-only rules accordingly.
  var livePageUrl = pageUrl;
  try{
    var resolvedPageUrl = new URL(pageUrl, window.location.href);
    resolvedPageUrl.hash = payload
      ? 'data=' + encodeURIComponent(payload) + '&live=1'
      : 'live=1';
    livePageUrl = resolvedPageUrl.href;
  }catch(e){
    if(payload && livePageUrl.indexOf('#') === -1 && livePageUrl.indexOf('data=') === -1){
      livePageUrl += '#data=' + encodeURIComponent(payload) + '&live=1';
    }else if(!payload && livePageUrl.indexOf('#') === -1){
      livePageUrl += '#live=1';
    }
  }

  var iframe = document.createElement('iframe');
  iframe.src = livePageUrl;
  iframe.style.width = '100%';
  iframe.style.border = '0';
  iframe.style.display = 'block';
  iframe.style.height = '100vh';
  iframe.setAttribute('allow', 'clipboard-write');
  iframe.setAttribute('title', 'FRAME');

  // Insert next to this loader when possible; otherwise wait for body.
  if(thisScript && thisScript.parentNode){
    thisScript.parentNode.insertBefore(iframe, thisScript);
  }else if(document.body){
    document.body.appendChild(iframe);
  }else{
    document.addEventListener('DOMContentLoaded', function(){
      document.body.appendChild(iframe);
    });
  }
})();