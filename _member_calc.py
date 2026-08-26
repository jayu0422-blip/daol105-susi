# -*- coding: utf-8 -*-
"""재원생판 내신 계산기 — 2015 개정 교육과정(현 고3 · 9등급제) 과목별 입력.

  두 갈래로 나눈다.
    ① 평균 등급을 이미 아는 학생  → 기존 한 칸 입력 그대로
    ② 평균 등급을 모르는 학생     → 고1·고2·고3(1학기) 과목별로 넣으면 계산

  계산식 : Σ(석차등급 × 이수단위) / Σ(이수단위)
  제외   : 진로선택 · 체육 · 예술 · 과학탐구실험 (석차등급이 산출되지 않는 과목)
  ★ hs12(고1·2)는 2022 개정 5등급제라 과목 체계가 다르다. 이 파일은 고3 전용.
"""

# ── 2015 개정 보통교과 ────────────────────────────────────────
#   공통 : (과목명, 학기당 기본 단위)      · 기준단위를 2학기로 나눈 값
#   일반 : (과목명, 학기 단위)             · 석차등급 산출 O
#   진로 : 과목명만                        · 석차등급 산출 X → 고를 수 없게 막되 목록엔 보여준다
CUR = {
    "국어": {
        "공통": [("국어", 4)],
        "일반": [("화법과 작문", 4), ("독서", 4), ("언어와 매체", 4), ("문학", 4)],
        "진로": ["실용 국어", "심화 국어", "고전 읽기"],
    },
    "수학": {
        "공통": [("수학", 4)],
        "일반": [("수학Ⅰ", 4), ("수학Ⅱ", 4), ("미적분", 4), ("확률과 통계", 4)],
        "진로": ["기본 수학", "실용 수학", "인공지능 수학", "기하", "경제 수학", "수학과제 탐구"],
    },
    "영어": {
        "공통": [("영어", 4)],
        "일반": [("영어 회화", 4), ("영어Ⅰ", 4), ("영어 독해와 작문", 4), ("영어Ⅱ", 4)],
        "진로": ["기본 영어", "실용 영어", "영어권 문화", "진로 영어", "영미 문학 읽기"],
    },
    "사회": {
        "공통": [("통합사회", 4), ("한국사", 3)],
        "일반": [("한국지리", 4), ("세계지리", 4), ("세계사", 4), ("동아시아사", 4), ("경제", 4),
                 ("정치와 법", 4), ("사회·문화", 4), ("생활과 윤리", 4), ("윤리와 사상", 4)],
        "진로": ["여행지리", "사회문제 탐구", "고전과 윤리"],
    },
    "과학": {
        "공통": [("통합과학", 4)],
        "일반": [("물리학Ⅰ", 4), ("화학Ⅰ", 4), ("생명과학Ⅰ", 4), ("지구과학Ⅰ", 4)],
        "진로": ["물리학Ⅱ", "화학Ⅱ", "생명과학Ⅱ", "지구과학Ⅱ", "과학사", "생활과 과학", "융합과학"],
    },
}

# 대학이 대개 반영하지 않지만 학생부에는 석차등급이 찍히는 교과 (전 과목 평균에만 들어간다)
ETC = [("기술·가정", 4), ("제2외국어", 4), ("한문", 4), ("그 밖의 과목", 4)]

# 고1 공통 6과목 — 화면에 고정으로 깔아 둔다
COMMON1 = [("국어", "국어", 4), ("수학", "수학", 4), ("영어", "영어", 4),
           ("사회", "한국사", 3), ("사회", "통합사회", 4), ("과학", "통합과학", 4)]


def _js_data():
    import json
    return ("var CUR=" + json.dumps(CUR, ensure_ascii=False) + ";\n"
            "var ETC=" + json.dumps(ETC, ensure_ascii=False) + ";\n"
            "var COMMON1=" + json.dumps(COMMON1, ensure_ascii=False) + ";\n")


# ── 화면 ──────────────────────────────────────────────────────
CALC_HTML = """
      <div class="gmode" role="tablist">
        <button type="button" class="gm on" data-gm="know" role="tab" aria-selected="true">평균 등급을 알아요</button>
        <button type="button" class="gm" data-gm="calc" role="tab" aria-selected="false">과목 넣고 계산할게요</button>
      </div>
      <div id="calcBox" class="calcbox" hidden>
        <div class="cb-h">📗 내신 평균 등급 계산 <span>고1 · 고2 · 고3 1학기 과목을 넣으면 <b>단위 수까지 반영</b>해 계산합니다 ·
          현 고3은 <b>2015 개정 · 9등급제</b>입니다</span></div>
        <div class="cquick">
          <span>전 과목 한 번에</span>
          <input id="cqv" type="number" step="0.1" min="1" max="9" placeholder="3.0" inputmode="decimal">
          <button type="button" id="cqb">채우기</button>
        </div>
        <div id="cYears"></div>
        <div class="cnote">단위 수는 <b>학교마다 다릅니다.</b> 생활기록부에 찍힌 <b>학점</b>과 다르면 옆 칸을 고쳐 주세요. (보통 공통 4 · 선택 4~6)<br>
          진로선택 · 체육 · 예술 · 과학탐구실험은 <b>석차등급 자체가 안 나와</b> 이 평균에서 빠집니다.
          다만 <b>대학 대부분(약 80%)은 진로선택 성취도 A·B·C를 따로 환산해 반영</b>합니다 —
          환산 방식이 대학마다 달라 여기서는 계산하지 않습니다.<br>
          한국사는 <b>사회 교과</b>로 넣었습니다. 대학에 따라 따로 보거나 아예 빼기도 합니다.</div>
        <div id="cOut" class="cout"></div>
      </div>
"""

# ── 스타일 ────────────────────────────────────────────────────
CALC_CSS = """
/* ══ 내신 계산기 ══ */
.gmode{display:grid;grid-template-columns:1fr 1fr;gap:6px;background:var(--soft);border-radius:12px;padding:4px;margin-bottom:12px}
.gm{font-family:inherit;font-size:13.5px;font-weight:800;color:var(--gray2);background:transparent;border:none;
  border-radius:9px;padding:11px 6px;cursor:pointer;letter-spacing:-.02em;min-height:44px}
.gm.on{background:#fff;color:var(--blue-strong);box-shadow:0 1px 4px rgba(20,30,50,.12)}
.calcbox{background:var(--soft2);border:1px solid var(--line);border-radius:14px;padding:14px 13px;margin:0 0 12px}
.cb-h{font-size:13.5px;font-weight:800;color:var(--ink);margin-bottom:11px}
.cb-h span{display:block;font-size:11.5px;font-weight:600;color:var(--gray2);margin-top:4px;line-height:1.65}
.cb-h b{color:var(--blue-strong)}
.cquick{display:flex;align-items:center;gap:7px;background:#fff;border:1px solid var(--line);border-radius:10px;
  padding:8px 10px;margin-bottom:11px;flex-wrap:wrap}
.cquick span{font-size:12px;font-weight:800;color:var(--gray);flex:0 0 auto}
.cquick input{flex:1 1 60px;min-width:60px;font-family:inherit;font-size:15px;font-weight:800;text-align:center;
  color:var(--ink);background:var(--soft2);border:1px solid var(--line);border-radius:8px;padding:10px 6px;outline:none;min-height:44px}
.cquick button{flex:0 0 auto;font-family:inherit;font-size:12.5px;font-weight:800;color:#fff;background:var(--gray);
  border:none;border-radius:8px;padding:9px 13px;cursor:pointer;min-height:44px}
.cy{background:#fff;border:1px solid var(--line);border-radius:12px;margin-bottom:9px;overflow:hidden}
.cyh{display:flex;align-items:center;gap:8px;width:100%;font-family:inherit;font-size:14px;font-weight:800;
  color:var(--ink);background:#fff;border:none;padding:13px 13px;cursor:pointer;text-align:left;min-height:48px}
.cyh .ar{margin-left:auto;font-size:12px;color:var(--gray2);font-weight:700;transition:transform .15s}
.cy.open .cyh .ar{transform:rotate(180deg)}
.cyh .st{font-size:11.5px;font-weight:700;color:var(--blue-strong);background:var(--blue-soft);
  border-radius:6px;padding:3px 7px;letter-spacing:-.02em}
.cyh .st.none{color:var(--gray2);background:var(--soft)}
.cyb{display:none;padding:0 12px 12px}
.cy.open .cyb{display:block}
.csem{margin-top:10px}
.csem>.h{font-size:12px;font-weight:800;color:var(--gray);padding:5px 0 7px;border-top:1px solid var(--line)}
.cr{display:grid;grid-template-columns:1fr 62px 56px;gap:6px;align-items:center;margin-bottom:6px}
.cr.sel{grid-template-columns:1fr 62px 56px 30px}
.cn{font-size:13px;font-weight:700;color:var(--ink);letter-spacing:-.02em;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.cr select,.cr input{width:100%;font-family:inherit;font-size:14px;font-weight:700;color:var(--ink);
  background:var(--soft2);border:1px solid var(--line);border-radius:9px;padding:10px 6px;outline:none;min-height:42px}
.cr select{font-size:12.5px;padding:10px 4px}
.cr input{text-align:center}
.cr input.cu{font-size:12.5px;font-weight:600;color:var(--gray2);background:#fff}
.cr input:focus,.cr select:focus{border-color:var(--blue);background:#fff}
.cr input.on{background:var(--blue-soft);border-color:var(--blue);color:var(--blue-strong);font-weight:800}
.cr .cx{background:transparent;border:none;color:var(--gray2);font-size:17px;cursor:pointer;padding:0;min-height:42px}
.chd{display:grid;grid-template-columns:1fr 62px 56px;gap:6px;font-size:10.5px;font-weight:800;color:var(--gray2);
  margin-bottom:5px;text-align:center}
.chd i{font-style:normal;text-align:left}
.cr.sel~.chd,.chd.sel{grid-template-columns:1fr 62px 56px 30px}
.cadd{width:100%;font-family:inherit;font-size:12.5px;font-weight:800;color:var(--blue-strong);background:var(--blue-soft2);
  border:1px dashed var(--blue);border-radius:9px;padding:10px;cursor:pointer;margin-top:2px;min-height:40px}
.cetc{margin-top:9px}
.cetc>summary{font-size:12px;font-weight:800;color:var(--gray2);cursor:pointer;padding:7px 0;list-style:none}
.cetc>summary::-webkit-details-marker{display:none}
.cetc>summary:before{content:'▸ ';color:var(--gray2)}
.cetc[open]>summary:before{content:'▾ '}
.cnote{font-size:11px;color:var(--gray2);line-height:1.7;margin:9px 2px 0}
.cnote b{color:var(--gray);font-weight:800}
.cout{margin-top:11px}
.cempty{font-size:12.5px;color:var(--gray2);text-align:center;padding:16px 10px;background:#fff;
  border:1px dashed var(--line);border-radius:11px;line-height:1.7}
.cres{background:#fff;border:1.5px solid var(--blue);border-radius:13px;padding:14px 13px}
.cbig{display:flex;align-items:baseline;gap:9px;flex-wrap:wrap}
.cbig b{font-size:31px;font-weight:800;color:var(--blue-strong);line-height:1;font-variant-numeric:tabular-nums}
.cbig span{font-size:12.5px;font-weight:800;color:var(--gray)}
.cbig em{font-size:11px;font-style:normal;font-weight:700;color:var(--gray2);width:100%;margin-top:5px;line-height:1.6}
.cbig em b{font-size:11px;font-weight:800;color:var(--gray);line-height:1.6}
.csub{margin-top:11px;padding-top:10px;border-top:1px solid var(--line)}
.csub .l{display:flex;align-items:baseline;gap:8px;padding:4px 0;font-size:12.5px}
.csub .l>i{font-style:normal;font-weight:700;color:var(--gray);flex:1;letter-spacing:-.02em}
.csub .l>b{font-weight:800;color:var(--ink);font-variant-numeric:tabular-nums;font-size:14px}
.csub .l.hi>b{color:var(--blue-strong)}
.csub .l u{text-decoration:none;font-size:10.5px;font-weight:700;color:var(--gray2)}
.cuse{width:100%;font-family:inherit;font-size:14.5px;font-weight:800;color:#fff;background:var(--blue);
  border:none;border-radius:11px;padding:13px;cursor:pointer;margin-top:11px;min-height:46px}
.cwarn{font-size:11.5px;color:#A16207;background:#FFF6E5;border-radius:8px;padding:8px 10px;margin-top:9px;line-height:1.65}

/* ══ 시인성 보정 — 전 뷰포트 실측 기준 ══
   --gray2(#8B95A1)는 흰 배경에서 대비 2.9 라 실제로 잘 안 읽힌다. 이 변수를 쓰는 곳이
   페이지 전체에 흩어져 있어 규칙을 하나씩 덮는 대신 변수 자체를 4.9:1 로 올린다. */
:root{--gray2:#667080}
.cuse{background:var(--blue-strong)}     /* 흰 글씨 대비 3.71 → 4.9 */
.more{color:var(--blue-strong)}          /* 3.48 → 4.6 */
.chip.cut{color:#0B4FB8}                 /* 4.33 → 6.3 */
.chip.min{color:#7A5200}                 /* 4.47 → 6.6 */
.endcta a.tel{padding:8px 0;min-height:44px}
.cnote{font-size:11.5px}
.cbig em,.cbig em b{font-size:11.5px}
.csub .l u{font-size:11.5px}

/* 아래는 계산기 자체 */
   --gray2(#8B95A1)는 흰 배경에서 대비 2.9~3.0 이라 실제로 잘 안 읽힌다.
   정보를 담은 글자는 --gray(#4E5968, 7.0)로 올린다. 장식이 아니라 읽어야 할 글자다. */
.gm{color:var(--gray)}                                  /* 비활성 탭 2.76 → 7.0 */
.cb-h span,.cnote,.cempty{color:var(--gray)}
.chd{font-size:11.5px;color:var(--gray)}                /* 10.5px → 11.5px */
.cr input.cu{color:var(--gray)}
.cbig em{color:var(--gray)}
.csub .l u{color:var(--gray)}
.cyh .st{color:#0B4FB8}                                 /* 4.33 → 6.5 */
.cyh .st.none{color:var(--gray)}
/* 수능 예상 등급 4칸 — 360px 에서 폭 21px 까지 눌려 손가락으로 못 눌렀다 */
.mb-g input{min-height:44px}
@media(max-width:440px){
  .mb-g{grid-template-columns:repeat(2,1fr);gap:9px}
}
/* 기존 페이지 쪽 — 같은 이유로 함께 올린다 */
.trust,.hint{color:var(--gray)}
.go{background:var(--blue-strong)}                      /* 흰 글씨 대비 3.71 → 4.9 */
.stick .x{min-width:44px;min-height:44px;font-size:20px}
.stick .msg a.tel,.stick a.tel{display:inline-block;padding:6px 0;min-height:32px}

@media(max-width:380px){
  .cr,.chd{grid-template-columns:1fr 54px 48px}
  .cr.sel,.chd.sel{grid-template-columns:1fr 54px 48px 26px}
  .cn{font-size:12px}
  .gm{font-size:12.5px}
}
"""

# ── 로직 ──────────────────────────────────────────────────────
CALC_JS = r"""
/* ══════════ 내신 평균 등급 계산기 (2015 개정 · 9등급제) ══════════
   Σ(석차등급 × 이수단위) / Σ(이수단위).
   진로선택·체육·예술·과학탐구실험은 석차등급이 없어 계산에서 뺀다.
   대학이 보는 값은 보통 '국·수·영·사·과'라서 그것을 대표값으로 올린다. */
__CALC_DATA__

var CY = [['고1', ['1학기', '2학기'], 'common'],
          ['고2', ['1학기', '2학기'], 'elective'],
          ['고3', ['1학기'], 'elective']];
var CMAIN = ['국어', '수학', '영어', '사회', '과학'];

function cEsc(t){ return String(t).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;'); }

/* 탐구·선택 과목 드롭다운 — 진로선택은 보여주되 고를 수 없게 막는다 */
var _cOpt = null;
function cOptions(){
  if(_cOpt) return _cOpt;
  var o = '<option value="">과목 선택</option>';
  ['국어','수학','영어','사회','과학'].forEach(function(k){
    o += '<option disabled>── ' + k + ' 일반선택 ──</option>';
    CUR[k]['일반'].forEach(function(x){
      o += '<option value="' + cEsc(x[0]) + '" data-grp="' + k + '" data-u="' + x[1] + '">' + cEsc(x[0]) + '</option>';
    });
    o += '<option disabled>── ' + k + ' 진로선택 · 석차등급 없음 ──</option>';
    CUR[k]['진로'].forEach(function(n){
      o += '<option disabled>' + cEsc(n) + ' (등급 미산출)</option>';
    });
  });
  o += '<option disabled>── 그 밖의 교과 ──</option>';
  ETC.forEach(function(x){
    o += '<option value="' + cEsc(x[0]) + '" data-grp="기타" data-u="' + x[1] + '">' + cEsc(x[0]) + '</option>';
  });
  _cOpt = o;
  return o;
}

function cRowFixed(grp, name, u){
  return '<div class="cr" data-grp="' + grp + '"><span class="cn">' + cEsc(name) + '</span>' +
    '<input class="cg" type="number" step="1" min="1" max="9" inputmode="numeric" placeholder="–">' +
    '<input class="cu" type="number" step="1" min="1" max="10" inputmode="numeric" value="' + u + '"></div>';
}
function cRowSel(){
  return '<div class="cr sel"><select class="cs">' + cOptions() + '</select>' +
    '<input class="cg" type="number" step="1" min="1" max="9" inputmode="numeric" placeholder="–">' +
    '<input class="cu" type="number" step="1" min="1" max="10" inputmode="numeric" value="4">' +
    '<button type="button" class="cx" aria-label="이 줄 지우기">&times;</button></div>';
}
function cHead(sel){
  return '<div class="chd' + (sel ? ' sel' : '') + '"><i>과목</i><span>등급</span><span>학점</span>' +
    (sel ? '<span></span>' : '') + '</div>';
}

function cSemHtml(yr, sem, kind){
  var h = '<div class="csem"><div class="h">' + yr + ' ' + sem + '</div>';
  if(kind === 'common'){
    h += cHead(false) + COMMON1.map(function(x){ return cRowFixed(x[0], x[1], x[2]); }).join('');
    h += '<div class="cadd-wrap">' + cHead(true) + cRowSel() +
         '<button type="button" class="cadd">＋ 그 밖에 들은 과목 추가</button></div>';
  }else{
    h += cHead(true);
    for(var i = 0; i < 6; i++) h += cRowSel();
    h += '<button type="button" class="cadd">＋ 과목 추가</button>';
  }
  return h + '</div>';
}

function cBuild(){
  var box = document.getElementById('cYears');
  if(!box) return;
  box.innerHTML = CY.map(function(y, idx){
    return '<div class="cy' + (idx === 0 ? ' open' : '') + '" data-yr="' + y[0] + '">' +
      '<button type="button" class="cyh"><span>' + y[0] + '</span>' +
      '<span class="st none" data-st>미입력</span><span class="ar">▾</span></button>' +
      '<div class="cyb">' + y[1].map(function(s){ return cSemHtml(y[0], s, y[2]); }).join('') + '</div></div>';
  }).join('');
  cWire(box);
  cCalc();
}

function cWire(root){
  root.addEventListener('click', function(e){
    var h = e.target.closest('.cyh');
    if(h){ h.parentNode.classList.toggle('open'); return; }
    var x = e.target.closest('.cx');
    if(x){
      var row = x.closest('.cr'), box = row.parentNode;
      if(box.querySelectorAll('.cr.sel').length <= 1){
        row.querySelector('.cs').value = '';
        row.querySelector('.cg').value = '';
        row.querySelector('.cg').classList.remove('on');
      }else row.remove();
      cCalc(); return;
    }
    var a = e.target.closest('.cadd');
    if(a){ a.insertAdjacentHTML('beforebegin', cRowSel()); cCalc(); return; }
  });
  root.addEventListener('change', function(e){
    var s = e.target.closest('.cs');
    if(s){
      var o = s.options[s.selectedIndex], u = s.parentNode.querySelector('.cu');
      if(o && o.dataset.u) u.value = o.dataset.u;
      var g = s.parentNode.querySelector('.cg');
      if(s.value && !g.value) g.focus();
    }
    cCalc();
  });
  root.addEventListener('input', function(e){
    var g = e.target.closest('.cg');
    if(g){
      var v = parseFloat(g.value);
      g.classList.toggle('on', v >= 1 && v <= 9);
    }
    cCalc();
  });
}

/* 화면에 들어간 값을 모은다 */
function cRows(){
  var out = [];
  document.querySelectorAll('#cYears .cr').forEach(function(r){
    var grp = r.dataset.grp, nm = '';
    var s = r.querySelector('.cs');
    if(s){
      if(!s.value) return;
      var o = s.options[s.selectedIndex];
      grp = o.dataset.grp; nm = s.value;
    }else nm = r.querySelector('.cn').textContent;
    var g = parseFloat(r.querySelector('.cg').value);
    var u = parseFloat(r.querySelector('.cu').value);
    if(!(g >= 1 && g <= 9)) return;
    if(!(u > 0)) return;
    var y = r.closest('.cy');
    out.push({ grp: grp, nm: nm, g: g, u: u, yr: y ? y.dataset.yr : '' });
  });
  return out;
}
function cAvg(rows){
  var s = 0, w = 0;
  for(var i = 0; i < rows.length; i++){ s += rows[i].g * rows[i].u; w += rows[i].u; }
  return w > 0 ? s / w : null;
}
function cPick(rows, grps){
  return rows.filter(function(r){ return grps.indexOf(r.grp) >= 0; });
}
function cFix(v){ return v == null ? '–' : v.toFixed(2); }

function cCalc(){
  var out = document.getElementById('cOut');
  if(!out) return;
  var rows = cRows();

  /* 학년 배지 */
  document.querySelectorAll('#cYears .cy').forEach(function(y){
    var n = rows.filter(function(r){ return r.yr === y.dataset.yr; }).length;
    var st = y.querySelector('[data-st]');
    st.textContent = n ? n + '과목' : '미입력';
    st.classList.toggle('none', !n);
  });

  if(!rows.length){
    out.innerHTML = '<div class="cempty">과목 등급을 넣으면 여기에 <b>평균 등급</b>이 나옵니다.<br>' +
      '위 <b>「전 과목 한 번에」</b>로 대충 채운 뒤 다른 과목만 고쳐도 됩니다.</div>';
    return;
  }

  var main = cPick(rows, CMAIN);
  var vMain = cAvg(main), vAll = cAvg(rows);
  var vIn = cAvg(cPick(rows, ['국어', '수학', '영어', '사회']));
  var vNa = cAvg(cPick(rows, ['국어', '수학', '영어', '과학']));
  var uSum = 0; main.forEach(function(r){ uSum += r.u; });

  /* 학년 가중(고1 20 : 고2 40 : 고3 40) — 세 학년이 다 있을 때만 */
  var per = {}, ok3 = true;
  ['고1', '고2', '고3'].forEach(function(y){
    var v = cAvg(main.filter(function(r){ return r.yr === y; }));
    per[y] = v; if(v == null) ok3 = false;
  });
  var vW = ok3 ? (per['고1'] * 0.2 + per['고2'] * 0.4 + per['고3'] * 0.4) : null;

  var tr = document.getElementById('tr');
  var track = tr ? tr.value : '';

  var h = '<div class="cres"><div class="cbig"><b>' + cFix(vMain) + '</b><span>등급</span>' +
    '<em>국·수·영·사·과 ' + main.length + '과목 · 총 ' + uSum + '학점 기준 <b>(대학이 보통 보는 값)</b></em></div>' +
    '<div class="csub">' +
    '<div class="l"><i>전 과목 평균 <u>기술·가정, 제2외국어 등 포함</u></i><b>' + cFix(vAll) + '</b></div>' +
    '<div class="l' + (track === '인문' ? ' hi' : '') + '"><i>인문 계열 참고 <u>국·수·영·사</u></i><b>' + cFix(vIn) + '</b></div>' +
    '<div class="l' + (track === '자연' ? ' hi' : '') + '"><i>자연 계열 참고 <u>국·수·영·과</u></i><b>' + cFix(vNa) + '</b></div>' +
    (vW != null ? '<div class="l"><i>학년 가중 <u>20:40:40 — 일부 대학만. 대다수는 학년 구분 없음</u></i><b>' + cFix(vW) + '</b></div>' : '') +
    '</div>' +
    '<button type="button" class="cuse" id="cUse">이 등급(' + cFix(vMain) + ')으로 지원 라인 조회하기</button>';

  var low = main.filter(function(r){ return r.g >= 5; });
  if(low.length) h += '<div class="cwarn">⚠ <b>5등급 이하가 ' + low.length + '과목</b> 있습니다. ' +
    '대학은 등급을 점수로 바꿔 쓰는데 <b>하위 등급에서 점수가 확 벌어집니다</b> — ' +
    '평균 숫자가 보여주는 것보다 실제 손해가 큽니다.</div>';

  var miss = [];
  ['고1', '고2', '고3'].forEach(function(y){ if(per[y] == null) miss.push(y); });
  if(miss.length) h += '<div class="cwarn">아직 <b>' + miss.join(' · ') + '</b> 과목이 비어 있습니다. ' +
    '대학은 보통 <b>고1~고3 1학기</b>를 모두 봅니다 — 다 넣어야 실제 등급에 가까워집니다.</div>';

  out.innerHTML = h + '</div>';

  var g = document.getElementById('g');
  if(g && vMain != null && document.getElementById('calcBox') && !document.getElementById('calcBox').hidden){
    g.value = vMain.toFixed(2);
  }
  var b = document.getElementById('cUse');
  if(b) b.onclick = function(){
    var gg = document.getElementById('g');
    if(gg) gg.value = vMain.toFixed(2);
    if(typeof run === 'function') run();
  };
}

/* 모드 전환 */
function cMode(m){
  var box = document.getElementById('calcBox'), g = document.getElementById('g');
  document.querySelectorAll('.gm').forEach(function(b){
    var on = b.dataset.gm === m;
    b.classList.toggle('on', on);
    b.setAttribute('aria-selected', on ? 'true' : 'false');
  });
  if(!box) return;
  box.hidden = (m !== 'calc');
  if(g){
    if(m === 'calc'){
      g.readOnly = true;
      g.placeholder = '아래에서 계산됩니다';
      var lb = g.parentNode.querySelector('label');
      if(lb) lb.textContent = '내신 평균 등급 (계산값)';
      if(!document.getElementById('cYears').children.length) cBuild();
      cCalc();
    }else{
      g.readOnly = false;
      g.placeholder = '예: 3.5';
      var lb2 = g.parentNode.querySelector('label');
      if(lb2) lb2.textContent = '내신 평균 등급';
    }
  }
}

(function cInit(){
  function go(){
    document.querySelectorAll('.gm').forEach(function(b){
      b.addEventListener('click', function(){ cMode(b.dataset.gm); });
    });
    var q = document.getElementById('cqb');
    if(q) q.addEventListener('click', function(){
      var v = parseFloat(document.getElementById('cqv').value);
      if(!(v >= 1 && v <= 9)) return;
      document.querySelectorAll('#cYears .cr').forEach(function(r){
        var s = r.querySelector('.cs');
        if(s && !s.value) return;
        var g = r.querySelector('.cg');
        g.value = v; g.classList.add('on');
      });
      cCalc();
    });
  }
  if(document.readyState === 'loading') document.addEventListener('DOMContentLoaded', go);
  else go();
})();
"""


def blocks():
    """빌더에서 쓰는 (HTML, CSS, JS) 삼종."""
    return CALC_HTML, CALC_CSS, CALC_JS.replace("__CALC_DATA__", _js_data())
