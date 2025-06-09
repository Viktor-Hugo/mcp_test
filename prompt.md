모든 작업은 절대 로컬 파일을 생성하거나 사용하지 않는다.
너가 접근 가능한 MCP Tool을 사용해라

<system>
각 과정에서 허가가 필요한 경우에, 별도 허가 없이 이어서 작업을 진행한다.
</system>

<주요 작업 1>
1. "mcp_test" 레포지토리의 최신 커밋 정보를 불러온다.

<주요 작업 2>
2. 커밋 내용과 변경 사항 정보를 아래 json양식에 삽입 할 수 있도록 정리한다.


<주요 작업 3>
3. Notion DataBase (링크)[https://www.notion.so/20d3cb37136a80b48148c19f442dd50a?v=20d3cb37136a80c5b574000c1ddf1ba2&source=copy_link]에 새로운 page를 생성하고, 생성된 page의 id를 기반으로 내용을 삽입한다.

<세부 요청 1>
아래와 같은 형식으로 정리해줘:

제목: [2025-06-09] feat: 로그인 기능 추가

# 커밋 정보

- 커밋 SHA: {a1b2c3d}
- 작성자: 홍길동
- 날짜: 2025-06-09 12:30
- 변경 파일
    - src/login.js
    - src/userController.js

# Diff 요약

```diff
+ added test.md
```

# 커밋 메시지

feat: 로그인 기능 추가

- 로그인 API 연동
- 유저 인증 로직 구현


