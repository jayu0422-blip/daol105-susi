/**
 * 다올105 · 내신 상세 진단 자료 신청 수집기
 *
 *   POST /api/submit          신청 저장 (공개)
 *   GET  /admin?k=KEY         관리자 화면
 *   GET  /api/list?k=KEY      신청 목록 JSON
 *   GET  /api/csv?k=KEY       문자 발송용 CSV
 *   POST /api/mark?k=KEY      발송 완료 표시
 *
 * 저장 구조 — 전화번호를 키로 쓴다. 같은 번호로 다시 신청하면 덮어쓴다.
 *   s:{tel}  →  { name, grade, school, tel, parentTel, src, note, at, sent }
 */

const 학년 = ['중3', '고1', '고2', '고3·N수'];
const 유입 = ['유튜브', '인스타그램', '네이버 블로그·검색', '카카오톡', '지인 소개', '학원 안내물', '기타'];
const TEL = /^01[016789]\d{7,8}$/;

const json = (o, s = 200, h = {}) =>
  new Response(JSON.stringify(o), {
    status: s,
    headers: { 'content-type': 'application/json; charset=utf-8', ...h },
  });

function cors(req, env) {
  const o = req.headers.get('Origin') || '';
  const 허용 = (env.ALLOWED || '').split(',').map(s => s.trim()).filter(Boolean);
  if (!허용.includes(o)) return null;
  return {
    'access-control-allow-origin': o,
    'access-control-allow-methods': 'POST, OPTIONS',
    'access-control-allow-headers': 'content-type',
    'access-control-max-age': '86400',
    'vary': 'Origin',
  };
}

const 정리 = (v, max) => String(v == null ? '' : v).trim().replace(/\s+/g, ' ').slice(0, max);
const 번호만 = v => String(v == null ? '' : v).replace(/[^0-9]/g, '');
const esc = s => String(s == null ? '' : s).replace(/[&<>"']/g, c =>
  ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));

/* 한국 시간 문자열 */
function KST(iso) {
  const d = new Date(new Date(iso).getTime() + 9 * 3600 * 1000);
  const p = n => String(n).padStart(2, '0');
  return `${d.getUTCFullYear()}-${p(d.getUTCMonth() + 1)}-${p(d.getUTCDate())} ${p(d.getUTCHours())}:${p(d.getUTCMinutes())}`;
}

/* 관리자 키 확인 — 길이가 달라도 타이밍이 새지 않게 상수시간 비교 */
function 관리자(url, env) {
  const k = url.searchParams.get('k') || '';
  const want = env.ADMIN_KEY || '';
  if (!want || k.length !== want.length) return false;
  let d = 0;
  for (let i = 0; i < want.length; i++) d |= k.charCodeAt(i) ^ want.charCodeAt(i);
  return d === 0;
}

async function 목록(env) {
  const out = [];
  let cursor;
  do {
    const r = await env.DB.list({ prefix: 's:', cursor, limit: 1000 });
    for (const k of r.keys) out.push(k.name);
    cursor = r.list_complete ? null : r.cursor;
  } while (cursor);

  const rows = [];
  for (let i = 0; i < out.length; i += 40) {
    const chunk = await Promise.all(out.slice(i, i + 40).map(n => env.DB.get(n, 'json')));
    for (const v of chunk) if (v) rows.push(v);
  }
  rows.sort((a, b) => String(b.at).localeCompare(String(a.at)));
  return rows;
}

export default {
  async fetch(req, env) {
    const url = new URL(req.url);
    const path = url.pathname.replace(/\/+$/, '') || '/';

    if (req.method === 'OPTIONS') {
      const h = cors(req, env);
      return h ? new Response(null, { status: 204, headers: h })
               : new Response(null, { status: 403 });
    }

    /* ─────────── 신청 접수 ─────────── */
    if (path === '/api/submit' && req.method === 'POST') {
      const h = cors(req, env);
      if (!h) return json({ ok: false, err: '허용되지 않은 접근입니다.' }, 403);

      let b;
      try { b = await req.json(); } catch { return json({ ok: false, err: '형식 오류' }, 400, h); }

      /* 봇 차단 — 사람 눈에 안 보이는 칸이 채워져 있으면 거른다 */
      if (정리(b.website, 50)) return json({ ok: true }, 200, h);

      const name = 정리(b.name, 20);
      const grade = 정리(b.grade, 10);
      const school = 정리(b.school, 30);
      const tel = 번호만(b.tel);
      const parentTel = 번호만(b.parentTel);
      const src = 정리(b.src, 20);
      const note = 정리(b.note, 100);   // 상담 맥락 (내신·계열·지역·전형)

      const 오류 = [];
      if (name.length < 2) 오류.push('이름을 확인해 주세요.');
      if (!학년.includes(grade)) 오류.push('학년을 골라주세요.');
      if (school.length < 2) 오류.push('학교를 적어주세요.');
      if (!TEL.test(tel)) 오류.push('휴대폰 번호를 확인해 주세요. (010-1234-5678)');
      if (parentTel && !TEL.test(parentTel)) 오류.push('보호자 번호 형식을 확인해 주세요.');
      if (b.agree !== true) 오류.push('개인정보 수집·이용 동의가 필요합니다.');
      if (오류.length) return json({ ok: false, err: 오류[0] }, 400, h);

      /* 같은 IP 에서 한 시간에 8건까지 */
      const ip = req.headers.get('CF-Connecting-IP') || '0';
      const rk = 'rl:' + ip;
      const n = parseInt(await env.DB.get(rk) || '0', 10);
      if (n >= 8) return json({ ok: false, err: '잠시 후 다시 시도해 주세요.' }, 429, h);
      await env.DB.put(rk, String(n + 1), { expirationTtl: 3600 });

      const 기존 = await env.DB.get('s:' + tel, 'json');
      const rec = {
        name, grade, school, tel,
        parentTel: parentTel || '',
        src: 유입.includes(src) ? src : '기타',
        note,
        at: 기존?.at || new Date().toISOString(),
        up: new Date().toISOString(),
        sent: 기존?.sent || '',
        ua: 정리(req.headers.get('User-Agent'), 120),
      };
      await env.DB.put('s:' + tel, JSON.stringify(rec));
      return json({ ok: true, again: !!기존 }, 200, h);
    }

    /* ─────────── 관리자 ─────────── */
    const 관 = 관리자(url, env);

    if (path === '/api/list') {
      if (!관) return json({ ok: false }, 403);
      return json({ ok: true, rows: await 목록(env) });
    }

    if (path === '/api/csv') {
      if (!관) return new Response('403', { status: 403 });
      const 미발송 = url.searchParams.get('all') !== '1';
      const rows = (await 목록(env)).filter(r => 미발송 ? !r.sent : true);
      const q = s => '"' + String(s == null ? '' : s).replace(/"/g, '""') + '"';
      const csv = [['수신번호', '이름', '학년', '학교', '상담맥락', '신청일시']]
        .concat(rows.map(r => [r.tel, r.name, r.grade, r.school, r.note || '', KST(r.at)]))
        .map(r => r.map(q).join(',')).join('\r\n');
      return new Response('﻿' + csv, {
        headers: {
          'content-type': 'text/csv; charset=utf-8',
          'content-disposition': 'attachment; filename="daol105-sms.csv"',
        },
      });
    }

    if (path === '/api/mark' && req.method === 'POST') {
      if (!관) return json({ ok: false }, 403);
      const { tel, sent } = await req.json();
      const k = 's:' + 번호만(tel);
      const r = await env.DB.get(k, 'json');
      if (!r) return json({ ok: false }, 404);
      r.sent = sent ? new Date().toISOString() : '';
      await env.DB.put(k, JSON.stringify(r));
      return json({ ok: true });
    }

    if (path === '/admin') {
      if (!관) {
        return new Response(
          '<meta charset="utf-8"><body style="font-family:system-ui;padding:60px;text-align:center;color:#475569">' +
          '<h2 style="color:#0F172A">접근 권한이 없습니다</h2><p>주소 끝에 관리자 키가 필요합니다.</p></body>',
          { status: 403, headers: { 'content-type': 'text/html; charset=utf-8' } });
      }
      const rows = await 목록(env);
      return new Response(관리자화면(rows, url.searchParams.get('k')), {
        headers: {
          'content-type': 'text/html; charset=utf-8',
          'x-robots-tag': 'noindex, nofollow',
          'cache-control': 'no-store',
        },
      });
    }

    return new Response('not found', { status: 404 });
  },
};


function 관리자화면(rows, key) {
  const 총 = rows.length;
  const 미발송 = rows.filter(r => !r.sent).length;

  const 집계 = (fn) => {
    const m = {};
    for (const r of rows) { const v = fn(r) || '미상'; m[v] = (m[v] || 0) + 1; }
    return Object.entries(m).sort((a, b) => b[1] - a[1]);
  };
  const 칩 = arr => arr.map(([k, v]) =>
    `<span class="chip">${esc(k)} <b>${v}</b></span>`).join('');

  /* 신청이 0건일 때 표의 모양을 보여주는 예시 두 줄. 실제 데이터가 아니다. */
  const 예시행 = `
    <tr class="demo"><td>–</td><td><span class="demolb">예시</span>2026-08-27 21:14</td>
      <td><b>김ㅇㅇ</b></td><td>고2</td><td>미사강변고</td>
      <td class="tel">010-1234-5678</td><td class="tel">010-8765-4321</td>
      <td class="memo">내신 2.4 · 자연 · 서울</td><td>유튜브</td></tr>
    <tr class="demo"><td>–</td><td><span class="demolb">예시</span>2026-08-27 22:03</td>
      <td><b>이ㅇㅇ</b></td><td>고1</td><td>하남고</td>
      <td class="tel">010-2222-3333</td><td class="tel">–</td>
      <td class="memo">–</td><td>인스타그램</td></tr>`;

  const tr = rows.map(r => `<tr class="${r.sent ? 'done' : ''}">
    <td><input type="checkbox" data-tel="${esc(r.tel)}" ${r.sent ? 'checked' : ''}></td>
    <td>${esc(KST(r.at))}</td>
    <td><b>${esc(r.name)}</b></td>
    <td>${esc(r.grade)}</td>
    <td>${esc(r.school)}</td>
    <td class="tel">${esc(r.tel.replace(/^(01[016789])(\d{3,4})(\d{4})$/, '$1-$2-$3'))}</td>
    <td class="tel">${esc(r.parentTel ? r.parentTel.replace(/^(01[016789])(\d{3,4})(\d{4})$/, '$1-$2-$3') : '–')}</td>
    <td class="memo">${esc(r.note || '–')}</td>
    <td>${esc(r.src)}</td>
  </tr>`).join('');

  return `<!doctype html><html lang="ko"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex,nofollow">
<title>다올105 · 자료 신청 관리</title>
<style>
:root{color-scheme:light}
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:-apple-system,BlinkMacSystemFont,'Pretendard','Malgun Gothic',sans-serif;
  background:#F8FAFC;color:#0F172A;padding:24px 18px 60px;-webkit-font-smoothing:antialiased}
.w{max-width:1180px;margin:0 auto}
h1{font-size:22px;font-weight:800;letter-spacing:-.03em;margin-bottom:4px}
.sub{font-size:13px;color:#64748B;margin-bottom:20px}
.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px;margin-bottom:16px}
.st{background:#fff;border:1px solid #E2E8F0;border-radius:13px;padding:15px 16px}
.st .k{font-size:12px;font-weight:700;color:#64748B;margin-bottom:5px}
.st .v{font-size:26px;font-weight:800;letter-spacing:-.03em}
.st.a .v{color:#2563EB}.st.b .v{color:#D97706}.st.c .v{color:#059669}
.box{background:#fff;border:1px solid #E2E8F0;border-radius:13px;padding:14px 16px;margin-bottom:16px}
.box h3{font-size:12.5px;font-weight:800;color:#64748B;margin-bottom:9px}
.chip{display:inline-block;background:#F1F5F9;border-radius:8px;padding:5px 10px;
  font-size:12.5px;font-weight:700;color:#475569;margin:0 6px 6px 0}
.chip b{color:#0F172A}
.bar{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:14px}
.btn{padding:10px 16px;border-radius:10px;border:0;font-size:13.5px;font-weight:700;
  cursor:pointer;font-family:inherit;text-decoration:none;display:inline-block}
.p{background:#2563EB;color:#fff}.p:hover{background:#1D4ED8}
.s{background:#fff;color:#334155;border:1px solid #CBD5E1}.s:hover{background:#F1F5F9}
table{width:100%;border-collapse:collapse;background:#fff;border:1px solid #E2E8F0;
  border-radius:13px;overflow:hidden;font-size:13.5px}
th{background:#F8FAFC;text-align:left;padding:11px 12px;font-weight:800;font-size:12px;
  color:#64748B;border-bottom:1px solid #E2E8F0;white-space:nowrap}
td{padding:11px 12px;border-bottom:1px solid #F1F5F9;white-space:nowrap}
tr:last-child td{border-bottom:0}
tr.done{background:#F8FAFC;color:#94A3B8}
tr.done b{color:#94A3B8;font-weight:700}
.tel{font-variant-numeric:tabular-nums;font-weight:700}
.memo{font-size:12.5px;color:#64748B;max-width:190px;overflow:hidden;text-overflow:ellipsis}
.y{color:#059669;font-weight:800;font-size:12px}
.n{color:#CBD5E1}
input[type=checkbox]{width:17px;height:17px;cursor:pointer;accent-color:#2563EB}
.scroll{overflow-x:auto;-webkit-overflow-scrolling:touch}
.empty{background:#fff;border:1px solid #E2E8F0;border-radius:13px;padding:34px 20px;
  text-align:center;color:#64748B;font-size:14px;line-height:1.8;margin-bottom:16px}
.empty b{color:#0F172A;font-weight:800;display:block;font-size:15.5px;margin-bottom:6px}
.note{font-size:12px;color:#94A3B8;line-height:1.75;margin-top:14px}
tr.demo td{color:#CBD5E1;font-style:italic}
tr.demo b{color:#CBD5E1;font-weight:700}
.demolb{display:inline-block;background:#F1F5F9;color:#64748B;border-radius:6px;
  padding:2px 7px;font-size:11px;font-weight:800;font-style:normal;margin-right:6px}
.fields{background:#fff;border:1px solid #E2E8F0;border-radius:13px;padding:14px 16px;margin-bottom:16px}
.fields h3{font-size:12.5px;font-weight:800;color:#64748B;margin-bottom:10px}
.fields ul{list-style:none;display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:7px}
.fields li{font-size:13px;color:#334155;line-height:1.5;padding-left:17px;position:relative}
.fields li:before{content:'✓';position:absolute;left:0;color:#2563EB;font-weight:800}
.fields li i{font-style:normal;color:#94A3B8;font-size:12px}
</style></head><body><div class="w">
<h1>자료 신청 관리</h1>
<div class="sub">다올105 · 내신 상세 진단 자료 신청 현황</div>

<div class="stats">
  <div class="st a"><div class="k">전체 신청</div><div class="v">${총}</div></div>
  <div class="st b"><div class="k">발송 대기</div><div class="v">${미발송}</div></div>
</div>

<div class="fields"><h3>신청 한 건에서 받는 항목</h3><ul>
  <li>학생 이름</li>
  <li>학년 <i>고1 / 고2 / 고3·N수</i></li>
  <li>학교</li>
  <li>휴대폰 번호 <i>형식 검증함</i></li>
  <li>보호자 번호 <i>선택</i></li>
  <li>상담 맥락 <i>내신·계열·지역·전형</i></li>
  <li>유입 경로 <i>어디서 보고 왔나</i></li>
  <li>개인정보 동의 <i>필수 · 체크해야 제출됨</i></li>
  <li>신청 일시</li>
</ul></div>

${총 ? `<div class="box"><h3>학년</h3>${칩(집계(r => r.grade))}</div>
<div class="box"><h3>유입 경로</h3>${칩(집계(r => r.src))}</div>
<div class="box"><h3>학교</h3>${칩(집계(r => r.school))}</div>` : `<div class="empty">
  <b>아직 신청이 없습니다</b>
  신청이 들어오면 아래 표에 한 줄씩 쌓입니다.<br>
  지금 보이는 회색 줄은 <b style="display:inline;font-size:inherit">모양을 보여드리는 예시</b>이고, 실제 데이터가 아닙니다.
</div>`}

<div class="bar">
  <a class="btn p" href="/api/csv?k=${encodeURIComponent(key)}">발송 대기 ${미발송}건 CSV 받기</a>
  <a class="btn s" href="/api/csv?all=1&k=${encodeURIComponent(key)}">전체 ${총}건 CSV</a>
  <button class="btn s" onclick="location.reload()">새로고침</button>
</div>

<div class="scroll"><table>
<thead><tr><th>발송</th><th>신청일시</th><th>이름</th><th>학년</th><th>학교</th>
<th>휴대폰</th><th>보호자</th><th>상담 맥락</th><th>유입</th></tr></thead>
<tbody>${총 ? tr : 예시행}</tbody></table></div>

<div class="note">
  체크박스를 누르면 발송 완료로 기록됩니다. 다음 CSV에서 제외됩니다.<br>
  동의는 <b>입시 자료 제공</b>까지입니다. 수강 안내·모집·할인 같은
  <b>광고성 문자는 보내면 안 됩니다.</b><br>
  이 화면 주소는 공유하지 마세요. 개인정보가 들어 있습니다.
</div>
</div>
<script>
document.querySelectorAll('input[type=checkbox]').forEach(function(c){
  c.addEventListener('change', function(){
    var tr = c.closest('tr');
    tr.classList.toggle('done', c.checked);
    fetch('/api/mark?k=' + encodeURIComponent(${JSON.stringify(key)}), {
      method: 'POST',
      headers: {'content-type': 'application/json'},
      body: JSON.stringify({tel: c.dataset.tel, sent: c.checked})
    }).catch(function(){ alert('저장에 실패했습니다. 새로고침 후 다시 시도해 주세요.'); });
  });
});
</script></body></html>`;
}
