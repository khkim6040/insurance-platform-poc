# 실험 7: CI/Docker 변경 (베이스 이미지 태그)

## 시나리오와 성공 기준

플랫폼 Dockerfile의 베이스를 `eclipse-temurin:25-jre`(Ubuntu) → `eclipse-temurin:25-jre-alpine`으로 바꾸고(`v1.4.0`) 세 contract의 `api-v1.2.0` 릴리스가 새 베이스로 이미지를 만드는지 본다. A는 머지, B/C는 `release.yml`의 `@v`만 올린다(`platformVersion`은 1.3.0에 그대로 둠). 성공 기준: release CI 통과, 이미지의 `/etc/os-release`가 Alpine. 매니페스트(`newTag`)는 올리지 않는다(실험 3에서 검증한 절차와 같고, 여기서는 이미지 생성 경로만 본다).

## 결과

| 항목 | A | B | C |
|---|---|---|---|
| 플랫폼 측 수동 단계 수 (목록) | 3: ① Dockerfile 1줄 ② PR → CI → 머지 ③ 태그 `v1.4.0` | 4: ①~③ 같음 ④ publish 대기(Dockerfile만 바뀌었는데 Maven 아티팩트 1.4.0도 함께 퍼블리시됨) | 4: 같음 |
| 프로젝트 측 수동 단계 수, 프로젝트 1개당 (목록) | 2: ① `merge upstream/main` → push → CI ② 태그 `api-v1.2.0` → release. 손댄 파일 0(들어온 파일 1) | 2: ① `release.yml` 1줄(`@v1.0.0` → `@v1.4.0`) → push ② 태그 → release. 손댄 파일 1 | 같음 |
| 머지 충돌 파일 수 | 0 (실험 6의 위반 파일과 겹치지 않음) | 0 | 0 |
| 의미적 충돌 (빌드·테스트 실패, 동작 변화) | 없음 | 없음. `platformVersion=1.3.0` / `@v1.4.0` 어긋남은 1.4.0 아티팩트 내용 = 1.3.0이라 영향 없음 | 같음 |
| 함께 끌려온 무관한 변경 수 | 0 | 0 (워크플로 측). 단 Maven 1.4.0은 내용 변화 없는 산출물 3개 | 같음 |
| 검증 방법과 결과 | `api:1.2.0` `Alpine Linux v3.24`, `api:1.1.0` `Ubuntu 26.04.1 LTS`. 크기 141.0MB → 99.1MB | `api:1.2.0` `Alpine Linux v3.24` (reusable workflow가 `demo-b-platform`을 `v1.4.0`로 checkout) | `api:1.2.0` `Alpine Linux v3.24` |
| 에이전트 개입 (사람 결정·행동이 필요했던 지점) | 0 | 0 | 0 |

## 근거: 커밋 SHA, PR, CI 실행 링크

- A 플랫폼 PR https://github.com/khkim6040/demo-a-platform/pull/4 (머지 `b253092` = `v1.4.0`, PR CI https://github.com/khkim6040/demo-a-platform/actions/runs/40151124101); contract 머지 `71d7069` CI https://github.com/khkim6040/demo-a-contract/actions/runs/40151366050, release https://github.com/khkim6040/demo-a-contract/actions/runs/40151418737, 이미지 `api:1.2.0` digest `sha256:6f77ac7fd4ed…` (`1.1.0` `sha256:7cbb34f9e1bb…`)
- B 플랫폼 PR https://github.com/khkim6040/demo-b-platform/pull/4 (머지 `6c44310` = `v1.4.0`), publish https://github.com/khkim6040/demo-b-platform/actions/runs/40151237555; contract 커밋 `b466b27`, release https://github.com/khkim6040/demo-b-contract/actions/runs/40151552804, digest `sha256:9f083ab40134…`
- C 플랫폼 PR https://github.com/khkim6040/demo-c-platform/pull/4 (머지 `d62961e` = `v1.4.0`), publish https://github.com/khkim6040/demo-c-platform/actions/runs/40151287056; contract 커밋 `2be0954`, release https://github.com/khkim6040/demo-c-contract/actions/runs/40151620671, digest `sha256:aa069ce68e38…`

## 관찰: 잘못하기 쉬운 지점, 자동화할 수 있는 단계

- B/C에서 `@v`를 올리지 않으면 릴리스는 성공하면서 옛 Dockerfile(Ubuntu)을 쓴다. 실패가 아니라 조용한 미반영이다. 실험 4~6에서 `platformVersion`만 올리고 `@v1.0.0`을 방치한 상태가 바로 그 조건이었다(당시엔 플랫폼 Dockerfile도 아직 Ubuntu여서 실해가 없었을 뿐이다). A는 머지 하나로 코드·빌드 설정·Dockerfile·워크플로가 함께 오므로 이런 종류의 누락이 없다.
- 플랫폼 태그 하나가 두 채널(Maven 아티팩트, reusable workflow)을 동시에 낸다. Dockerfile만 바꿔도 Maven 1.4.0이 퍼블리시되고, 반대로 스타터만 바꿔도 `@v1.4.0`이 생긴다. 소비자는 변경 내용을 보고 어느 숫자를 올릴지 판단해야 한다. "모든 릴리스에 두 숫자를 같이 올린다"는 정책으로 단순화할 수 있지만 그러면 B/C의 프로젝트 측 변경이 항상 2줄이 된다.
- A의 Dockerfile 전파는 코드 변경(실험 5)과 완전히 같은 경로·비용이었다. B/C는 변경 종류에 따라 올리는 숫자가 다르다(실험 5·6: `platformVersion`, 7: `@v`).
- 이미지 크기 141MB → 99MB. 베이스 변경의 효과는 세 안 모두 같고, 전파 방식만 다르다.
- 도구 관찰(측정 외): CI가 만든 이미지는 `linux/amd64` 단일 플랫폼이라 Apple Silicon에서 확인할 때 `--platform linux/amd64`가 필요했다.
