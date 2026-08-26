# -*- coding: utf-8 -*-
"""고3(루트) 조회 페이지에 hs12의 '내 등급은 어디쯤인가' 막대를 이식.

  hs12와 고3의 data 행 포맷이 동일해서(r[0]대학 r[1]지역 r[5]전형유형 r[8~10]3개년컷)
  uniBar()를 그대로 옮길 수 있다. 변수명만 고3 팔레트로 맞춘다.
"""
import io, os, re, sys
sys.stdout.reconfigure(encoding="utf-8")
os.chdir(r"F:\작업\03_기출분석\하남고1_수학_기출분석_SNS\수시조회웹")

hs = io.open("hs12/index.html", encoding="utf-8", errors="replace").read()
g3 = io.open("index.html", encoding="utf-8", errors="replace").read()
orig = len(g3)

def grab(src, name):
    i = src.find("function " + name + "(")
    assert i >= 0, name
    j = src.find("{", i); d = 0; k = j
    while k < len(src):
        if src[k] == "{": d += 1
        elif src[k] == "}":
            d -= 1
            if d == 0: return src[i:k + 1]
        k += 1
    raise AssertionError(name)

MED, UNI = grab(hs, "medOf"), grab(hs, "uniBar")

# ── 변수명 매핑 (hs12 팔레트 → 고3 팔레트) ─────────────────
MAP = {"var(--card)": "#fff", "var(--ln)": "var(--line)", "var(--g1)": "var(--gray)",
       "var(--g2)": "var(--gray)", "var(--g3)": "var(--gray2)", "var(--b3)": "var(--blue-strong)",
       "var(--bg)": "var(--soft2)"}

CSS = """
/* ══ 내 등급은 어디쯤인가 (hs12에서 이식) ══ */
.uni{background:#fff;border:1px solid var(--line);border-radius:13px;padding:16px 15px 14px;margin-bottom:16px}
.uni-h{font-size:13.5px;font-weight:800;color:var(--ink);letter-spacing:-.02em;margin-bottom:26px}
.uni-w{position:relative;margin-bottom:13px}
.uni-bar{position:relative;display:flex;height:26px;border-radius:7px;overflow:hidden}
.uni-bar i{position:relative;display:flex;align-items:center;justify-content:center;font-style:normal}
.uni-bar i span{font-size:10px;font-weight:800;color:#fff;white-space:nowrap;letter-spacing:-.03em;
  text-shadow:0 1px 2px rgba(0,0,0,.25)}
.uni-bar .s1{flex:1;background:#059669}
.uni-bar .s2{flex:1;background:#2563EB}
.uni-bar .s3{flex:1;background:#D97706}
.uni-bar .s4{flex:1;background:#EA580C}
.uni-bar .s5{flex:1;background:#DC2626}
.uni-tk{position:relative;height:9px}
.uni-tk u{position:absolute;top:0;transform:translateX(-50%);width:0;height:0;text-decoration:none;
  border-left:5px solid transparent;border-right:5px solid transparent;border-bottom:7px solid}
.uni-w .me{position:absolute;top:-24px;transform:translateX(-50%);z-index:2;font-weight:800}
.uni-w .me span{display:block;background:var(--ink);color:#fff;font-size:11px;padding:3px 7px;
  border-radius:6px;white-space:nowrap;letter-spacing:-.02em}
.uni-w .me:after{content:'';position:absolute;left:50%;bottom:-7px;transform:translateX(-50%);
  border:4px solid transparent;border-top-color:var(--ink)}
.uni-ax{display:flex;justify-content:space-between;font-size:10.5px;font-weight:700;
  color:var(--gray2);margin-top:2px;font-variant-numeric:tabular-nums}
.uni-msg{font-size:12.5px;color:var(--gray);line-height:1.7;padding:9px 11px;background:var(--soft2);
  border-radius:9px;margin-bottom:11px}
.uni-msg b{color:var(--blue-strong);font-weight:800}
.lg{display:flex;align-items:baseline;gap:8px;padding:6px 0;border-top:1px solid #F1F5F9}
.lg em{width:8px;height:8px;border-radius:50%;flex:0 0 auto;align-self:center}
.lg>b{font-size:14px;font-weight:800;color:var(--ink);font-variant-numeric:tabular-nums;flex:0 0 auto}
.lg span{font-size:12.5px;font-weight:700;color:var(--gray);line-height:1.5}
.lg i{display:block;font-style:normal;font-size:11px;font-weight:600;color:var(--gray2);margin-top:1px}
.uni-n{font-size:11px;color:var(--gray2);line-height:1.7;margin-top:10px;padding-top:9px;
  border-top:1px solid var(--line)}
.uni-n b{color:var(--gray);font-weight:800}
"""

# ① CSS 주입
i = g3.rfind("</style>")
assert i > 0, "style 없음"
g3 = g3[:i] + CSS + g3[i:]

# ② 함수 주입 — cutOf 정의 뒤에
JS = "\n\n/* ── 내 등급 위치 막대 (hs12 이식) ── */\n" + MED + "\n\n" + UNI + "\n"
for k, v in MAP.items():
    JS = JS.replace(k, v)
m = re.search(r"function cutOf\([^)]*\)\s*\{[^}]*\}", g3)
assert m, "cutOf 없음"
g3 = g3[:m.end()] + JS + g3[m.end():]

io.open("index.html", "w", encoding="utf-8").write(g3)
print(f"이식 완료 · {orig:,} → {len(g3):,}자 (medOf {len(MED)} · uniBar {len(UNI)})")
