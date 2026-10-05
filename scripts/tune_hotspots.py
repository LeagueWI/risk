from pathlib import Path
import re

p = Path('index.html')
s = p.read_text()

s = re.sub(r'spot-risk-build" content="[^"]+"', 'spot-risk-build" content="2026-10-05-final-hotspots-v10"', s)

replacements = {
    'anchors:[{x:25.0,y:82.0,r:7.5},{x:34.0,y:82.0,r:7.5},{x:45.0,y:80.0,r:7.5},{x:56.0,y:77.5,r:7.5},{x:65.0,y:75.0,r:7.0}]':
    'anchors:[{x:20.0,y:82.0,r:7.5},{x:27.0,y:82.0,r:7.5},{x:34.0,y:82.0,r:7.5},{x:45.0,y:80.0,r:7.5},{x:56.0,y:77.5,r:7.5},{x:65.0,y:75.0,r:7.0},{x:72.0,y:74.0,r:7.0}]',
    'anchors:[{x:31.0,y:85.0,r:8.0},{x:37.0,y:87.0,r:8.5},{x:43.0,y:88.0,r:8.0}]':
    'anchors:[{x:27.0,y:85.0,r:8.0},{x:33.0,y:86.5,r:8.5},{x:39.0,y:87.5,r:8.5},{x:45.0,y:88.0,r:8.0},{x:49.0,y:87.0,r:7.5}]',
    'anchors:[{x:47.0,y:91.0,r:7.5},{x:55.0,y:93.0,r:7.5},{x:63.0,y:92.0,r:7.5},{x:69.0,y:88.0,r:7.0}]':
    'anchors:[{x:43.0,y:90.0,r:7.5},{x:49.0,y:92.0,r:7.5},{x:55.0,y:93.0,r:7.5},{x:61.0,y:93.0,r:7.5},{x:67.0,y:90.0,r:7.5},{x:71.0,y:87.0,r:7.0}]',
    'anchors:[{x:8.0,y:78.0,r:8.0},{x:12.0,y:83.0,r:8.5},{x:17.0,y:87.0,r:8.5}]':
    'anchors:[{x:6.0,y:77.0,r:8.0},{x:10.0,y:81.0,r:8.5},{x:14.0,y:85.0,r:8.5},{x:18.0,y:88.0,r:8.5},{x:22.0,y:89.0,r:8.0}]',
    'anchors:[{x:78.0,y:58.0,r:8.0},{x:84.0,y:62.0,r:8.5},{x:89.0,y:66.0,r:8.5}]':
    'anchors:[{x:75.0,y:54.0,r:8.0},{x:80.0,y:58.0,r:8.5},{x:85.0,y:62.0,r:8.5},{x:90.0,y:66.0,r:8.5},{x:94.0,y:69.0,r:8.0}]',
}
for old, new in replacements.items():
    if old not in s:
        raise SystemExit('Expected anchor pattern not found: ' + old[:80])
    s = s.replace(old, new)

old_block = '''layer.onclick=function(e){
   if(!current)return;
   var rect=layer.getBoundingClientRect();
   var tapX=e.clientX-rect.left;
   var tapY=e.clientY-rect.top;
   var candidates=[];
   scenes[current].risks
     .filter(function(r){return !found.has(r.id)})
     .forEach(function(r){
       riskAnchors(r).forEach(function(a){
         var targetX=(a.x/100)*rect.width;
         var targetY=(a.y/100)*rect.height;
         var dx=tapX-targetX;
         var dy=tapY-targetY;
         var d=Math.sqrt(dx*dx+dy*dy);
         var proportional=((a.r||5)/100)*rect.width;
         var hitRadius=Math.max(74,proportional*1.75);
         if(d<=hitRadius)candidates.push({risk:r,anchor:a,d:d});
       });
     });
   candidates.sort(function(a,b){return a.d-b.d});
   if(candidates.length)hit(candidates[0].risk.id,candidates[0].anchor);
 };'''

new_block = '''layer.onpointerup=function(e){
   if(!current)return;
   var rect=layer.getBoundingClientRect();
   var tapX=e.clientX-rect.left;
   var tapY=e.clientY-rect.top;
   var coarse=!!(window.matchMedia&&window.matchMedia("(pointer: coarse)").matches);
   var primaryMin=coarse?94:82;
   var assistMin=coarse?132:112;

   var ranked=scenes[current].risks
     .filter(function(r){return !found.has(r.id)})
     .map(function(r){
       var best=null;
       riskAnchors(r).forEach(function(a){
         var targetX=(a.x/100)*rect.width;
         var targetY=(a.y/100)*rect.height;
         var dx=tapX-targetX;
         var dy=tapY-targetY;
         var d=Math.sqrt(dx*dx+dy*dy);
         var proportional=((a.r||5)/100)*rect.width;
         var primary=Math.max(primaryMin,proportional*1.95);
         var assist=Math.max(assistMin,proportional*2.45);
         if(!best||d<best.d)best={risk:r,anchor:a,d:d,primary:primary,assist:assist};
       });
       return best;
     })
     .filter(Boolean)
     .sort(function(a,b){return a.d-b.d});

   if(!ranked.length)return;
   var first=ranked[0];
   var second=ranked[1];

   if(first.d<=first.primary){
     hit(first.risk.id,first.anchor);
     return;
   }

   var clearWinner=!second || first.d+28<second.d || first.d<=second.d*0.72;
   if(first.d<=first.assist&&clearWinner){
     hit(first.risk.id,first.anchor);
   }
 };'''

if old_block not in s:
    raise SystemExit('Existing hotspot handler was not found exactly')
s = s.replace(old_block, new_block)
s = s.replace('touch-action:manipulation}', 'touch-action:manipulation;-webkit-tap-highlight-color:transparent;user-select:none}')

p.write_text(s)

assert '2026-10-05-final-hotspots-v10' in s
assert 'primaryMin=coarse?94:82' in s
assert 'assistMin=coarse?132:112' in s
assert 'clearWinner' in s

# Touch this file to trigger the tuning workflow after the workflow itself was simplified.
