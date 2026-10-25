# 실험 10: 신규 공통 기능 (관측성·복원력 스타터 → contract·claims 전파)

## 시나리오와 성공 기준

플랫폼이 `observability-starter`(Actuator, Micrometer Prometheus, Boot 4.1 `spring-boot-starter-opentelemetry`, 기본 프로퍼티)와 `resilience-starter`(`resilience4j-spring-boot4` 2.4.0 CB·Retry 기본 설정)를 추가해 `v1.6.0`으로 내고, contract·claims 여섯 프로젝트가 받는다. 스펙 5.4가 예상한 충돌 지점(프로젝트의 의존성 추가 vs 플랫폼의 스타터 추가)을 실제로 만들기 위해 세 contract는 먼저 `apps/api/build.gradle.kts`에 `commons-lang3` 한 줄을 넣었다(A에서는 소유권 규약 위반이지만 스펙이 명시한 측정 지점). claims는 손대지 않은 프로젝트의 경로다. 측정은 관측성으로 한다: `/actuator/health` 200, `/actuator/prometheus`의 `http_server_requests`에 `application="api"` 태그, `/actuator/circuitbreakers` 200, 요청 범위 로그 줄에 `[traceId-spanId]`, OTLP 내보내기 오류 0.

`resilience4j-spring-boot4` 2.4.0은 Boot 4.1.2에서 그대로 동작했다(스타터 테스트: Retry 3회, CB 5콜 후 OPEN). 스펙 8장의 대체안(`@Retryable`만)은 쓰지 않았다.

## 결과

| 항목 | A | B | C |
|---|---|---|---|
| 플랫폼 측 수동 단계 수 (목록) | 3: ① 스타터 2모듈 + toml·settings·api·admin·README(17파일, +211줄) ② PR → CI → 머지 ③ 태그 `v1.6.0` | 5: ① 스타터 2모듈 + toml·settings·BOM·카탈로그(16파일, +228줄) ② PR → CI → 머지 ③ 태그 ④ publish 대기 ⑤ **템플릿 레포** 4파일(핀 2 + api·admin 배선) → push → CI | 4: ① 스타터 2모듈 + toml·settings·BOM·카탈로그 + 템플릿 4파일(20파일, +233/−2줄) ② PR → CI → 머지 ③ 태그 ④ publish 대기 |
| 프로젝트 측 수동 단계 수, 프로젝트 1개당 (목록) | contract **3**: ① v1.5.0 revert의 revert ② `fetch tag` + `merge v1.6.0` + 충돌 **2**파일 해소 ③ push → CI. 손댄 파일 2, 들어온 파일 16(+209줄). claims **1**: 머지 + 충돌 **1**파일(README) 해소 → push → CI. 손댄 파일 1 | contract **1**: `gradle.properties` 1줄 + api 2줄 + admin 1줄 → push → CI. 손댄 파일 3. claims 1, 손댄 파일 3 | B와 같음 |
| 머지 충돌 파일 수 | contract **2**: `apps/api/build.gradle.kts`(예상. 같은 자리에 프로젝트 1줄 vs 플랫폼 2줄, 양쪽 유지) + `README.md`(**예상 밖**. 플랫폼이 프로젝트 소유 파일에 줄을 더함, 프로젝트 쪽 유지). claims **1**: `README.md`(같은 원인. 빌드 파일은 깨끗히 들어옴) | 0 (앱 빌드 파일·README는 프로젝트 소유, 플랫폼은 건드리지 않음) | 0 |
| 의미적 충돌 (빌드·테스트 실패, 동작 변화) | 없음. graceful 기본값이 재올림으로 돌아옴(의도). 충돌을 `--ours`로 풀었다면 스타터가 빠진 채 빌드가 통과하는 의미적 충돌이 됐을 것 | 없음. 1.3.0 → 1.6.0 점프로 graceful 기본값이 들어옴(실험 8에서 되돌린 것) | B와 같음 |
| 함께 끌려온 무관한 변경 수 | contract: v1.5.0 재적용 1(graceful). claims 0 | contract 1 (graceful, 1.4.0·1.5.0 건너뜀). claims 0 | B와 같음 |
| 검증 방법과 결과 | contract: `clean build` 테스트 33, runtimeClasspath에 두 스타터, probe `health 200 / prom-app-tag 2 / cb 200 / traced-log-lines 29 / export-errors 0`, `read-timeout: 3s` 유지 + `shutdown: graceful` 복귀, CI ok. claims: 테스트 30, deps 둘 다, `health 200 / prom-app-tag 2 / cb 200 / export-errors 0`, CI ok | contract: 테스트 20, deps `platform-observability-starter:1.6.0`·`platform-resilience-starter:1.6.0`(→ `resilience4j-spring-boot4:2.4.0`), probe A와 같음(29줄), CI ok. claims: 테스트 20, probe 같음, CI ok | B와 같음(`cplatform:…:1.6.0`) |
| 에이전트 개입 (사람 결정·행동이 필요했던 지점) | 0 | 0 | 0 |

플랫폼 측 스타터 테스트: A 플랫폼 전체 테스트 25 → 30(관측성 2, 복원력 3). 샘플 api 로컬 probe `health 200 / prom-app-tag 2 / cb 200 / traced-log-lines 29 / export-errors 0`.

## 근거: 커밋 SHA, PR, CI 실행 링크

- 사전(contract `commons-lang3`): `demo-a-contract` `60b9f45` (CI https://github.com/khkim6040/demo-a-contract/actions/runs/40157827838), `demo-b-contract` `a0b5ac5` (https://github.com/khkim6040/demo-b-contract/actions/runs/40157829851), `demo-c-contract` `903bb11` (https://github.com/khkim6040/demo-c-contract/actions/runs/40157831454)
- 플랫폼 A: PR #6 (`371c626` 스타터, `b42cd9c` 배선) → `37ae1af` = `v1.6.0`, CI https://github.com/khkim6040/demo-a-platform/actions/runs/40158262575
- 플랫폼 B: PR #6 → `7c32896` = `v1.6.0`, publish https://github.com/khkim6040/demo-b-platform/actions/runs/40158562286; `demo-b-template` `c7c719a` (CI https://github.com/khkim6040/demo-b-template/actions/runs/40158713798)
- 플랫폼 C: PR #6 → `b91fe02` = `v1.6.0`, publish https://github.com/khkim6040/demo-c-platform/actions/runs/40158982354
- contract A: `b37bd75` Reapply v1.5.0, `55ee560` Merge tag v1.6.0 (CI https://github.com/khkim6040/demo-a-contract/actions/runs/40159254365); B `35fcba4` (https://github.com/khkim6040/demo-b-contract/actions/runs/40159256196); C `bc4600f` (https://github.com/khkim6040/demo-c-contract/actions/runs/40159257846)
- claims A: `8dc2e88` Merge tag v1.6.0 (CI https://github.com/khkim6040/demo-a-claims/actions/runs/40159561733); B `f54f677` (https://github.com/khkim6040/demo-b-claims/actions/runs/40159563049); C `363fde3` (https://github.com/khkim6040/demo-c-claims/actions/runs/40159565327)
- 계획: `docs/superpowers/plans/2026-10-25-phase6-observability-resilience-exp10.md`

## 관찰: 잘못하기 쉬운 지점, 자동화할 수 있는 단계

- **A의 충돌은 예상 1파일이 아니라 2파일이었다.** 플랫폼 PR이 자기 README에 스타터 두 줄을 더했는데, README는 규약상 프로젝트 소유 파일이다. 그 결과 프로젝트가 빌드 파일을 건드리지 않은 claims에도 충돌 1이 났다. A에서는 플랫폼이 프로젝트 소유 파일을 한 줄만 고쳐도 모든 하위 프로젝트에 충돌이 전파된다. 규약을 플랫폼 CI가 강제하지 않으면(예: `README.md`·`apps/*/src/**` 변경 시 PR 실패) 사람이 기억에 의존해야 한다. B/C에는 이 문제가 구조적으로 없다.
- A: `apps/api/build.gradle.kts` 충돌의 해소 정책을 미리 정하지 않았다면 `--ours`(스타터 소실)·`--theirs`(프로젝트 의존성 소실) 어느 쪽도 빌드는 통과한다. 조용한 의미적 충돌이다.
- A: 되돌린 머지 위에 다음 버전을 머지하면 되돌린 내용은 돌아오지 않는다(실험 8 함정 재확인). 재올림에 revert-of-revert 1단계가 추가로 들었다.
- A는 플랫폼이 앱 빌드 파일을 소유하므로 새 스타터가 머지로 **자동 적용**된다(claims 빌드 파일 손댄 0). B/C는 **opt-in**이라 프로젝트가 앱마다 한 줄을 적는다(손댄 파일 3). 전파 비용은 B/C가 더 들지만 적용 범위(어느 앱에 넣을지)를 프로젝트가 고른다. 플랫폼이 BOM·카탈로그에 별칭을 올리는 것만으로는 아무 프로젝트에도 들어가지 않는다.
- B/C: 템플릿 배선은 새 프로젝트에만 영향을 준다. 기존 프로젝트(contract·claims)에는 아무 효과가 없다. B는 publish 뒤 별도 레포에서 핀을 올려야 하는 순서 의존이 이번에도 있었다(실험 8과 같음).
- 스타터 작성 중 에이전트가 스스로 고친 것 두 가지(개입 아님): ① Kotlin 스타터는 `kotlin-reflect`와 `spring-boot-starter`를 `api`로 가져가야 Boot가 `EnvironmentPostProcessor`를 인스턴스화한다(`resilience4j-spring-boot4`는 Boot 모듈을 runtime scope로만 가져옴). `http-starter`가 이미 그렇게 하고 있었다. ② Boot 4의 로그 상관관계 필드는 `[traceId-spanId]` 49자 고정폭이며, 환경변수로 넘긴 로거 이름은 소문자로 바인딩되므로 로그 그룹 `web`(`LOGGING_LEVEL_WEB=DEBUG`)을 써야 한다.
- 관측성 기본값은 http-starter와 독립된 yml·프로세서로 두어 세 기본값 파일이 키를 공유하지 않는다. 공유하면 `addLast` 순서(= spring.factories 로드 순서)가 승자를 정해 추적이 어렵다. OTLP 메트릭 내보내기는 기본값에서 꺼 두어야 수집기 없는 환경에서 오류 로그가 나지 않는다(`export-errors 0`으로 확인).
