# 실험 1: 신규 프로젝트 생성

## 시나리오와 성공 기준

각 안의 절차로 비즈니스 프로젝트 `contract`를 만든다. 성공 기준: `./gradlew build` 통과, 네 앱 기동, CI 녹색, 태그 push로 api 이미지가 `ghcr.io/khkim6040/demo-<x>-contract/api:0.1.0`에 올라감. 측정: 생성 직후 빌드·기동까지 사람이 손댄 수동 단계와 파일 수.

## 결과

| 항목 | A | B | C |
|---|---|---|---|
| 플랫폼 측 수동 단계 수 (목록) | 0 (레포 생성은 Phase 0 부트스트랩, 세 안 공통) | Phase 3에서 기록 | Phase 4에서 기록 |
| 프로젝트 측 수동 단계 수, 프로젝트 1개당 (목록) | 5: ① clone + 리모트 재구성(`clone`, `remote rename`, `remote add`, upstream 태그 삭제, `tagOpt --no-tags`) ② 패키지 치환(디렉터리 10개 `git mv` + `sed`, `.kt` 23개) ③ overlay 수정(네임스페이스 + 이미지 `newName`×4 + `newTag`×4, 파일 1) ④ README 교체(파일 1) ⑤ push + 태그. 손댄 파일 25 | | |
| 머지 충돌 파일 수 | 0 (생성 시점, 머지 없음) | | |
| 의미적 충돌 (빌드·테스트 실패, 동작 변화) | 없음. 치환 직후 `clean build` 통과, 테스트 25개 | | |
| 함께 끌려온 무관한 변경 수 | 해당 없음. 단, clone은 플랫폼의 샘플 코드·`api-v0.1.0` 태그·커밋 이력 11개를 전부 가져온다 | | |
| 검증 방법과 결과 | `clean build` 통과, 네 jar의 `Start-Class`가 `contract` 패키지, 네 앱 기동(api quote 12000 + `X-Correlation-Id`, admin 목록 2건·suspend 200→409, consumer Tomcat 없음·PROCESSED/DUPLICATE/DEAD_LETTERED, batch `expired 1` exit 0), CI 성공, `api:0.1.0` 매니페스트 확인, `merge upstream/main` = Already up to date | | |

## 근거: 커밋 SHA, PR, CI 실행 링크

- A: https://github.com/khkim6040/demo-a-contract — 패키지 치환 `1ab1435`, overlay·README `d05f63f`, ci https://github.com/khkim6040/demo-a-contract/actions/runs/40098410348, release https://github.com/khkim6040/demo-a-contract/actions/runs/40098586190, 이미지 `ghcr.io/khkim6040/demo-a-contract/api:0.1.0` (digest `sha256:7d9101143e6a`)

## 관찰: 잘못하기 쉬운 지점, 자동화할 수 있는 단계

- A: clone이 upstream 태그(`api-v0.1.0`)를 가져온다. 지우지 않고 `git push --tags`를 하면 contract 레포에서 플랫폼 릴리스가 재실행된다. `remote.upstream.tagOpt=--no-tags`를 생성 절차에 넣어야 한다.
- A: `deploy/base`가 upstream 소유라 이미지 이름이 `demo-a-platform`으로 남는다. overlay에서 `newName`으로 덮는 것을 잊으면 CI(`kubectl kustomize`)는 통과하지만 배포 시 엉뚱한 이미지를 당긴다. 소유권 규약이 만드는 비직관적 지점.
- A: `rootProject.name`이 `demo-a-platform`으로 남는다(루트 빌드 파일 수정 금지). 산출물 이름·이미지 경로에 영향은 없지만 IDE 프로젝트 이름이 플랫폼 이름으로 보인다.
- A: 리모트가 둘이면 `gh run list`가 upstream 레포를 고를 수 있다. `-R khkim6040/demo-a-contract`를 명시해야 한다.
- A: ①~④는 셸 스크립트 하나로 자동화할 수 있다(C안의 `create-project.sh`와 같은 자리). 다만 A안의 본질(이력 공유, 머지로 전파)은 그대로이므로 생성 비용만 줄어들고 이후 실험의 충돌 비용은 변하지 않는다.
- A: 패키지 치환이 git rename으로 인식되는지(`git status`의 `R`) 확인해야 한다. 디렉터리 이동과 내용 치환을 한 커밋에 넣었더니 23개 전부 rename으로 잡혔다. upstream이 `apps/*/src/**`를 바꾸지 않는 한 머지에 영향이 없다.
