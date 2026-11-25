# App과 lifecycle

| 사용자 요청 | 도구와 확인 |
| --- | --- |
| App 찾기 | `list_ennoia_apps` → exact `assistant_hash` → 필요한 경우 `get_ennoia_app` |
| App 생성 | 사용 가능한 배포를 확인한 뒤 `create_ennoia_app`; 생성이 에이전트 배포를 대신하지 않는다. |
| App 변경 | `get_ennoia_app`의 현재 설정 전체를 보존하고 요청한 변경을 합쳐 `update_ennoia_app`에 전달 |
| 복제 | `clone_ennoia_app` 후 새 ID 확인. 공유 설정까지 동일하게 복제됐다고 가정하지 않는다. |
| 공개 링크 생성·활성화·비활성화·철회 | `share_ennoia_app`의 `action=create/enable/disable/revoke`; 요청한 공개 범위만 적용 |
| App 삭제 | `delete_ennoia_app`; 에이전트나 전체 배포까지 삭제하지 않는다. |
| 에이전트 이름 변경·복제·삭제 | `rename_multi_agent`, `clone_multi_agent`, `delete_multi_agent`; exact ID와 영향 범위 확인 |
| 배포 중지·삭제 | `stop_multi_agent_deployment`, `delete_multi_agent_deployment`; 버전과 선행 실행 상태 확인 |

App 수정은 부분 patch가 아니다. 현재 호출할 tool input schema와 실제 상세 응답이 지원하는 설정 계약으로 전체 settings를 보낸다. 구 계약의 여섯 필드 `name`, `description`, `welcome_message`, `history_count`, `allow_file_upload`, `recommended_questions`가 모두 완전하게 확인됐으면 요청한 값만 교체해 승인된 수정을 진행한다. 그 계약에 없는 `welcome_message_enabled`를 필수로 요구하거나, 그 부재만으로 추가 상세 조회·사용자 입력·수동 변경을 요구하지 않는다.

새 `welcome_message_enabled`는 실제 input schema와 상세 계약 모두에서 지원할 때 기존 값을 그대로 보존한다. 특히 false와 저장된 welcome text를 함께 유지하고 text가 있다고 true로 바꾸지 않는다. 새 MCP·구 O 혼합 상태에서 input schema에만 이 field가 있어도 상세에 없는 값을 추측하지 않는다. 활성화 true에 null/빈 문자열을 보내지 않는다.

구 상세의 여섯 설정이 모두 완전하게 확인됐다면 새 metadata가 없는 경우뿐 아니라, **이미 완료한 `get_ennoia_app` 상세 조회**에 `welcome_message_enabled=null`, `settings_field_states={}`, `settings_input_required=[]`, `settings_readiness=detail_required`가 함께 나타나는 경우도 기존 여섯 필드로 승인된 수정을 진행하고 새 flag는 생략한다. 이 조합은 새 MCP가 구 O 응답에 채우는 기본 metadata일 수 있다. 조합 자체만으로 새 flag 입력·상세 재조회·수동 변경을 요구하지 않는다. 목록 응답만 읽은 상태에는 이 예외를 적용하지 않는다.

이 호환 분기는 여섯 기존 설정이 모두 확인된 경우에만 적용한다. 누락·null·기본값 여부가 불명확한 설정을 임의 값으로 채워 완전한 여섯 필드로 만들지 않는다. `settings_field_states`에 실제 field의 `null`/`absent`가 명시되거나 `settings_input_required`가 비어 있지 않거나 readiness가 `explicit_input_required`/`builder_unavailable`이면 해당 guard를 우선한다. 단순 flag 값 null과 명시적 field-state의 null/absent를 혼동하지 않는다. 새 O의 명시적 guard를 위 기본 metadata 조합으로 취급하지 않는다.

생략된 유효 설정은 기본값으로 초기화될 수 있다. 이름만 바꾸더라도 설명·welcome·history·파일 업로드·추천 질문을 보존한다. 현재 계약에서 필요한 기존 값이 불명확해 전체 설정을 안전하게 재구성할 수 없으면 임의 기본값을 넣지 말고 아래 readiness 절차를 따른다. 저장 후 설정을 다시 조회해 요청 범위만 바뀌었는지 확인한다. 동시 수정 방지(CAS)가 없으므로 GET과 전체 PUT 사이의 다른 변경은 보장할 수 없다고 결과에 짧게 밝힌다.

목록 또는 아직 읽지 않은 상세의 `settings_readiness=detail_required`는 상세 조회 필요다. 이미 읽은 상세에는 위 호환 조건을 먼저 적용한다. `explicit_input_required`는 표시된 `settings_input_required`의 전체 교체 값을 사용자가 명시해야 함, `builder_unavailable`은 안전한 수정 경로 없음이다. `settings_field_states=absent|null|value`와 실제 값으로 보존 범위를 확인한다. `complete`도 GET→full PUT 사이의 동시 변경을 막지 않는다. legacy 이름만 입력은 여전히 전체 교체이며 생략한 유효 field도 defaults로 바뀐다. 이름만 보냈다고 다른 설정이 보존된 것으로 설명하지 않는다.

위 기본 metadata와 별개로, 보존해야 할 기존 설정 일부가 null 또는 불명확하면 안전하게 보존할 수 있는 공식 부분 변경 경로가 있는지 먼저 확인한다. 없다면 값의 임의 기본값이나 빈 값으로 전체 교체하지 않는다. 요청한 이름 변경은 설정 화면에서 수행하도록 안내한다.

App의 상세 조회에 나타나지 않는 credential은 채워 넣거나 유추하지 않는다. 선택한 App의 credential이 없으면 backend의 관리 경로를 사용한다.

쓰기 도구가 `operation_id`를 요구하면 하나의 논리적 변경에 같은 UUID를 사용한다. timeout 후 상태 조회를 먼저 하며 같은 요청에 새 ID를 만들지 않는다. 공유 링크는 의도적으로 공개 요청된 결과에만 전달한다. API key·OAuth token·업로드 ticket은 공유 링크가 아니다.
