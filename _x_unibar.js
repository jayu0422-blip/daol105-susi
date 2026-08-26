function medOf(rows){
  var v=[],i;
  for(i=0;i<rows.length;i++){var c=cutOf(rows[i]);if(c!=null)v.push(c)}
  if(!v.length)return null;
  v.sort(function(a,b){return a-b});
  return v[Math.floor(v.length/2)];
}

function uniBar(data,g){
  var gy=data.filter(function(r){return r[5]==='학생부교과'&&cutOf(r)!=null});
  var seoul=gy.filter(function(r){return r[1]==='서울'});
  var gg=gy.filter(function(r){return r[1]==='경기'||r[1]==='인천'});
  var lo=gy.filter(function(r){return r[1]!=='서울'&&r[1]!=='경기'&&r[1]!=='인천'});
  var gc=gy.filter(function(r){return r[0].indexOf('가천')>=0});
  var L=[
    {g:medOf(seoul), n:seoul.length, t:'서울 소재',      s:'서울에 있는 대학 교과 전형', c:'#2563EB'},
    {g:medOf(gc),    n:gc.length,    t:'가천대 등 경기 주요대', s:'가천대 교과 전형', c:'#7C3AED'},
    {g:medOf(gg),    n:gg.length,    t:'경기·인천 전체', s:'경기·인천 교과 전형', c:'#0891B2'},
    {g:medOf(lo),    n:lo.length,    t:'비수도권',       s:'서울·경기·인천 밖 교과 전형', c:'#D97706'}
  ].filter(function(x){return x.g!=null});
  if(!L.length)return '';
  var X=function(v){return Math.max(0,Math.min(100,(v-1)/4*100))};
  var NM=['1등급대','2등급대','3등급대','4등급대','5등급대'];
  var seg='',i;
  for(i=0;i<5;i++)seg+='<i class="s'+(i+1)+'"><span>'+NM[i]+'</span></i>';
  var tick='';
  for(i=0;i<L.length;i++)tick+='<u style="left:'+X(L[i].g).toFixed(1)+'%;border-bottom-color:'+L[i].c+'"></u>';
  var me='<b class="me" style="left:'+X(g).toFixed(1)+'%">'+
         '<span>나 '+g.toFixed(2)+'</span></b>';
  var leg='';
  for(i=0;i<L.length;i++){
    leg+='<div class="lg"><em style="background:'+L[i].c+'"></em>'+
      '<b>'+L[i].g.toFixed(2)+'</b><span>'+L[i].t+
      '<i>'+L[i].s+' '+L[i].n.toLocaleString()+'개의 절반이 이보다 낮은 컷</i></span></div>';
  }
  /* 내 위치가 어느 구간인지 한 줄로 */
  var above=[],below=[];
  for(i=0;i<L.length;i++)(g<=L[i].g?above:below).push(L[i].t);
  var msg = above.length
    ? '지금 <b>'+g.toFixed(2)+'</b>은 <b>'+above.join(' · ')+'</b> 중앙값보다 위쪽입니다.'
    : '지금 <b>'+g.toFixed(2)+'</b>은 표시된 모든 기준선보다 아래쪽입니다.';
  return '<div class="uni"><div class="uni-h">교과 전형 기준 · 내 등급은 어디쯤인가</div>'+
    '<div class="uni-w">'+me+'<div class="uni-bar">'+seg+'</div>'+
    '<div class="uni-tk">'+tick+'</div>'+
    '<div class="uni-ax"><span>1.00</span><span>3.00</span><span>5.00</span></div></div>'+
    '<div class="uni-msg">'+msg+'</div>'+leg+
    '<div class="uni-n">권역이 서로 겹칩니다. 서울에도 컷 2.0~2.7인 곳이 있고 비수도권에도 1.7 아래가 있습니다. '+
    '<b>합격선이 아니라 지난 3개년 컷의 중앙값</b>이며, 학생부종합은 등급만으로 판단할 수 없습니다.</div></div>';
}