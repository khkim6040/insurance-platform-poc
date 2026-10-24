# 실험 4: 보안 패치 (전이 의존성 강제)

## 시나리오와 성공 기준

Spring Boot 4.1.2가 고정한 Jackson 3.1.7(`jackson-core`, `jackson-databind`, `jackson-module-kotlin`)을 3.1.8로 강제한다. `tools.jackson:jackson-bom:3.1.8`을 플랫폼으로 import해 세 모듈을 한 번에 올린다. 성공 기준: 세 contract의 네 앱 `runtimeClasspath`에서 Jackson이 3.1.8. 플랫폼 변경과 프로젝트 반영 모두 실제 PR.

패치 대상 선정: 세 contract의 api 런타임 의존성 48개를 Maven Central `maven-metadata.xml`과 대조한 결과, 같은 major.minor 안에 더 새 패치가 있는 것은 Jackson(3.1.7 → 3.1.8)만이었다. Tomcat 11.0.27, Logback 1.5.38 등은 Boot가 이미 최신 패치를 고정하고 있었다.

변경 전: api·admin 3.1.7 세 모듈 / consumer·batch에는 Jackson 없음(세 안 동일).

## 결과

| 항목 | A | B | C |
|---|---|---|---|
| 플랫폼 측 수동 단계 수 (목록) | 3: ① `libs.versions.toml` 2줄 + 컨벤션 플러그인 1줄(2파일) ② PR → CI → 머지 ③ 태그 `v1.1.0`(참조용, 트리거 없음) | 4: ① `libs.versions.toml` 2줄 + `platform-bom` 1줄(2파일) ② PR → CI → 머지 ③ 태그 `v1.1.0` ④ publish 완료 대기(구조적 대기 1) | 4: 같음 |
| 프로젝트 측 수동 단계 수, 프로젝트 1개당 (목록) | 1 PR: `fetch upstream` + `merge upstream/main` → push → CI → 머지. 손댄 파일 0(머지 커밋만, upstream 변경 2파일이 들어옴) | 1 PR: `gradle.properties` 1줄 → push → CI → 머지. 손댄 파일 1 | 1 PR: 같음 |
| 머지 충돌 파일 수 | 0 (실험 2의 프로젝트 소유 변경 8파일 + 실험 3의 3파일과 upstream 소유 변경 2파일이 겹치지 않음) | 0 (머지 없음) | 0 |
| 의미적 충돌 (빌드·테스트 실패, 동작 변화) | 없음. `build` 통과 | 없음. `build` 통과(1.1.0 패키지 다운로드) | 없음 |
| 함께 끌려온 무관한 변경 수 | 0 (upstream 커밋 2개 = 이 패치 커밋 + PR 머지 커밋) | 0 (`1.1.0` = 이 패치만) | 0 |
| 검증 방법과 결과 | 네 앱 `dependencies --configuration runtimeClasspath`: api·admin 세 모듈 `3.1.7 -> 3.1.8`, consumer·batch 없음(변경 전과 같음) | 같음. `platform-bom:1.1.0` pom에 `jackson-bom` import 1 | 같음 |
| 에이전트 개입 (사람 결정·행동이 필요했던 지점) | 0 | 0 | 0 |

## 근거: 커밋 SHA, PR, CI 실행 링크

- A 플랫폼 PR https://github.com/khkim6040/demo-a-platform/pull/1 (커밋 `9197fea`, 머지 `b99f894` = `v1.1.0`), PR CI https://github.com/khkim6040/demo-a-platform/actions/runs/40105222172; contract PR https://github.com/khkim6040/demo-a-contract/pull/2 (머지 `6d1fdf7`), CI https://github.com/khkim6040/demo-a-contract/actions/runs/40105781281
- B 플랫폼 PR https://github.com/khkim6040/demo-b-platform/pull/1 (머지 `30735e0` = `v1.1.0`), publish https://github.com/khkim6040/demo-b-platform/actions/runs/40105511148; contract PR https://github.com/khkim6040/demo-b-contract/pull/1 (머지 `c6e5416`), CI https://github.com/khkim6040/demo-b-contract/actions/runs/40106012181
- C 플랫폼 PR https://github.com/khkim6040/demo-c-platform/pull/1 (머지 `741125e` = `v1.1.0`), publish https://github.com/khkim6040/demo-c-platform/actions/runs/40105625814; contract PR https://github.com/khkim6040/demo-c-contract/pull/1 (머지 `04a0959`), CI https://github.com/khkim6040/demo-c-contract/actions/runs/40106156661

## 관찰: 잘못하기 쉬운 지점, 자동화할 수 있는 단계

- 수단은 셋 다 "BOM을 하나 더 import"이고 Gradle이 높은 버전을 택한다. 플랫폼 측 파일 수는 같다(2). 차이는 전달: A는 git 머지(대기 0, 프로젝트가 손대는 파일 0), B/C는 퍼블리시(대기 1, 이번 실행에서 태그 push → 패키지 200까지 약 1분) + 숫자 1줄.
- B/C는 `platformVersion`만 올리고 `release.yml`의 `@v`는 `v1.0.0`에 남겼다. 아티팩트와 워크플로가 다른 버전을 가리키는 상태가 정상 운영에서 생긴다. 이것이 문제가 되는지는 실험 7(워크플로 변경)에서 본다.
- A는 upstream 머지가 프로젝트 변경(실험 2·3, 11파일)과 충돌하지 않았다. 소유권 규약이 지켜지는 동안 A의 전파 비용은 "머지 PR 하나"다.
- Boot가 이미 최신 패치를 고정한 라이브러리(Tomcat, Logback)는 강제할 패치가 없었다. 패치 대상을 찾는 일 자체가 플랫폼 측 작업이며, 세 안 공통.
- `dependencies` 출력의 `(c)`(constraint)와 `->`(치환) 표기를 확인하지 않으면 BOM이 적용된 줄 알고 넘어가기 쉽다.
- B/C contract PR의 CI는 플랫폼 publish가 끝난 뒤에만 통과한다. 플랫폼 PR 머지 → 태그 → publish 성공 확인 → contract PR 순서를 지켜야 하며, 이 순서 의존이 A에는 없다.
