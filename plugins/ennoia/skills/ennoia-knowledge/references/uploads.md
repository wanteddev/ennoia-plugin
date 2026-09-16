# 업로드 경로

| 입력 | 경로 | 확인할 것 |
| --- | --- | --- |
| 텍스트 내용 | `upload_rag_text_document` | 현재 정책의 크기·UTF-8·file_name |
| 로컬 PDF/Office 등 binary | `prepare_rag_document_upload` | 반환된 method·upload URL·필수 header·만료·실제 파일 byte |
| 공개 HTTPS 문서 | `import_rag_document_from_url` | 인증 없는 공개 주소, 허용 형식과 크기 |

One-time upload는 준비 tool 호출 후 host의 파일 전송 기능으로 반환된 URL에 실제 byte를 `PUT`해야 한다. upload URL을 일반 보고서·로그·공유 링크로 출력하지 않는다. host에서 byte 전송이 불가능하면 Ennoia의 파일 업로드 화면을 통한 업로드가 필요하다고 정확히 알리고, 완료 후 같은 컬렉션에서 상태 확인을 이어간다.

URL import에 cookie·Authorization header·signed query를 넣거나 내부/private 주소를 제공하지 않는다. 보호된 문서를 public으로 공개해서 이 경로에 맞추지 않는다. 사용자가 제공한 로컬 파일은 one-time upload 경로를 사용한다.

업로드 ticket 발급, HTTP 전송 성공, 인덱싱 완료는 서로 다른 단계다. 마지막은 `get_rag_file_status`의 readiness로 확인한다. 오류가 timeout이라면 먼저 파일 목록·상태를 조회해 중복 업로드를 피한다.

기존 컬렉션을 graph에 연결할 때 목록의 `collection_name`이 null이면 정확한 `collection_code`로 `get_rag_collection`을 단건 조회한다. 단건에도 index 이름이 없으면 연결 불가 상태로 알리고 표시 이름·code를 index 이름으로 만들지 않는다.
