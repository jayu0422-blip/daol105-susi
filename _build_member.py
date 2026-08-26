# -*- coding: utf-8 -*-
"""재원생 전용 무료 버전 생성 — /member/

  루트(공개)와 다른 점
  1. 리드 폼(상세 결과 열어보기) 제거 — 처음부터 전부 열려 있음
  2. 게이트가 '열어준다'던 항목을 **실제로 구현**
       ① 수능최저 충족 판정  ② 3개년 컷 추이  ③ 출렁임 경고  ④ 특목·자사 주의
       (모집인원·추합은 데이터에 없어 넣지 않고, 없다고 명시한다)
  3. '실패 없이 지원하는 법' → '다올105 컨설팅 프로그램'
  4. 검색 노출 차단(noindex) · 재원생 전용 표시
"""
import io, os, re, sys
sys.stdout.reconfigure(encoding="utf-8")
os.chdir(r"F:\작업\03_기출분석\하남고1_수학_기출분석_SNS\수시조회웹")
os.makedirs("member", exist_ok=True)

s = io.open("index.html", encoding="utf-8", errors="replace").read()
orig = len(s)

def rep(old, new, tag, cnt=1):
    global s
    assert s.count(old) == cnt, f"[{tag}] {s.count(old)} ≠ {cnt}"
    s = s.replace(old, new)

# ── 1. 데이터 경로 (하위 폴더) ──────────────────────────────
rep("data.json?v=20260825b", "../data.json?v=20260825b", "데이터경로")

# ── 2. 게이트 마크업 통째 제거 ──────────────────────────────
i = s.find('<div class="gate" id="gate"')
assert i > 0
d, k = 0, i
while k < len(s):
    if s.startswith("<div", k): d += 1
    elif s.startswith("</div>", k):
        d -= 1
        if d == 0: break
    k += 1
s = s[:i] + '<!-- 재원생 버전: 리드 폼 없음. 상세가 처음부터 열려 있다. -->' + s[k + 6:]

# ── 3. 게이트 JS 제거 ───────────────────────────────────────
def cut_fn(name):
    global s
    j = s.find("function " + name + "(")
    if j < 0: return
    b = s.find("{", j); dd = 0; e = b
    while e < len(s):
        if s[e] == "{": dd += 1
        elif s[e] == "}":
            dd -= 1
            if dd == 0: break
        e += 1
    s = s[:j] + s[e + 1:]
for fn in ("bindGate", "showGate", "gateUnlocked", "srcOf"):
    cut_fn(fn)
s = re.sub(r"\n[^\n]*\b(bindGate|showGate)\s*\([^\n]*\n", "\n", s)
s = re.sub(r"var GATE_KEY=[^;]*;", "", s)
s = re.sub(r"var GAS_URL=[^;]*;", "", s)
s = re.sub(r"var API=[^;]*;", "", s)

# ── 4. 상세 분석 로직 (실제 구현) ───────────────────────────
DETAIL = r"""
/* ══ 재원생 버전 — 게이트가 약속만 하던 항목을 실제로 계산한다 ══ */

/* 수능 최저 문자열 파싱.
   실제 데이터에 있는 형태: "국,수,영,탐(1) 2합7" / "1개4" / "3합13" / 뒤에 "한5" 같은 부가조건. */
function parseMin(txt){
  if(!txt || txt === '-' || txt.indexOf('없음') === 0) return null;
  var sum = /(\d)\s*합\s*(\d+)/.exec(txt);
  if(sum) return {kind:'sum', n:+sum[1], v:+sum[2], raw:txt};
  var cnt = /(\d)\s*개\s*(\d+)/.exec(txt);
  if(cnt) return {kind:'each', n:+cnt[1], v:+cnt[2], raw:txt};
  return {kind:'etc', raw:txt};
}

/* 내 수능 예상 등급(국·수·영·탐) 으로 충족 여부를 본다.
   상위 n과목을 쓰는 규정이라 정렬해서 앞에서부터 센다. */
function judgeMin(txt, my){
  var p = parseMin(txt);
  if(!p) return {t:'none', s:'수능 최저 없음 — 내신만 본다'};
  if(!my || !my.length) return {t:'ask', s:'최저 있음'};
  if(p.kind === 'etc') return {t:'ask', s:'최저 확인 필요'};
  var g = my.slice().sort(function(a,b){return a-b});
  if(p.kind === 'sum'){
    if(g.length < p.n) return {t:'ask', s:'등급 더 입력'};
    var t = 0, i;
    for(i=0;i<p.n;i++) t += g[i];
    return t <= p.v ? {t:'ok', s:'최저 충족 (' + p.n + '합 ' + t + ' ≤ ' + p.v + ')'}
                    : {t:'no', s:'최저 미달 (' + p.n + '합 ' + t + ' > ' + p.v + ')'};
  }
  var c = 0, j;
  for(j=0;j<g.length;j++) if(g[j] <= p.v) c++;
  return c >= p.n ? {t:'ok', s:'최저 충족 (' + p.v + '등급 이내 ' + c + '개)'}
                  : {t:'no', s:'최저 미달 (' + p.v + '등급 이내 ' + c + '개 / ' + p.n + '개 필요)'};
}

/* 3개년 컷 방향 — 숫자가 커지면 컷이 낮아진 것(= 들어가기 쉬워짐) */
function trendOf(r){
  var v = [r[8], r[9], r[10]];           /* 25 / 24 / 23 */
  if(v[0] == null || v[2] == null) return null;
  var diff = v[0] - v[2];                /* +면 최근이 더 높은 등급 = 쉬워짐 */
  var all = v.filter(function(x){return x != null});
  var spread = Math.max.apply(null, all) - Math.min.apply(null, all);
  var dir = Math.abs(diff) < 0.15 ? 'flat' : (diff > 0 ? 'easy' : 'hard');
  return {dir:dir, diff:diff, spread:spread};
}

/* 종합 컷이 교과보다 크게 낮은 학과 — 일반고 학생이 그대로 보면 안 되는 숫자 */
var COMP_GAP = null;
function buildGap(data){
  if(COMP_GAP) return COMP_GAP;
  var m = {}, i, r, c, k;
  for(i=0;i<data.length;i++){
    r = data[i]; c = cutOf(r);
    if(c == null) continue;
    if(r[5] !== '학생부교과' && r[5] !== '학생부종합') continue;
    k = r[0] + '|' + r[4];
    if(!m[k]) m[k] = {};
    if(m[k][r[5]] == null || c < m[k][r[5]]) m[k][r[5]] = c;
  }
  COMP_GAP = {};
  for(k in m) if(m[k]['학생부교과'] != null && m[k]['학생부종합'] != null
                 && m[k]['학생부종합'] - m[k]['학생부교과'] >= 0.8) COMP_GAP[k] = 1;
  return COMP_GAP;
}

/* 입력한 수능 예상 등급 읽기 */
function myMin(){
  var out = [], ids = ['sk','sm','se','ss'], i, v;
  for(i=0;i<ids.length;i++){
    var el = document.getElementById(ids[i]);
    if(!el) continue;
    v = parseFloat(el.value);
    if(v >= 1 && v <= 9) out.push(v);
  }
  return out;
}
"""

m = re.search(r"function cutOf\([^)]*\)\s*\{[^}]*\}", s)
assert m, "cutOf 없음"
s = s[:m.end()] + "\n" + DETAIL + "\n" + s[m.end():]

# ── 5. rowHtml — 판정·추이·경고를 실제로 붙인다 ─────────────
OLD_ROW = """  const minChip = (r[7] && r[7] !== '-') ? '<span class="chip min">최저 있음</span>' : '<span class="chip">최저 없음/미확인</span>';
  const compChip = r[5] === '학생부종합' ? '<span class="chip comp">종합 — 등급은 참고치</span>' : '';"""
NEW_ROW = """  const jm = judgeMin(r[7], myMin());
  const minChip = '<span class="chip ' + (jm.t === 'ok' ? 'mok' : jm.t === 'no' ? 'mno' : jm.t === 'none' ? 'mnone' : 'min') + '">' + jm.s + '</span>';
  const tr = trendOf(r);
  const trChip = !tr ? '' :
    '<span class="chip tr ' + tr.dir + '">' +
      (tr.dir === 'easy' ? '↘ 컷 내려가는 중' : tr.dir === 'hard' ? '↗ 컷 올라가는 중' : '→ 3년째 비슷') +
    '</span>';
  const swChip = (tr && tr.spread >= 1.0)
    ? '<span class="chip sw">⚠ 3년새 ' + tr.spread.toFixed(1) + '등급 출렁임</span>' : '';
  const gapChip = (r[5] === '학생부종합' && buildGap(DATA_ALL)[r[0] + '|' + r[4]])
    ? '<span class="chip gap">⚠ 특목·자사 영향 가능 — 일반고는 그대로 보면 안 됨</span>' : '';
  const compChip = r[5] === '학생부종합' ? '<span class="chip comp">종합 — 등급은 참고치</span>' : '';"""
rep(OLD_ROW, NEW_ROW, "rowHtml 칩")
rep("minChip + compChip + '</div></div>';",
    "minChip + trChip + swChip + compChip + gapChip + '</div></div>';", "칩 조립")

# 전역 데이터 보관 (buildGap 용)
rep("  const data = await load();", "  const data = await load(); DATA_ALL = data;", "전역데이터")
rep("var GATE", "var DATA_ALL = [];\nvar GATE", "전역선언") if "var GATE" in s else None
if "var DATA_ALL" not in s:
    _m = re.search(r"<script(?![^>]*src=)[^>]*>", s)
    s = s[:_m.end()] + chr(10) + "var DATA_ALL = [];" + chr(10) + s[_m.end():]

# ── 6. 수능 예상 등급 입력칸 추가 ───────────────────────────
FORM = """
      <div class="minbox">
        <div class="mb-h">🎯 수능 예상 등급 <span>넣으면 전형별 <b>최저 충족 여부</b>를 자동으로 판정합니다 · 비워도 조회됩니다</span></div>
        <div class="mb-g">
          <div><label>국어</label><input id="sk" type="number" step="0.5" min="1" max="9" placeholder="-"></div>
          <div><label>수학</label><input id="sm" type="number" step="0.5" min="1" max="9" placeholder="-"></div>
          <div><label>영어</label><input id="se" type="number" step="0.5" min="1" max="9" placeholder="-"></div>
          <div><label>탐구</label><input id="ss" type="number" step="0.5" min="1" max="9" placeholder="-"></div>
        </div>
      </div>
"""
mm = re.search(r'<button[^>]*>지원 라인 조회하기</button>', s)
assert mm, "조회 버튼 없음"
bs = s.rfind("<div", 0, mm.start())
s = s[:bs] + FORM + s[bs:]

# ── 7. CSS ──────────────────────────────────────────────────
CSS = """
/* ══ 재원생 버전 추가 스타일 ══ */
.minbox{background:var(--soft2);border:1px solid var(--line);border-radius:12px;padding:13px 14px;margin:14px 0}
.mb-h{font-size:13.5px;font-weight:800;color:var(--ink);margin-bottom:10px}
.mb-h span{display:block;font-size:11.5px;font-weight:600;color:var(--gray2);margin-top:3px;line-height:1.6}
.mb-h b{color:var(--blue-strong)}
.mb-g{display:grid;grid-template-columns:repeat(4,1fr);gap:8px}
.mb-g label{display:block;font-size:11.5px;font-weight:800;color:var(--gray);margin-bottom:4px}
.mb-g input{width:100%;padding:9px 8px;border:1px solid var(--line);border-radius:9px;
  font-size:15px;font-weight:700;text-align:center;color:var(--ink);background:#fff}
.mb-g input:focus{outline:2px solid rgba(49,130,246,.3);border-color:var(--blue)}
.chip.mok{background:#E6F7F0;color:#0B7A55;font-weight:800}
.chip.mno{background:#FFECEC;color:#C2352C;font-weight:800}
.chip.mnone{background:#ECFDF5;color:#065F46;font-weight:800}
.chip.tr.easy{background:#EAF3FF;color:#1B5FB8}
.chip.tr.hard{background:#FFF3E6;color:#B45309}
.chip.tr.flat{background:var(--soft);color:var(--gray)}
.chip.sw{background:#FFF6E5;color:#A16207;font-weight:800}
.chip.gap{background:#F5EEFF;color:#6D28D9;font-weight:800}
.memberbar{background:#0F2E4A;color:#fff;text-align:center;padding:9px 14px;font-size:12.5px;font-weight:700}
.memberbar b{color:#FFD98C}
"""
i = s.rfind("</style>")
s = s[:i] + CSS + s[i:]

# ── 8. 문구 · 메타 ──────────────────────────────────────────
rep("'<a href=\"consulting/\">실패 없이 지원하는 법 &rarr;</a>'",
    "'<a href=\"../consulting/\">다올105 컨설팅 프로그램 &rarr;</a>'", "CTA")
s = s.replace('href="consulting/"', 'href="../consulting/"')
rep("<title>내신 등급으로 보는 수시 지원 라인 | 다올105 무료 조회</title>",
    '<meta name="robots" content="noindex,nofollow" />\n'
    "<title>고3 수시지원 프로그램 (재원생 전용) | 다올105</title>", "타이틀")

# 상단 재원생 안내 바
mb = re.search(r"<body[^>]*>", s)
BAR = ('\n<div class="memberbar">🎓 <b>다올105 재원생 전용</b> · 전 기능 무료 — '
       '수능최저 판정 · 3개년 컷 추이 · 출렁임 경고까지 <b>바로 보입니다</b></div>\n')
s = s[:mb.end()] + BAR + s[mb.end():] if mb else BAR + s

io.open("member/index.html", "w", encoding="utf-8").write(s)
print(f"member/index.html 생성 · {orig:,} → {len(s):,}자")
