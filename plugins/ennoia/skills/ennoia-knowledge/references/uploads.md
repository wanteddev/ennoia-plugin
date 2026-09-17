# 업로드 경로

| 입력 | 경로 | 확인할 것 |
| --- | --- | --- |
| 대화에 제공된 텍스트 내용 | `upload_rag_text_document` | 현재 정책의 크기·UTF-8·file_name |
| 사용자 PC의 로컬 파일 | `prepare_rag_document_upload` → `upload_ennoia_rag_file` → status | 파일명·실제 size_bytes·content_type, 반환 URL과 exact headers |
| 공개 HTTPS 문서 | `import_rag_document_from_url` | 인증 없는 공개 주소, 허용 형식과 크기 |

## 로컬 파일 전송 계약

1. 정확한 `collection_code`를 알면 `get_rag_collection(collection_code)`로 조회한다. code를 모를 때만 컬렉션 목록에서 찾는다. 표시 이름을 code로 가정하지 않는다.
2. 현재 도구 목록에 `upload_ennoia_rag_file`이 있는지 먼저 확인한다. 없으면 `prepare_rag_document_upload`를 호출하지 않는다. Ennoia plugin을 최신 버전으로 업데이트하고 세션을 다시 시작한 뒤 도구 목록을 다시 확인하도록 안내한다. 일반 HTTP client나 `curl`을 대체 수단으로 사용하지 않는다.
3. `get_rag_capabilities` 응답의 `allowed_extensions`와 `max_file_size_bytes`를 확인한다. 파일 내용은 읽지 않고 파일명, 실제 byte 크기, content type을 확인한다. 로컬 uploader의 허용 형식은 `.csv`, `.txt`, `.md`, `.pdf`, `.docx`, `.pptx`, `.xlsx`, `.xls`, `.zip`이고 크기는 1~104857600 bytes이다. 서버의 `max_file_size_bytes`가 더 작으면 그 제한을 따른다. 일반 파일만 지원하며 symlink는 지원하지 않는다.
4. `file_name`은 ASCII만 사용한다. 한글 등 non-ASCII 이름이면 영문·숫자·`-`·`_`로 이름을 바꾸고 기존 확장자를 유지한 실제 파일을 준비하도록 안내한다. 표시 이름만 바꾸거나 존재하지 않는 경로를 만들어내지 않는다.
5. 현재 원격 schema에 맞춰 `prepare_rag_document_upload`에 `collection_code`, `file_name`, `size_bytes`, `content_type` 및 동일한 `project_scope`를 전달한다. 로컬 경로를 원격 prepare에 전달하지 않는다.
6. prepare가 성공하고 `method=PUT`인 경우 로컬 `upload_ennoia_rag_file`에 정확히 세 인자를 전달한다: `local_path`는 `/tmp/employee-handbook.pdf`, `upload_url`은 prepare 성공 응답의 URL, `headers`는 prepare 성공 응답의 header object 그대로다. `headers`를 문자열로 바꾸지 않는다. OAuth Bearer·Cookie를 추가하거나 `Content-Length`를 바꾸지 않는다. 파일 byte·base64·본문·`file_data`를 MCP JSON이나 모델 context에 넣지 않는다.
7. 로컬 tool은 자신이 실행되는 device host에서 보이는 파일만 읽는다. Cowork 채팅 첨부의 cloud path와 device host의 연결된 로컬 폴더는 서로 다른 filesystem일 수 있다. `FILE_NOT_FOUND_ON_UPLOADER_HOST`, `FILE_ACCESS_DENIED`, `FILE_NOT_REGULAR`이면 같은 ticket을 임의의 다른 경로로 반복하지 않고 아래 웹 업로드 링크를 안내한다.
8. 웹 링크는 확인된 `group_code`, `project_code`, `collection_code`를 각각 percent-encoding하여 만든다. 표시 이름이나 예시 ID를 대신 넣지 않는다. 환경은 현재 Ennoia MCP 연결 endpoint로 판단한다. `https://mcp.ennoia.so/mcp`이면 `[Ennoia에서 파일 업로드](https://ennoia.so/studio/rag/files-detail?group={group_code}&project={project_code}&slug=rag&collection={collection_code})`, `https://dev-mcp-server.ennoia.so/mcp`이면 `[Ennoia dev에서 파일 업로드](https://dev.ennoia.so/studio/rag/files-detail?group={group_code}&project={project_code}&slug=rag&collection={collection_code})` 형식을 사용한다. 결과에는 `{...}` placeholder가 아니라 실제 값을 넣은 클릭 가능한 Markdown 링크를 제공한다. 현재 context에 code가 없으면 `get_current_ennoia_project`로 확인한다. endpoint를 확인할 수 없으면 환경을 추측하거나 잘못된 링크를 만들지 않는다.
9. 로컬 tool은 disk stream으로 1회 PUT하고 redirect를 거부한다. 대상은 HTTPS `mcp.ennoia.so` 또는 `dev-mcp-server.ennoia.so`의 `/rag/uploads/{opaque-id}`만 허용한다. upload URL·token·headers를 로그·보고서·공유 링크로 출력하지 않는다.
10. PUT 결과에 `file_seq`가 있으면 같은 `collection_code`로 `get_rag_file_status`를 조회한다. 없으면 `list_rag_files(collection_code)`로 해당 파일의 `file_seq`를 찾아 조회한다. 원격 식별자는 `collection_code`와 `file_seq`이며 `collection_id`·`file_id`로 바꾸지 않는다. 같은 `project_scope`를 유지한다.
11. `processing_state=ready`와 `ready_for_agent=true`를 함께 확인해야 준비 완료다. 업로드 ticket 발급, HTTP 전송 성공, 인덱싱 완료를 구분한다. timeout이면 먼저 파일 목록·상태를 확인하고 중복 업로드를 피한다.

로컬 uploader가 설치되지 않았거나 host가 Node 실행·파일 접근을 지원하지 않으면 위 규칙으로 실제 Ennoia 파일 업로드 화면 링크를 안내하고, 완료 후 같은 컬렉션에서 상태 확인을 이어간다. 파일을 base64로 바꾸거나 원격 서버에서 로컬 경로를 읽으려 하지 않는다. binary 파일을 임의로 텍스트 변환해 `upload_rag_text_document`로 대신 올리지 않는다.

URL import에 cookie·Authorization header·signed query를 넣거나 내부/private 주소를 제공하지 않는다. 보호된 문서를 public으로 공개해서 이 경로에 맞추지 않는다. 사용자가 제공한 로컬 파일은 위 local upload 경로를 사용한다.

기존 컬렉션을 graph에 연결할 때 `collection_name`이 null이면 정확한 `collection_code`로 `get_rag_collection`을 단건 조회한다. 단건에도 index 이름이 없으면 연결 불가 상태로 알리고 표시 이름·code를 index 이름으로 만들지 않는다.
