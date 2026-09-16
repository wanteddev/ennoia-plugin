# 업로드 경로

| 입력 | 경로 | 확인할 것 |
| --- | --- | --- |
| 대화에 제공된 텍스트 내용 | `upload_rag_text_document` | 현재 정책의 크기·UTF-8·file_name |
| 사용자 PC의 로컬 파일 | `prepare_rag_document_upload` → `upload_ennoia_rag_file` → status | 파일명·실제 size_bytes·content_type, 반환 URL과 exact headers |
| 공개 HTTPS 문서 | `import_rag_document_from_url` | 인증 없는 공개 주소, 허용 형식과 크기 |

## 로컬 파일 전송 계약

1. 정확한 `collection_code`를 알면 `get_rag_collection(collection_code)`로 조회한다. code를 모를 때만 컬렉션 목록에서 찾는다. 표시 이름을 code로 가정하지 않는다.
2. `get_rag_capabilities` 응답의 `allowed_extensions`와 `max_file_size_bytes`를 확인한다. 파일 내용은 읽지 않고 파일명, 실제 byte 크기, content type을 확인한다. 로컬 uploader의 허용 형식은 `.csv`, `.txt`, `.md`, `.pdf`, `.docx`, `.pptx`, `.xlsx`, `.xls`, `.zip`이고 크기는 1~104857600 bytes이다. 서버의 `max_file_size_bytes`가 더 작으면 그 제한을 따른다. 일반 파일만 지원하며 symlink는 지원하지 않는다.
3. 현재 원격 schema에 맞춰 `prepare_rag_document_upload`에 `collection_code`, `file_name`, `size_bytes`, `content_type` 및 동일한 `project_scope`를 전달한다. 로컬 경로를 원격 prepare에 전달하지 않는다.
4. prepare가 성공하고 `method=PUT`인 경우 로컬 `upload_ennoia_rag_file`에 정확히 세 인자를 전달한다: `local_path`는 `/tmp/employee-handbook.pdf`, `upload_url`은 prepare 성공 응답의 URL, `headers`는 prepare 성공 응답의 header object 그대로다. `headers`를 문자열로 바꾸지 않는다. OAuth Bearer·Cookie를 추가하거나 `Content-Length`를 바꾸지 않는다. 파일 byte·base64·본문·`file_data`를 MCP JSON이나 모델 context에 넣지 않는다.
5. 로컬 tool은 disk stream으로 1회 PUT하고 redirect를 거부한다. 대상은 HTTPS `mcp.ennoia.so` 또는 `dev-mcp-server.ennoia.so`의 `/rag/uploads/{opaque-id}`만 허용한다. upload URL·token·headers를 로그·보고서·공유 링크로 출력하지 않는다.
6. PUT 결과에 `file_seq`가 있으면 같은 `collection_code`로 `get_rag_file_status`를 조회한다. 없으면 `list_rag_files(collection_code)`로 해당 파일의 `file_seq`를 찾아 조회한다. 원격 식별자는 `collection_code`와 `file_seq`이며 `collection_id`·`file_id`로 바꾸지 않는다. 같은 `project_scope`를 유지한다.
7. `processing_state=ready`와 `ready_for_agent=true`를 함께 확인해야 준비 완료다. 업로드 ticket 발급, HTTP 전송 성공, 인덱싱 완료를 구분한다. timeout이면 먼저 파일 목록·상태를 확인하고 중복 업로드를 피한다.

로컬 uploader가 설치되지 않았거나 host가 Node 실행·파일 접근을 지원하지 않으면 Ennoia 파일 업로드 화면을 안내하고, 완료 후 같은 컬렉션에서 상태 확인을 이어간다. 파일을 base64로 바꾸거나 원격 서버에서 로컬 경로를 읽으려 하지 않는다.

URL import에 cookie·Authorization header·signed query를 넣거나 내부/private 주소를 제공하지 않는다. 보호된 문서를 public으로 공개해서 이 경로에 맞추지 않는다. 사용자가 제공한 로컬 파일은 위 local upload 경로를 사용한다.

기존 컬렉션을 graph에 연결할 때 `collection_name`이 null이면 정확한 `collection_code`로 `get_rag_collection`을 단건 조회한다. 단건에도 index 이름이 없으면 연결 불가 상태로 알리고 표시 이름·code를 index 이름으로 만들지 않는다.
