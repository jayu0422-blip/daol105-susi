# -*- coding: utf-8 -*-
"""9등급 입결 -> 5등급 환산.
   등급 구간 '대표 백분위(중앙값)' 보간 + 클램프 제거 + [1.0,5.0] 재정규화.
   상위권 변별을 살리는 것이 목적."""
import io, json

CUM9 = [0, 4, 11, 23, 40, 60, 77, 89, 96, 100]
CUM5 = [0, 10, 34, 66, 90, 100]
MID9 = [(CUM9[i] + CUM9[i + 1]) / 2.0 for i in range(9)]   # 1~9등급 대표 백분위
MID5 = [(CUM5[i] + CUM5[i + 1]) / 2.0 for i in range(5)]   # 1~5등급 대표 백분위


def pct9(g):
    """9등급 평균값 -> 백분위(%)"""
    if g <= 1: return MID9[0] + (g - 1) * (MID9[1] - MID9[0])
    if g >= 9: return MID9[8]
    i = int(g); f = g - i
    return MID9[i - 1] + f * (MID9[i] - MID9[i - 1])


def raw5(p):
    """백분위(%) -> 5등급 원값 (클램프 없음)"""
    if p <= MID5[0]:
        return 1.0 + (p - MID5[0]) / (MID5[1] - MID5[0])
    if p >= MID5[4]:
        return 5.0 + (p - MID5[4]) / (MID5[4] - MID5[3])
    for i in range(4):
        if MID5[i] <= p <= MID5[i + 1]:
            return (i + 1) + (p - MID5[i]) / (MID5[i + 1] - MID5[i])
    return 5.0


# 9등급 유효범위(1.0~9.0)에 대응하는 원값 하한/상한으로 [1,5] 재정규화
LO = raw5(pct9(1.0))
HI = raw5(pct9(9.0))


def g9_to_g5(g):
    if g is None: return None
    v = raw5(pct9(g))
    v = 1.0 + (v - LO) * 4.0 / (HI - LO)
    return round(max(1.0, min(5.0, v)), 2)


def g9_to_pct(g):
    if g is None: return None
    return round(pct9(g), 1)


if __name__ == '__main__':
    src = json.load(io.open('data_full.json', encoding='utf-8'))
    out = []
    for r in src:
        n = list(r)
        p = []
        for idx in (8, 9, 10):
            n[idx] = g9_to_g5(r[idx])
            p.append(g9_to_pct(r[idx]))
        n += p
        out.append(n)
    json.dump(out, io.open('data_5g.json', 'w', encoding='utf-8'),
              ensure_ascii=False, separators=(',', ':'))

    o = io.open('_변환검증3.txt', 'w', encoding='utf-8')
    o.write("재정규화 기준 LO=%.4f (9등급 1.0)  HI=%.4f (9등급 9.0)\n\n" % (LO, HI))
    o.write("%-8s %-10s %-10s\n" % ('9등급', '백분위%', '5등급'))
    o.write("-" * 32 + "\n")
    for g in [1.0, 1.2, 1.39, 1.45, 1.54, 1.63, 1.70, 2.0, 2.5, 3.0, 4.0, 5.0, 6.0, 7.0, 9.0]:
        o.write("%-8.2f %-10.2f %-10.2f\n" % (g, pct9(g), g9_to_g5(g)))

    o.write("\n[고려대 교과 — 변별 확인]\n")
    KO = [('사회학과', 1.39), ('경영대학', 1.45), ('영어영문', 1.48), ('한국사학', 1.49),
          ('국어국문', 1.54), ('사학과', 1.63), ('불어불문', 1.64), ('독어독문', 1.66), ('한문학과', 1.70)]
    for name, g in KO:
        o.write("  %-8s 9등급 %.2f -> 5등급 %.2f (상위 %.1f%%)\n" % (name, g, g9_to_g5(g), pct9(g)))
    vals = [g9_to_g5(g) for _, g in KO]
    o.write("  고유값 %d개 / %d개 → %s\n" % (len(set(vals)), len(vals), '전부 구분됨' if len(set(vals)) == len(vals) else '일부 중복'))

    v5 = [v for r in out for v in (r[8], r[9], r[10]) if v is not None]
    o.write("\n[분포] n=%s  min %.2f  max %.2f  avg %.2f  고유값 %s개\n"
            % (format(len(v5), ','), min(v5), max(v5), sum(v5) / len(v5), format(len(set(v5)), ',')))
    o.close()
    print('data_5g.json %s행' % format(len(out), ','))
