# 실험 3: 독립 배포

## 시나리오와 성공 기준

api만 수정(`QuoteResponse.rate` 추가, 2파일), `deploy/overlays/dev`의 api 이미지 태그를 1.1.0으로 올리고 `api-v1.1.0` 태그를 push한다. 성공 기준: CI가 api 이미지만 빌드·푸시하고(admin 등은 안 만들어짐), 매니페스트 커밋 revert만으로 롤백된다(CI는 레포에 커밋을 쓰지 않음). 세 contract에서 수행.

## 결과

| 항목 | A | B | C |
|---|---|---|---|
| 플랫폼 측 수동 단계 수 (목록) | 0 | 0 | 0 |
| 프로젝트 측 수동 단계 수, 프로젝트 1개당 (목록) | 3: ① api 코드 커밋(2파일) ② overlay `newTag` 커밋(1파일) + 태그 push ③ 롤백 = revert 커밋 | 3: 같음 | 3: 같음 |
| 머지 충돌 파일 수 | 0 | 0 | 0 |
| 의미적 충돌 (빌드·테스트 실패, 동작 변화) | 없음 | 없음 | 없음 |
| 함께 끌려온 무관한 변경 수 | 0 | 0 | 0 |
| 검증 방법과 결과 | release 로그에 `Task :apps:api:bootJar`만, `api:1.1.0` 존재·`admin:1.1.0` 부재, revert 후 kustomize 렌더 네 이미지 전부 `0.1.0`, revert 후 release 실행 수 2로 불변(CI 녹색) | 같음 (reusable `demo-b-platform/release-app.yml@v1.0.0` 경로) | 같음 (`demo-c-platform/release-app.yml@v1.0.0` 경로) |
| 에이전트 개입 (사람 결정·행동이 필요했던 지점) | 0 | 0 | 0 |

## 근거: 커밋 SHA, PR, CI 실행 링크

- A: 코드 `feb4473`, 매니페스트 `69d9646`, revert `59cf94c`, release https://github.com/khkim6040/demo-a-contract/actions/runs/40104898197, revert 후 ci https://github.com/khkim6040/demo-a-contract/actions/runs/40105057437
- B: 코드 `a66ea4f`, 매니페스트 `2f38e43`, revert `ab3c7a1`, release https://github.com/khkim6040/demo-b-contract/actions/runs/40104901633, revert 후 ci https://github.com/khkim6040/demo-b-contract/actions/runs/40105060300
- C: 코드 `6133556`, 매니페스트 `b092a5e`, revert `e379a8a`, release https://github.com/khkim6040/demo-c-contract/actions/runs/40104905248, revert 후 ci https://github.com/khkim6040/demo-c-contract/actions/runs/40105062509

## 관찰: 잘못하기 쉬운 지점, 자동화할 수 있는 단계

- 세 안의 차이는 릴리스 단계가 어디 있느냐(A 레포 안, B/C 플랫폼 reusable)뿐이고, 프로젝트 측 절차와 결과는 같다. 독립 배포는 태그 규칙 `<app>-v<ver>` + `:apps:<app>:bootJar`라는 Phase 1 설계가 결정하며 플랫폼 구조와 무관하다.
- 롤백은 매니페스트 revert이고 이미지·태그는 남는다. 같은 버전을 다시 태그하면 release가 다시 돌아 이미지를 덮어쓴다(태그 재사용 금지 규칙이 필요).
- `newTag`를 올릴 때 다른 앱 항목을 잘못 건드리기 쉽다. A안 overlay는 `newName`이 끼어 있어 B/C와 줄 구조가 다르다(이번에는 정규식을 두 구조 모두 맞게 썼다). 네 앱의 `newTag`가 한 파일에 있어 diff 리뷰로 잡는다.
- 코드 커밋과 매니페스트 커밋을 분리했으므로 revert가 코드를 건드리지 않는다. 한 커밋에 섞으면 revert가 코드까지 되돌린다.
