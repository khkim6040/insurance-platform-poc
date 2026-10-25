# 실험 5: 공통 HTTP 변경 (Correlation Filter 응답 헤더 추가)

## 시나리오와 성공 기준

플랫폼의 `CorrelationIdFilter`가 응답 헤더 `X-Correlation-Source`(`generated` | `propagated`)를 하나 더 내보내도록 바꾸고 세 contract에 전파한다. 성공 기준: 각 contract의 api를 띄워 curl로 두 값을 모두 확인. 플랫폼 버전 `v1.2.0`. 플랫폼 측 변경은 세 안에서 바이트 단위로 같은 3파일(`CorrelationId.kt` 상수 1줄, `CorrelationIdFilter.kt` 2줄, 스타터 테스트 단언 2줄)이다.

## 결과

| 항목 | A | B | C |
|---|---|---|---|
| 플랫폼 측 수동 단계 수 (목록) | 3: ① 스타터 3파일 수정 ② PR → CI → 머지 ③ 태그 `v1.2.0`(참조용, 트리거 없음) | 4: ① 같은 3파일 ② PR → CI → 머지 ③ 태그 `v1.2.0` ④ publish 완료 대기(구조적 대기 1) | 4: 같음 |
| 프로젝트 측 수동 단계 수, 프로젝트 1개당 (목록) | 1: `fetch upstream` + `merge upstream/main` → push → CI. 손댄 파일 0(들어온 파일 3, +6/-1) | 1: `gradle.properties` 1줄 → push → CI. 손댄 파일 1 | 1: 같음 |
| 머지 충돌 파일 수 | 0 (실험 2·3의 프로젝트 소유 변경 11파일과 겹치지 않음) | 0 (머지 없음) | 0 |
| 의미적 충돌 (빌드·테스트 실패, 동작 변화) | 없음. `build` 통과 | 없음. `build` 통과(1.2.0 다운로드) | 없음 |
| 함께 끌려온 무관한 변경 수 | 0 (upstream 커밋 2개 = 이 변경 + PR 머지 커밋) | 0 (`1.2.0` = 이 변경만) | 0 |
| 검증 방법과 결과 | api 기동 후 curl: 헤더 없음 → `X-Correlation-Source: generated`, `X-Correlation-Id: exp5` → `X-Correlation-Id: exp5` + `X-Correlation-Source: propagated` | 같음 (`platform-http-starter:1.2.0`) | 같음 (`cplatform:platform-http-starter:1.2.0`) |
| 에이전트 개입 (사람 결정·행동이 필요했던 지점) | 0 | 0 | 0 |

## 근거: 커밋 SHA, PR, CI 실행 링크

- A 플랫폼 PR https://github.com/khkim6040/demo-a-platform/pull/2 (머지 `2397591` = `v1.2.0`), 브랜치 CI https://github.com/khkim6040/demo-a-platform/actions/runs/40149709138, main CI https://github.com/khkim6040/demo-a-platform/actions/runs/40149712230; contract 머지 커밋 `bdc330c`, CI https://github.com/khkim6040/demo-a-contract/actions/runs/40149856798
- B 플랫폼 PR https://github.com/khkim6040/demo-b-platform/pull/2 (머지 `6b3bb08` = `v1.2.0`), publish https://github.com/khkim6040/demo-b-platform/actions/runs/40149730157; contract 커밋 `f527494`, CI https://github.com/khkim6040/demo-b-contract/actions/runs/40149993079
- C 플랫폼 PR https://github.com/khkim6040/demo-c-platform/pull/2 (머지 `6a96770` = `v1.2.0`), publish https://github.com/khkim6040/demo-c-platform/actions/runs/40149743688; contract 커밋 `a8e3ec7`, CI https://github.com/khkim6040/demo-c-contract/actions/runs/40150090152

## 관찰: 잘못하기 쉬운 지점, 자동화할 수 있는 단계

- 실험 4와 구조가 같다. 플랫폼 측 파일 수·내용은 세 안 동일(3파일)이고, 차이는 전달 경로만이다: A는 머지(대기 0, 프로젝트 손댄 파일 0), B/C는 퍼블리시 대기 1 + 숫자 1줄. 코드 변경이든 의존성 변경이든 전파 비용의 형태가 같다는 뜻이다.
- B/C는 `platformVersion`만 1.2.0으로 올리고 `release.yml`의 `@v`는 `v1.0.0`에 남겼다. 워크플로 변경이 없으므로 올릴 이유가 없고, 두 숫자가 어긋난 상태는 이번에도 아무 영향이 없다.
- A는 머지가 가져온 3파일이 모두 `platform/**`(upstream 소유)이라 충돌 후보가 없었다. 프로젝트가 규약을 지키는 동안 A의 머지는 실질적으로 "pull"이다.
- 세 플랫폼의 스타터 모듈 경로가 다르다(A `platform/http-starter`, B/C `platform-http-starter`). 같은 변경을 세 번 적용할 때 경로 매핑이 유일한 차이였다.
- 도구 관찰(측정 외): `gh pr checks --watch`는 PR 생성 직후 체크가 아직 등록되지 않으면 "no checks reported"로 즉시 반환해 CI 완료 전에 머지가 일어날 수 있다. 세 PR의 브랜치 CI와 main CI는 모두 성공했으나, 이후 PR부터는 체크 등록을 기다리도록 보조 함수를 고쳤다.
