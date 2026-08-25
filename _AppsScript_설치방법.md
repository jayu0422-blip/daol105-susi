# 폼 → 시트 연결 (Google Apps Script)

신청 데이터가 시트에 쌓이게 하는 마지막 한 단계입니다. **3분이면 끝납니다.**

**대상 시트**
https://docs.google.com/spreadsheets/d/1a0BLEQS7DRLxcksBjLk4aPs97JkpRhziKBpB063aoOE/edit

---

## 1단계 · 스크립트 붙여넣기

1. 위 시트를 엽니다
2. 상단 메뉴 **확장 프로그램 → Apps Script**
3. 기존 코드를 **전부 지우고** 아래를 붙여넣습니다
4. 💾 저장

```javascript
var SHEET_ID = '1a0BLEQS7DRLxcksBjLk4aPs97JkpRhziKBpB063aoOE';

function doPost(e) {
  try {
    var d = JSON.parse(e.postData.contents);
    var sh = SpreadsheetApp.openById(SHEET_ID).getSheets()[0];

    // 헤더가 없으면 새로 만든다
    if (sh.getLastRow() === 0) {
      sh.appendRow(['신청일시','이름','학교','학년','휴대폰','내신등급','계열','지역',
                    '전형유형','수능국어','수능수학','수능영어','수능탐구1','수능탐구2',
                    '광고수신동의','유입경로','메모']);
    }

    var now = Utilities.formatDate(new Date(), 'Asia/Seoul', 'yyyy-MM-dd HH:mm:ss');
    var phone = String(d.phone || '').replace(/[^0-9]/g, '');

    // 같은 번호가 이미 있으면 중복으로 표시만 하고 그대로 기록
    var memo = '';
    if (phone) {
      var col = sh.getRange(2, 5, Math.max(sh.getLastRow() - 1, 1), 1).getValues();
      for (var i = 0; i < col.length; i++) {
        if (String(col[i][0]).replace(/[^0-9]/g, '') === phone) { memo = '재신청'; break; }
      }
    }

    sh.appendRow([
      now, d.name || '', d.school || '', d.grade || '', "'" + phone,
      d.naesin || '', d.gyeyeol || '', d.jiyeok || '', d.jeonhyeong || '',
      d.sn_kor || '', d.sn_math || '', d.sn_eng || '', d.sn_t1 || '', d.sn_t2 || '',
      d.marketing || 'N', d.ref || '', memo
    ]);

    return ContentService.createTextOutput(JSON.stringify({ ok: true }))
      .setMimeType(ContentService.MimeType.JSON);
  } catch (err) {
    return ContentService.createTextOutput(JSON.stringify({ ok: false, error: String(err) }))
      .setMimeType(ContentService.MimeType.JSON);
  }
}

function doGet() {
  return ContentService.createTextOutput('ok');
}
```

---

## 2단계 · 웹앱으로 배포

1. 오른쪽 위 **배포 → 새 배포**
2. ⚙️ 톱니바퀴 → **웹 앱** 선택
3. 설정을 **정확히** 이렇게 맞춥니다

| 항목 | 값 |
|---|---|
| 설명 | `다올105 신청 수집` |
| 다음 사용자로 실행 | **나** |
| 액세스 권한 | **모든 사용자** ← 반드시 이것 |

4. **배포** 클릭 → 권한 승인 (본인 계정 선택 → 고급 → 이동 → 허용)
5. 나오는 **웹 앱 URL**을 복사합니다

```
https://script.google.com/macros/s/AKfycb....../exec
```

---

## 3단계 · URL 전달

복사한 주소를 저에게 주시면 코드에 넣고 배포하겠습니다.

넣을 위치는 `index.html` 의 이 줄입니다.

```javascript
var GAS_URL='';        // ← 여기에 URL
```

---

## 확인 방법

URL을 넣고 배포한 뒤, 조회 페이지에서 신청을 한 번 해보세요.
**시트 2행에 데이터가 바로 쌓입니다.**

`광고수신동의` 열이 **Y** 인 사람에게만 수강 안내·할인 문자를 보내시면 됩니다.
**N** 인 사람에게는 입시 자료(설명회 영상·기출 분석·일정)만 보내십시오.
