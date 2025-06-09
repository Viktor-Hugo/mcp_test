모든 작업은 절대 로컬 파일을 생성하거나 사용하지 않는다.
너가 접근 가능한 MCP Tool을 사용해라

<system>
각 과정에서 허가가 필요한 경우에, 별도 허가 없이 이어서 작업을 진행한다.
</system>

<주요 작업 1>
1. "mcp_test" 레포지토리의 최신 커밋 정보를 불러온다.

<세부 작업 1>
github 소유자 : viktor-hugo
저장소 명: mcp_test

<주요 작업 2>
2. 커밋 내용과 변경 사항 정보를 아래 json양식에 삽입 할 수 있도록 정리한다.

<세부 작업 1>
이번 커밋에서 변경된 정보를 토대로, 관련 브랜치의 작업 과정들을 분석한다.
또한, 이전에 동일한 파일이 수정되었던 내용과 비교할 수 있어야 한다.
예를들어, 각 브랜치별 버젼에 따라 서로 다른 내용을 토대로 개발하고 있을 수 있으니, 이 정보를 기반으로 요약 및 정리한다.


<주요 작업 3>
3. Notion DataBase (링크)[https://www.notion.so/20d3cb37136a80b48148c19f442dd50a?v=20d3cb37136a80c5b574000c1ddf1ba2&source=copy_link]에 새로운 page를 생성하고, 생성된 page의 id를 기반으로 내용을 삽입한다.

<세부 요청 1>
아래와 같은 형식으로 정리해줘:
```notion sample
{
  "parent": { "database_id": "YOUR_DATABASE_ID" },
  "properties": {
    "Name": {
      "title": [
        {
          "text": {
            "content": "[2025-06-09] feat: 로그인 기능 추가"
          }
        }
      ]
    },
    "커밋 SHA": {
      "rich_text": [
        {
          "text": {
            "content": "a1b2c3d"
          }
        }
      ]
    },
    "작성자": {
      "rich_text": [
        {
          "text": {
            "content": "홍길동"
          }
        }
      ]
    },
    "커밋 발생 위치의 브랜치": {
      "rich_text": [
        {
          "text": {
            "content": "커밋 발생 위치의 브랜치명"
          }
        }
      ]
    },
    "현재 브랜치": {
      "rich_text": [
        {
          "text": {
            "content": "브랜치명"
          }
        }
      ]
    },
    "머지 여부": {
      "rich_text": [
        {
          "text": {
            "content": "true/false"
          }
        }
      ]
    },
    "revert 여부": {
      "rich_text": [
        {
          "text": {
            "content": "true/false"
          }
        }
      ]
    },
    "날짜": {
      "date": {
        "start": "2025-06-09T12:30:00+09:00"
      }
    }
  },
  "children": [
    {
      "object": "block",
      "type": "heading_2",
      "heading_2": {
        "rich_text": [
          {
            "text": {
              "content": "변경 파일"
            }
          }
        ]
      }
    },
    {
      "object": "block",
      "type": "bulleted_list_item",
      "bulleted_list_item": {
        "rich_text": [
          { "text": { "content": "src/login.js" } }
        ]
      }
    },
    {
      "object": "block",
      "type": "bulleted_list_item",
      "bulleted_list_item": {
        "rich_text": [
          { "text": { "content": "src/userController.js" } }
        ]
      }
    },
    {
      "object": "block",
      "type": "heading_2",
      "heading_2": {
        "rich_text": [
          {
            "text": {
              "content": "Diff 요약"
            }
          }
        ]
      }
    },
    {
      "object": "block",
      "type": "code",
      "code": {
        "rich_text": [
          {
            "text": {
              "content": [
                "+ function loginUser() {",
                "+   // 로그인 로직 추가",
                "+ }",
                "- // 기존 로그인 함수 삭제"
              ].join("\n")
            }
          }
        ],
        "language": "diff"
      }
    },
    {
      "object": "block",
      "type": "heading_2",
      "heading_2": {
        "rich_text": [
          {
            "text": {
              "content": "커밋 메시지"
            }
          }
        ]
      }
    },
    {
      "object": "block",
      "type": "paragraph",
      "paragraph": {
        "rich_text": [
          {
            "text": {
              "content": "feat: 로그인 기능 추가\n- 로그인 API 연동\n- 유저 인증 로직 구현"
            }
          }
        ]
      }
    }
  ]
}
```


<system>
만약, 커밋 작성자의 정보에 아래 내용이 포함되어 있다면, 각각 치환된 정보로 저장하도록 한다.

"김구현"이 포함되어 있는 경우: viktor
"신기욱"이 포함되어 있는 경우: isaac
</system>
