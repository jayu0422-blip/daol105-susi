/**
 * 다올105 · 내신 상세 진단 자료 신청 폼 자동 생성
 *
 * 사용법
 *   1) script.google.com → 새 프로젝트 → 이 파일 전체를 붙여넣기
 *   2) 상단 함수 선택창에서 폼만들기 → 실행 → 권한 승인
 *   3) 실행 로그(Ctrl+Enter)에 찍힌 3개 주소를 저장
 *
 * 만들어지는 것
 *   · 구글폼 1개 (필수 동의 1 + 선택 동의 1)
 *   · 응답 스프레드시트 1개
 *   · 페이지에 붙일 폼 주소 + 유입경로 프리필 주소
 */

var 폼제목 = '다올105 · 내신 상세 진단 자료 신청';
var 학원 = '다올105';
var 등록번호 = '제 하남 298호';
var 전화 = '031-794-8158';

/* ─────────────────────────────────────────────────────────────
   동의 문구
   개인정보 보호법 제22조 — 선택 동의를 필수로 강제할 수 없다.
   정보통신망법 제50조 — 광고성 정보는 사전 동의가 있어야 보낼 수 있다.
   그래서 ①은 필수(자료를 보내려면 번호가 반드시 필요),
          ②는 선택(설명회·특강 안내는 광고성)으로 나눈다.
   ───────────────────────────────────────────────────────────── */

var 필수동의 = [
  '[필수] 개인정보 수집·이용에 동의합니다',
  '',
  '· 수집 항목 : 학생 이름, 학년, 학교, 휴대폰 번호 (보호자 번호는 선택)',
  '· 수집 목적 : 신청하신 내신 상세 진단 자료 발송, 자료에 대한 문의 응대',
  '· 보유 기간 : 수집일로부터 1년, 이후 지체 없이 파기',
  '',
  '동의하지 않으셔도 됩니다. 다만 자료를 보내드릴 방법이 없어',
  '신청 접수가 어렵습니다. 아래 조회 기능은 동의 없이 그대로 무료입니다.',
  '',
  '삭제를 원하시면 ' + 전화 + '로 말씀해 주세요. 바로 지웁니다.'
].join('\n');

var 선택동의 = [
  '[선택] 입시 설명회·특강 안내를 문자로 받겠습니다',
  '',
  '· 보내는 내용 : 입시 설명회, 학년별 특강, 입시 일정 안내',
  '· 보내는 빈도 : 한 달 2회 이내',
  '· 이 항목은 선택입니다. 동의하지 않으셔도 신청한 자료는 그대로 보내드립니다.',
  '· 수신 거부 : 문자에 적힌 번호로 회신하시거나 ' + 전화 + '로 말씀하시면 즉시 중단합니다.'
].join('\n');

var 폼설명 = [
  '고1·고2 내신 상세 진단 자료를 보내드립니다.',
  '',
  '무엇을 받게 되나요',
  '  · 3개년 합격 컷 추이 14,611개',
  '  · 수능 최저 충족 여부 판정 4,721개 전형',
  '  · 특목고·자사고 강세 전형 판별',
  '  · 지금 등급의 상위 백분위와 목표 등수',
  '',
  '입력하신 번호로 열람 링크를 문자로 보내드립니다.',
  '번호가 정확하지 않으면 자료를 받으실 수 없습니다.',
  '',
  '─────────────────',
  학원 + ' (등록번호 ' + 등록번호 + ')',
  '교습과정 : 진학상담·지도',
  '교습비 : 490,000원 (1개월 · 총 교습시간 2,107분)',
  '문의 : ' + 전화
].join('\n');

var 제출후안내 = [
  '신청이 접수되었습니다.',
  '',
  '입력해 주신 번호로 상세 진단 열람 링크를 문자로 보내드립니다.',
  '평일 기준 당일, 늦어도 다음 날 오전까지 도착합니다.',
  '',
  '문자가 오지 않으면 ' + 전화 + '로 연락 주세요.',
  '번호를 잘못 적으셨다면 다시 신청해 주시면 됩니다.'
].join('\n');


function 폼만들기() {
  var form = FormApp.create(폼제목);
  form.setDescription(폼설명)
      .setConfirmationMessage(제출후안내)
      .setAllowResponseEdits(false)
      .setCollectEmail(false)
      .setLimitOneResponsePerUser(false)
      .setShowLinkToRespondAgain(false)
      .setProgressBar(false);

  var 이름 = form.addTextItem()
    .setTitle('학생 이름')
    .setRequired(true);

  var 학년 = form.addMultipleChoiceItem()
    .setTitle('학년')
    .setChoiceValues(['고1', '고2', '고3·N수'])
    .setRequired(true);

  var 학교 = form.addTextItem()
    .setTitle('학교')
    .setHelpText('예) 미사강변고, 하남고. 검정고시는 "검정고시"라고 적어주세요.')
    .setRequired(true);

  /* 휴대폰 번호 — 형식 검증을 걸어 오타·가짜 입력을 1차로 거른다 */
  var 연락처 = form.addTextItem()
    .setTitle('자료를 받으실 휴대폰 번호')
    .setHelpText('이 번호로 열람 링크를 보내드립니다. 010-1234-5678 형식으로 적어주세요.')
    .setRequired(true);
  연락처.setValidation(
    FormApp.createTextValidation()
      .setHelpText('휴대폰 번호 형식이 아닙니다. 010-1234-5678 처럼 적어주세요.')
      .requireTextMatchesPattern('^01[016789][-\\s]?\\d{3,4}[-\\s]?\\d{4}$')
      .build()
  );

  var 보호자 = form.addTextItem()
    .setTitle('보호자 휴대폰 번호 (선택)')
    .setHelpText('보호자께도 함께 보내드리길 원하시면 적어주세요. 비워두셔도 됩니다.')
    .setRequired(false);

  var 유입 = form.addMultipleChoiceItem()
    .setTitle('어떻게 알고 오셨나요')
    .setChoiceValues(['유튜브', '인스타그램', '네이버 블로그·검색', '카카오톡', '지인 소개', '학원 안내물', '기타'])
    .setRequired(true);

  form.addPageBreakItem().setTitle('개인정보 동의');

  var 동의1 = form.addCheckboxItem()
    .setTitle(필수동의)
    .setChoiceValues(['동의합니다'])
    .setRequired(true);

  var 동의2 = form.addCheckboxItem()
    .setTitle(선택동의)
    .setChoiceValues(['동의합니다'])
    .setRequired(false);

  /* 응답 스프레드시트 */
  var ss = SpreadsheetApp.create(폼제목 + ' (응답)');
  form.setDestination(FormApp.DestinationType.SPREADSHEET, ss.getId());

  /* 페이지에 심을 프리필 주소 — 유입경로/학년을 미리 채워 보낸다 */
  var res = form.createResponse();
  res.withItemResponse(학년.createResponse('고1'));
  res.withItemResponse(유입.createResponse('유튜브'));
  var 프리필 = res.toPrefilledUrl();

  var 결과 = [
    '',
    '════════════════════════════════════════',
    ' 폼이 만들어졌습니다. 아래 3개를 저장하세요.',
    '════════════════════════════════════════',
    '',
    '① 학생이 여는 주소 (페이지 버튼에 연결)',
    '   ' + form.getPublishedUrl(),
    '',
    '② 응답 스프레드시트',
    '   ' + ss.getUrl(),
    '',
    '③ 폼 편집 주소',
    '   ' + form.getEditUrl(),
    '',
    '④ 프리필 주소 (학년·유입경로 자동 입력용)',
    '   ' + 프리필,
    '',
    '   → 위 ④ 주소에서 entry.숫자 부분을 확인하면',
    '      페이지에서 유입경로를 자동으로 넣을 수 있습니다.',
    '',
    '════════════════════════════════════════'
  ].join('\n');

  Logger.log(결과);
  return 결과;
}


/**
 * 문자 발송 명단 만들기
 * 응답 시트에서 아직 안 보낸 건만 뽑아 문자114 규격 CSV로 저장한다.
 * 발송한 뒤에는 시트의 '발송' 열에 O 를 적어두면 다음 회차에서 제외된다.
 */
function 발송명단만들기() {
  var ss = SpreadsheetApp.openByUrl(
    '여기에_응답_스프레드시트_주소를_붙여넣으세요'
  );
  var sh = ss.getSheets()[0];
  var v = sh.getDataRange().getValues();
  if (v.length < 2) { Logger.log('응답이 없습니다.'); return; }

  var head = v[0];
  var col = function (키) {
    for (var i = 0; i < head.length; i++) {
      if (String(head[i]).indexOf(키) >= 0) return i;
    }
    return -1;
  };
  var iName = col('학생 이름');
  var iTel  = col('받으실 휴대폰');
  var iGr   = col('학년');
  var iSent = col('발송');

  /* '발송' 열이 없으면 만든다 */
  if (iSent < 0) {
    iSent = head.length;
    sh.getRange(1, iSent + 1).setValue('발송');
  }

  var out = [['수신번호', '이름', '학년']];
  var 대기 = 0;
  for (var r = 1; r < v.length; r++) {
    if (String(v[r][iSent] || '').trim()) continue;      // 이미 보낸 건
    var tel = String(v[r][iTel] || '').replace(/[^0-9]/g, '');
    if (!/^01[016789]\d{7,8}$/.test(tel)) continue;      // 번호 형식 불량
    out.push([tel, v[r][iName], v[r][iGr]]);
    대기++;
  }

  if (대기 === 0) { Logger.log('보낼 대상이 없습니다.'); return; }

  var csv = out.map(function (row) {
    return row.map(function (c) { return '"' + String(c).replace(/"/g, '""') + '"'; }).join(',');
  }).join('\r\n');

  /* 문자114는 EUC-KR 계열을 쓰는 경우가 있어 UTF-8 BOM 을 붙여둔다 */
  var blob = Utilities.newBlob('﻿' + csv, 'text/csv', '발송명단.csv');
  var file = DriveApp.createFile(blob);
  Logger.log('발송 대기 ' + 대기 + '건\n' + file.getUrl());
}
