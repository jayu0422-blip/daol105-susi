# -*- coding: utf-8 -*-
import fitz

COLS = [('광역',50,70),('기초',70,95),('대학',95,132),('계열',132,155),
        ('모집단위',155,272),('전형유형',272,318),('전형명',318,370),
        ('모집인원',370,388),('전년대비',388,410),('최저',410,470),
        ('기준24',470,518),('등급24',518,550),('환산24',550,588),('충원24',588,607),
        ('기준23',607,643),('등급23',643,673),('환산23',673,713),('충원23',713,738),
        ('등급22',738,768),('충원22',768,800)]
NAMES=[c[0] for c in COLS]

def _cells(cluster):
    cell={n:[] for n in NAMES}
    for w in cluster:
        xc=(w[0]+w[2])/2
        for n,p,q in COLS:
            if p<=xc<q:
                cell[n].append(((w[1]+w[3])/2, w[0], w[4])); break
    return {n:' '.join(t for _,_,t in sorted(v)).strip() for n,v in cell.items()}

def parse_page(pg, gap=3.2):
    ws=[w for w in pg.get_text("words") if 45<=(w[0]+w[2])/2<800]
    if not ws: return []
    ws.sort(key=lambda w:(w[1]+w[3])/2)
    cls=[]; cur=[ws[0]]
    for w in ws[1:]:
        if ((w[1]+w[3])/2)-((cur[-1][1]+cur[-1][3])/2)<=gap: cur.append(w)
        else: cls.append(cur); cur=[w]
    cls.append(cur)

    rows=[]
    for cl in cls:
        rec=_cells(cl)
        if rec['광역'] and '대학' in rec['대학']:
            if rec['광역']=='광역': continue     # 헤더
            rows.append(rec)
        elif rows:
            # 연속 줄 → 직전 행에 병합
            prev=rows[-1]
            if rec['모집단위']:
                prev['모집단위']=(prev['모집단위']+' '+rec['모집단위']).strip()
            for n in NAMES:
                if n=='모집단위': continue
                if rec[n] and not prev[n]: prev[n]=rec[n]
    return rows

def num(s):
    s=str(s).strip().replace(',','')
    # 논술 전형은 원본이 "등급/환산점수"(예: 4.15/73.63) 결합 표기 -> 앞의 등급만 취한다
    if '/' in s: s = s.split('/')[0].strip()
    try:
        v=float(s); return v if 0.5<=v<=9.9 else None
    except: return None
