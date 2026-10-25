# 실험 6: 커스터마이징 (contract의 기본값 변경과 플랫폼의 같은 값 변경)

## 시나리오와 성공 기준

1단계: contract가 HTTP 클라이언트 read-timeout 기본값 5s를 3s로 바꾼다. A는 스타터의 `platform/http-starter/src/main/resources/platform-defaults.yml`을 직접 고친다(스펙 5.4 소유권 규약의 의도적 위반). B/C는 플랫폼 파일이 아티팩트 안에 있어 `apps/api/src/main/resources/application.yml`에만 쓸 수 있다. 2단계: 플랫폼이 같은 기본값을 4s로 바꿔 `v1.3.0`을 낸다. 측정: A의 충돌 파일 수. 검증: 지연 스텁(`STUB_DELAY_MS`)으로 3.5s 지연 시 500, 2.5s 지연 시 200.

변경 전 기준점(A, 코드는 세 안 동일): 5s 기본값에서 3.5s 지연 → `200 3.58s`, 6s 지연 → `500 5.05s`. `spring.http.clients.read-timeout`이 auto-configured `RestClient.Builder`에 실제로 적용된다.

## 결과

| 항목 | A | B | C |
|---|---|---|---|
| 플랫폼 측 수동 단계 수 (목록) | 3: ① `platform-defaults.yml` 1줄 ② PR → CI → 머지 ③ 태그 `v1.3.0` | 4: ①~③ 같음 ④ publish 대기 | 4: 같음 |
| 프로젝트 측 수동 단계 수, 프로젝트 1개당 (목록) | 1단계 1: 스타터 yml 1줄 → push → CI. 2단계 1: `merge upstream/main` → **충돌 해소**(`checkout --ours`, `add`, `commit`) → push → CI. 손댄 파일 1 + 해소 1 | 1단계 1: api `application.yml` 3줄 → push → CI. 2단계 1: `gradle.properties` 1줄 → push → CI. 손댄 파일 2 | 같음 |
| 머지 충돌 파일 수 | **1** (`platform/http-starter/src/main/resources/platform-defaults.yml`, 같은 줄 `3s` vs `4s`) | 0 (머지 없음) | 0 |
| 의미적 충돌 (빌드·테스트 실패, 동작 변화) | 빌드·테스트 통과. 플랫폼의 4s 의도는 해소 시 버려져 A contract 안에 흔적이 없다(머지 커밋에만 남음) | 없음. 아티팩트(1.3.0 jar) 안은 4s, 앱 yml은 3s로 둘 다 보존 | 같음 |
| 함께 끌려온 무관한 변경 수 | 0 | 0 | 0 |
| 검증 방법과 결과 | 1단계 후 3.5s → `500 3.05s`, 2.5s → `200 2.58s`. 2단계(해소) 후 3.5s → `500 3.05s` | 1단계 후 3.5s → `500 3.05s`. 2단계 후 `500 3.04s`. `platform-http-starter-1.3.0.jar`의 yml `read-timeout: 4s` | 1단계 `500 3.06s`, 2단계 `500 3.04s`. `cplatform` 1.3.0 jar `4s` |
| 에이전트 개입 (사람 결정·행동이 필요했던 지점) | 0 (충돌 해소 정책 "프로젝트 값 유지"는 계획에 사전 결정) | 0 | 0 |

## 근거: 커밋 SHA, PR, CI 실행 링크

- A: 위반 커밋 `e85165e` CI https://github.com/khkim6040/demo-a-contract/actions/runs/40150247439; 플랫폼 PR https://github.com/khkim6040/demo-a-platform/pull/3 (머지 `536e6f2` = `v1.3.0`, PR CI https://github.com/khkim6040/demo-a-platform/actions/runs/40150492569); 충돌 해소 머지 커밋 `45a1dbb` CI https://github.com/khkim6040/demo-a-contract/actions/runs/40150777157
- B: yml 커밋 `7e0c890` CI https://github.com/khkim6040/demo-b-contract/actions/runs/40150340968; 플랫폼 PR https://github.com/khkim6040/demo-b-platform/pull/3 (머지 `a8a6fc2` = `v1.3.0`), publish https://github.com/khkim6040/demo-b-platform/actions/runs/40150627275; bump 커밋 `549c4ca` CI https://github.com/khkim6040/demo-b-contract/actions/runs/40150863153
- C: yml 커밋 `29e53cc` CI https://github.com/khkim6040/demo-c-contract/actions/runs/40150401987; 플랫폼 PR https://github.com/khkim6040/demo-c-platform/pull/3 (머지 `b878f3b` = `v1.3.0`), publish https://github.com/khkim6040/demo-c-platform/actions/runs/40150702733; bump 커밋 `c798e83` CI https://github.com/khkim6040/demo-c-contract/actions/runs/40150970944

## 관찰: 잘못하기 쉬운 지점, 자동화할 수 있는 단계

- A의 위반은 한 줄이었지만 그 파일은 이후 모든 upstream 머지에서 충돌 후보로 남는다. 플랫폼이 그 파일을 건드릴 때마다(이번처럼 같은 줄이면 반드시) 프로젝트가 해소해야 한다. 규약을 지켰다면(`application.yml`에 3s) A도 B/C와 같이 충돌 0이었다. A의 비용은 규약 준수 여부에 전적으로 달려 있다.
- `--ours`로 해소하면 플랫폼의 4s 의도가 소리 없이 사라진다. 리뷰어가 머지 커밋의 충돌 diff를 보지 않으면 "플랫폼이 4s로 조였다"는 사실을 contract 쪽 누구도 모른다. B/C는 아티팩트에 4s가 그대로 있고 프로젝트 오버라이드가 별도 파일에 명시되어 두 의도가 모두 읽힌다.
- B/C는 구조적으로 위반이 불가능하다. 플랫폼 파일이 jar 안에 있어 고칠 수 없고, 유일한 길이 앱 프로퍼티다. "규약"이 아니라 "구조"가 경계를 지킨다.
- 결과(유효 3s)는 세 안이 같다. 차이는 그 상태에 도달하는 비용(A 충돌 1)과 상태의 가독성(B/C는 오버라이드가 프로젝트 파일에 있음)이다.
- 스타터 테스트 `platform defaults apply with lowest precedence`는 read-timeout을 9s로 덮어쓰고 검사하므로 기본값이 5s → 3s → 4s로 바뀌어도 잡지 못한다. 기본값 자체를 단언하는 테스트가 없어서 A의 위반 커밋도, 플랫폼의 변경도 테스트 실패 없이 통과했다. 기본값을 보호하려면 별도 테스트가 필요하다(세 안 공통).
- 타임아웃 500의 원인(`ResourceAccessException`)에 핸들러 매핑이 없어 Boot 기본 ProblemDetail 500으로 떨어진다. 실험 목적에는 충분하지만 운영이라면 504 매핑이 스타터에 들어갈 후보다.
