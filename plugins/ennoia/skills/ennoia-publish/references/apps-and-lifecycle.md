# App과 lifecycle

| 사용자 요청 | 도구와 확인 |
| --- | --- |
| App 찾기 | `list_ennoia_apps` → exact `assistant_hash` → 필요한 경우 `get_ennoia_app` |
| App 생성 | 사용 가능한 배포를 확인한 뒤 `create_ennoia_app`; 생성이 에이전트 배포를 대신하지 않는다. |
| App 변경 | 현재 설정을 읽고 `update_ennoia_app`으로 요청한 field만 변경 |
| 복제 | `clone_ennoia_app` 후 새 ID 확인. 공유 설정까지 동일하게 복제됐다고 가정하지 않는다. |
| 공개 링크 생성·활성화·비활성화·철회 | `share_ennoia_app`의 `action=create/enable/disable/revoke`; 요청한 공개 범위만 적용 |
| App 삭제 | `delete_ennoia_app`; 에이전트나 전체 배포까지 삭제하지 않는다. |
| 에이전트 이름 변경·복제·삭제 | `rename_multi_agent`, `clone_multi_agent`, `delete_multi_agent`; exact ID와 영향 범위 확인 |
| 배포 중지·삭제 | `stop_multi_agent_deployment`, `delete_multi_agent_deployment`; 버전과 선행 실행 상태 확인 |

App의 상세 조회에 나타나지 않는 credential은 채워 넣거나 유추하지 않는다. 선택한 App의 credential이 없으면 backend의 관리 경로를 사용한다.

쓰기 도구가 `operation_id`를 요구하면 하나의 논리적 변경에 같은 UUID를 사용한다. timeout 후 상태 조회를 먼저 하며 같은 요청에 새 ID를 만들지 않는다. 공유 링크는 의도적으로 공개 요청된 결과에만 전달한다. API key·OAuth token·업로드 ticket은 공유 링크가 아니다.
