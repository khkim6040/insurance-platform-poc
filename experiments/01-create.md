# 실험 1: 신규 프로젝트 생성

## 시나리오와 성공 기준

각 안의 절차로 비즈니스 프로젝트 `contract`를 만든다. 성공 기준: `./gradlew build` 통과, 네 앱 기동, CI 녹색, 태그 push로 api 이미지가 `ghcr.io/khkim6040/demo-<x>-contract/api:0.1.0`에 올라감. 측정: 생성 직후 빌드·기동까지 사람이 손댄 수동 단계와 파일 수.

## 결과

| 항목 | A | B | C |
|---|---|---|---|
| 플랫폼 측 수동 단계 수 (목록) | 0 (레포 생성은 Phase 0 부트스트랩, 세 안 공통) | 0 (템플릿·아티팩트는 1회성 플랫폼 구축, baseline에 기록) | Phase 4에서 기록 |
| 프로젝트 측 수동 단계 수, 프로젝트 1개당 (목록) | 5: ① clone + 리모트 재구성(`clone`, `remote rename`, `remote add`, upstream 태그 삭제, `tagOpt --no-tags`) ② 패키지 치환(디렉터리 10개 `git mv` + `sed`, `.kt` 23개) ③ overlay 수정(네임스페이스 + 이미지 `newName`×4 + `newTag`×4, 파일 1) ④ README 교체(파일 1) ⑤ push + 태그. 손댄 파일 25 | 4: ① `gh repo create --template --clone` ② 패키지 치환(디렉터리 10개 `git mv` + `sed`, `.kt` 23개) ③ 레포 이름 `sed`(`settings.gradle.kts`, `deploy/` 5, README = 7) ④ push + 태그. 손댄 파일 30. 별도로 개발자 환경 1회: `~/.gradle/gradle.properties`에 GitHub Packages 토큰 | |
| 머지 충돌 파일 수 | 0 (생성 시점, 머지 없음) | 0 (머지 개념 없음) | |
| 의미적 충돌 (빌드·테스트 실패, 동작 변화) | 없음. 치환 직후 `clean build` 통과, 테스트 25개 | 없음. `clean build` 통과, 테스트 20개(스타터 테스트 5개는 플랫폼 레포에 있음) | |
| 함께 끌려온 무관한 변경 수 | 해당 없음. 단, clone은 플랫폼의 샘플 코드·`api-v0.1.0` 태그·커밋 이력 11개를 전부 가져온다 | 해당 없음. 템플릿 생성은 이력 없이 파일만 복사(커밋 1개), 태그 없음 | |
| 검증 방법과 결과 | `clean build` 통과, 네 jar의 `Start-Class`가 `contract` 패키지, 네 앱 기동(api quote 12000 + `X-Correlation-Id`, admin 목록 2건·suspend 200→409, consumer Tomcat 없음·PROCESSED/DUPLICATE/DEAD_LETTERED, batch `expired 1` exit 0), CI 성공, `api:0.1.0` 매니페스트 확인, `merge upstream/main` = Already up to date | A와 같은 기동 검증 통과, `runtimeClasspath`에 `platform-http-starter:1.0.0`·`platform-bom:1.0.0`, CI 성공(다른 레포의 `GITHUB_TOKEN`으로 GitHub Packages 읽기 성공, 추가 시크릿 없음), reusable `release-app.yml@v1.0.0`로 `api:0.1.0` 푸시(플랫폼 checkout `github.job_workflow_sha` = `v1.0.0` 커밋 `61f42812`) | |

## 근거: 커밋 SHA, PR, CI 실행 링크

- A: https://github.com/khkim6040/demo-a-contract — 패키지 치환 `1ab1435`, overlay·README `d05f63f`, ci https://github.com/khkim6040/demo-a-contract/actions/runs/40098410348, release https://github.com/khkim6040/demo-a-contract/actions/runs/40098586190, 이미지 `ghcr.io/khkim6040/demo-a-contract/api:0.1.0` (digest `sha256:7d9101143e6a`)

- B: https://github.com/khkim6040/demo-b-contract — 템플릿 초기 커밋 `c5710b9`, 패키지 치환 `c85501b`, 이름 치환 `c5823ec`, ci https://github.com/khkim6040/demo-b-contract/actions/runs/40100540764, release https://github.com/khkim6040/demo-b-contract/actions/runs/40100753155, 이미지 `ghcr.io/khkim6040/demo-b-contract/api:0.1.0` (digest `sha256:f8ac9fcbdf5b`). 플랫폼: https://github.com/khkim6040/demo-b-platform `v1.0.0` publish https://github.com/khkim6040/demo-b-platform/actions/runs/40100047177, 템플릿 https://github.com/khkim6040/demo-b-template ci https://github.com/khkim6040/demo-b-template/actions/runs/40100214721

## 관찰: 잘못하기 쉬운 지점, 자동화할 수 있는 단계

- A: clone이 upstream 태그(`api-v0.1.0`)를 가져온다. 지우지 않고 `git push --tags`를 하면 contract 레포에서 플랫폼 릴리스가 재실행된다. `remote.upstream.tagOpt=--no-tags`를 생성 절차에 넣어야 한다.
- A: `deploy/base`가 upstream 소유라 이미지 이름이 `demo-a-platform`으로 남는다. overlay에서 `newName`으로 덮는 것을 잊으면 CI(`kubectl kustomize`)는 통과하지만 배포 시 엉뚱한 이미지를 당긴다. 소유권 규약이 만드는 비직관적 지점.
- A: `rootProject.name`이 `demo-a-platform`으로 남는다(루트 빌드 파일 수정 금지). 산출물 이름·이미지 경로에 영향은 없지만 IDE 프로젝트 이름이 플랫폼 이름으로 보인다.
- A: 리모트가 둘이면 `gh run list`가 upstream 레포를 고를 수 있다. `-R khkim6040/demo-a-contract`를 명시해야 한다.
- A: ①~④는 셸 스크립트 하나로 자동화할 수 있다(C안의 `create-project.sh`와 같은 자리). 다만 A안의 본질(이력 공유, 머지로 전파)은 그대로이므로 생성 비용만 줄어들고 이후 실험의 충돌 비용은 변하지 않는다.
- A: 패키지 치환이 git rename으로 인식되는지(`git status`의 `R`) 확인해야 한다. 디렉터리 이동과 내용 치환을 한 커밋에 넣었더니 23개 전부 rename으로 잡혔다. upstream이 `apps/*/src/**`를 바꾸지 않는 한 머지에 영향이 없다.
- B: GitHub 템플릿 생성은 기존 레포를 대상으로 못 한다. Phase 0이 `demo-b-contract`를 미리 만들어 둔 탓에 삭제 후 재생성했다(`delete_repo` 스코프 필요). 실무에서는 템플릿 생성이 레포 생성 자체이므로 부트스트랩이 비즈니스 레포를 미리 만들면 안 된다.
- B: 패키지 치환은 A와 같은 수동 단계다. GitHub Template에는 치환 기능이 없다. 이 단계는 C안의 스크립트가 흡수한다.
- B: 레포 이름이 `settings.gradle.kts`·`deploy/`·README 세 곳에 박혀 있어 `sed` 한 번이 필요하다. A안은 `deploy/base`를 못 건드려 overlay `newName`으로 우회했지만, B안은 전부 프로젝트 소유라 직접 바꾼다.
- B: 로컬 빌드에 GitHub Packages 토큰이 필요하다. 사내 Nexus도 같은 조건이지만, 토큰 없이는 `./gradlew build`조차 안 되므로 온보딩 문서의 첫 줄이 된다. 이번 PoC에서는 gh 토큰에 `read:packages` 스코프를 추가하는 브라우저 인증이 한 번 필요했다.
- B: CI에서 다른 레포 패키지 읽기는 `GITHUB_TOKEN`으로 됐다. 공개 레포의 패키지라 가능했고, 비공개 플랫폼 레포라면 PAT 시크릿이 필요하다.
- B: 플랫폼 버전을 올릴 때 숫자 두 개(`gradle.properties`의 `platformVersion`, `release.yml`의 `@v`)를 맞춰야 한다. 스펙은 "하나"를 목표로 했지만 reusable workflow 참조는 Gradle 프로퍼티로 못 만든다. 실험 7·8에서 두 숫자가 어긋났을 때의 비용을 본다.
