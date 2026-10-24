# Phase 2: A안 비즈니스 프로젝트(demo-a-contract) 구현 계획

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** A안의 생성 절차(`git clone` + `remote add upstream` + 패키지 치환)로 `demo-a-contract`를 만들고, 빌드·네 앱 기동·CI·이미지 푸시까지 확인한 뒤 실험 1(A) 기록을 남긴다.

**Architecture:** `demo-a-contract`는 `demo-a-platform`의 git 이력을 그대로 물려받은 clone이다. `upstream` 리모트가 플랫폼 레포를, `origin`이 비즈니스 레포를 가리킨다. 프로젝트는 스펙 5.4의 소유권 규약에 따라 프로젝트 소유 파일(`apps/*/src/**`, `libs/**`, `deploy/overlays/**`, README)만 바꾼다. upstream 소유 파일은 한 글자도 건드리지 않으며, 그 때문에 생기는 제약(`rootProject.name`, `deploy/base`의 이미지 이름)은 실험 1의 관찰로 기록한다.

**Tech Stack:** git, GitHub CLI, Gradle 9.7.0 wrapper(레포에 포함), JDK 25, GitHub Actions, GHCR, `kubectl kustomize`.

**Spec:** `docs/superpowers/specs/2026-10-24-insurance-platform-poc-design.md` (3장 레포 구성, 5.4 소유권 규약, 5.5 패키지 이름, 6.2~6.4 워크플로·배포, 7.1~7.2 실험 1, 9장 Phase 2)

## Global Constraints

- 모든 레포는 `/Users/gwanhokim/personal-projects/insurance-poc/<레포>` 아래에 둔다. 이 계획의 코드는 `demo-a-contract`에, 기록은 `insurance-platform-poc`에 들어간다.
- 모든 Gradle·java 명령은 `export JAVA_HOME=$(/usr/libexec/java_home -v 25)` 후 실행한다. JDK 25는 `~/Library/Java/JavaVirtualMachines/temurin-25.jdk`에 설치되어 있다.
- 생성 방식은 `git clone` + `remote add upstream`으로 고정한다. GitHub Fork를 쓰지 않는다.
- **upstream 소유 파일은 수정 금지**: `platform/**`, `build-logic/**`, `gradle/**`, 루트 빌드 파일(`settings.gradle.kts`, `gradle.properties`, `gradlew*`), `apps/*/build.gradle.kts`, `Dockerfile`, `.dockerignore`, `.github/**`, `deploy/base/**`. 이 계획의 어떤 Task도 이 파일들을 바꾸지 않는다. 바꾸고 싶어지는 지점이 나오면 바꾸지 말고 실험 1의 관찰에 적는다.
- 프로젝트 소유 파일: `apps/*/src/**`, `libs/**`, `deploy/overlays/**`, `README.md`.
- 패키지: 비즈니스 프로젝트는 `io.github.khkim6040.contract.*`. 플랫폼 코드 `io.github.khkim6040.platform.*`은 그대로 둔다.
- 이미지 경로: `ghcr.io/khkim6040/demo-a-contract/<app>:<semver>`. `release.yml`은 `github.repository`를 쓰므로 수정 없이 이 경로로 푸시된다.
- 커밋 메시지는 영어 제목 한 줄. 본문·Co-Authored-By 없음. 빌드가 깨진 상태로 커밋하지 않는다.
- 실험 1의 측정값은 "수동 단계 수(목록)"다. 이 계획의 Task 1~5에서 사람이 손댄 단계와 파일 수를 세어 Task 6에 적는다. 시간은 측정하지 않는다.
- 외부 서비스에 쓰는 행동(push, 태그, 이미지 푸시)은 스펙에서 승인되었다. 레포 `khkim6040/demo-a-contract`는 Phase 0에서 빈 공개 레포로 만들어져 있다.

---

## 파일 구조

### demo-a-contract (clone이므로 "변경"만 적는다)

| 경로 | 변경 | 소유 |
|---|---|---|
| `.git/config` 리모트 | `upstream` = demo-a-platform, `origin` = demo-a-contract | — |
| `apps/{api,admin,consumer,batch}/src/{main,test}/kotlin/io/github/khkim6040/sample/**` | 디렉터리 `sample` → `contract`, 패키지·import 문자열 치환 | 프로젝트 |
| `libs/domain/src/{main,test}/kotlin/io/github/khkim6040/sample/**` | 같은 치환 | 프로젝트 |
| `deploy/overlays/dev/kustomization.yaml` | `namespace: contract-dev`, 이미지마다 `newName: ghcr.io/khkim6040/demo-a-contract/<app>` | 프로젝트 |
| `README.md` | 비즈니스 프로젝트 README로 교체 | 프로젝트 |

변경하지 않는 것: `settings.gradle.kts`의 `rootProject.name = "demo-a-platform"`(upstream 소유), `deploy/base/**`의 이미지 이름(upstream 소유, overlay의 `newName`으로 덮음), `apps/*/src/main/resources/application.yml`의 `spring.application.name`(api/admin/consumer/batch 그대로가 맞음), `platform/**`.

### insurance-platform-poc

| 파일 | 책임 |
|---|---|
| `experiments/01-create.md` | 실험 1 기록. 이 Phase에서 A 열을 채우고 B/C 열은 Phase 3·4가 채운다 |

---

### Task 1: clone과 리모트 구성

**Files:**
- Create: `/Users/gwanhokim/personal-projects/insurance-poc/demo-a-contract/` (clone)

**Interfaces:**
- Produces: 로컬 레포 `demo-a-contract`. `git remote -v`에 `upstream`(demo-a-platform)과 `origin`(demo-a-contract). 브랜치 `main`이 `demo-a-platform`의 `95d383a`와 같은 이력을 가진다. 이후 Task는 모두 이 디렉터리에서 실행한다.

- [x] **Step 1: clone**

```bash
cd /Users/gwanhokim/personal-projects/insurance-poc
git clone -q https://github.com/khkim6040/demo-a-platform.git demo-a-contract
cd demo-a-contract
git log --oneline -1
```
Expected: `95d383a Add CI and tag-based release workflows`

- [x] **Step 2: 리모트 재구성**

```bash
cd /Users/gwanhokim/personal-projects/insurance-poc/demo-a-contract
git remote rename origin upstream
git remote add origin https://github.com/khkim6040/demo-a-contract.git
git branch --unset-upstream
git remote -v
```
Expected:
```text
origin    https://github.com/khkim6040/demo-a-contract.git (fetch)
origin    https://github.com/khkim6040/demo-a-contract.git (push)
upstream  https://github.com/khkim6040/demo-a-platform.git (fetch)
upstream  https://github.com/khkim6040/demo-a-platform.git (push)
```

- [x] **Step 3: upstream 태그 정리**

clone은 `api-v0.1.0` 태그를 함께 가져온다. 이 태그가 origin으로 push되면 contract 레포에서 플랫폼의 릴리스가 다시 돌아가므로 로컬에서 지운다. 이후 `git fetch upstream`은 태그를 가져오지 않도록 설정한다.

```bash
cd /Users/gwanhokim/personal-projects/insurance-poc/demo-a-contract
git tag -d api-v0.1.0
git config remote.upstream.tagOpt --no-tags
git tag
```
Expected: 출력 없음(태그 0개)

- [x] **Step 4: 그대로 빌드되는지 확인 (변경 전 기준점)**

```bash
cd /Users/gwanhokim/personal-projects/insurance-poc/demo-a-contract
export JAVA_HOME=$(/usr/libexec/java_home -v 25)
./gradlew build --console=plain 2>&1 | grep -E 'BUILD|FAILED'
```
Expected: `BUILD SUCCESSFUL`. 커밋 없음(아직 변경이 없다).

### Task 2: 패키지 치환

**Files:**
- Modify(이동+치환): `demo-a-contract/apps/{api,admin,consumer,batch}/src/{main,test}/kotlin/io/github/khkim6040/sample/**/*.kt`
- Modify(이동+치환): `demo-a-contract/libs/domain/src/{main,test}/kotlin/io/github/khkim6040/sample/**/*.kt`

**Interfaces:**
- Consumes: Task 1의 clone.
- Produces: 모든 앱·도메인 코드가 `io.github.khkim6040.contract.{domain,api,admin,consumer,batch}` 패키지에 있다. `platform/**`은 `io.github.khkim6040.platform.*` 그대로. 빌드 산출물 `app.jar`의 `Start-Class`가 `io.github.khkim6040.contract.<app>.<App>ApplicationKt`.

- [x] **Step 1: 치환 대상 확인 (실패 조건 정의)**

```bash
cd /Users/gwanhokim/personal-projects/insurance-poc/demo-a-contract
find apps libs -type d -path '*/io/github/khkim6040/sample' -not -path '*/build/*' | sort
grep -rl 'io.github.khkim6040.sample' apps libs --include='*.kt' | wc -l
grep -rl 'io.github.khkim6040.sample' platform build-logic deploy .github Dockerfile settings.gradle.kts 2>/dev/null | wc -l
```
Expected: 디렉터리 10개(api·admin·consumer·batch·domain 각 main·test), `.kt` 파일 23개, 마지막 줄 `0`(upstream 소유 파일에는 `sample` 참조가 없어서 소유권 규약 안에서 치환이 끝난다).

- [x] **Step 2: 디렉터리 이동**

```bash
cd /Users/gwanhokim/personal-projects/insurance-poc/demo-a-contract
for d in $(find apps libs -type d -path '*/io/github/khkim6040/sample' -not -path '*/build/*'); do
  git mv "$d" "$(dirname "$d")/contract"
done
find apps libs -type d -path '*/io/github/khkim6040/*' -not -path '*/build/*' | sort
```
Expected: 경로 10개가 모두 `.../io/github/khkim6040/contract`로 끝난다.

- [x] **Step 3: 패키지·import 문자열 치환**

```bash
cd /Users/gwanhokim/personal-projects/insurance-poc/demo-a-contract
grep -rl 'io.github.khkim6040.sample' apps libs --include='*.kt' | xargs sed -i '' 's/io\.github\.khkim6040\.sample/io.github.khkim6040.contract/g'
grep -rn 'khkim6040.sample' apps libs platform | wc -l
grep -rn '^package ' apps libs --include='*.kt' | sed 's/.*package //' | sort -u
```
Expected: 첫 줄 `0`. 둘째 출력은 정확히 다섯 줄:
```text
io.github.khkim6040.contract.admin
io.github.khkim6040.contract.api
io.github.khkim6040.contract.batch
io.github.khkim6040.contract.consumer
io.github.khkim6040.contract.domain
```

- [x] **Step 4: 빌드와 테스트로 검증**

```bash
cd /Users/gwanhokim/personal-projects/insurance-poc/demo-a-contract
export JAVA_HOME=$(/usr/libexec/java_home -v 25)
./gradlew clean build --console=plain 2>&1 | grep -E 'BUILD|FAILED'
grep -ho 'tests="[0-9]*"' */*/build/test-results/test/*.xml | grep -o '[0-9]*' | paste -sd+ - | bc
for app in api admin consumer batch; do unzip -p apps/$app/build/libs/app.jar META-INF/MANIFEST.MF | grep Start-Class; done
```
Expected: `BUILD SUCCESSFUL`, 테스트 합계 `25`, `Start-Class: io.github.khkim6040.contract.<app>.<App>ApplicationKt` 네 줄.

- [x] **Step 5: 커밋**

```bash
cd /Users/gwanhokim/personal-projects/insurance-poc/demo-a-contract
git add -A apps libs
git status --short | grep -c '^R'
git commit -q -m "Rename sample packages to contract"
git log --oneline -1
```
Expected: `R`(rename) 23개. git이 이동+치환을 rename으로 인식해야 이후 upstream 머지에서 `apps/*/src/**` 변경이 rename을 따라간다(실험 2·10의 충돌 수에 영향).

### Task 3: 프로젝트 소유 배포 설정과 README

**Files:**
- Modify: `demo-a-contract/deploy/overlays/dev/kustomization.yaml`
- Modify: `demo-a-contract/README.md`

**Interfaces:**
- Consumes: `deploy/base/**`의 이미지 이름 `ghcr.io/khkim6040/demo-a-platform/<app>` (upstream 소유, 그대로 둔다).
- Produces: `kubectl kustomize deploy/overlays/dev`가 네 워크로드의 이미지를 `ghcr.io/khkim6040/demo-a-contract/<app>:0.1.0`으로, 네임스페이스를 `contract-dev`로 렌더링한다. 실험 3은 이 파일의 `newTag`만 바꾼다.

- [x] **Step 1: overlay 수정**

`deploy/overlays/dev/kustomization.yaml` 전체를 다음으로 교체:
```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
namespace: contract-dev
resources:
  - ../../base/api
  - ../../base/admin
  - ../../base/consumer
  - ../../base/batch
images:
  - name: ghcr.io/khkim6040/demo-a-platform/api
    newName: ghcr.io/khkim6040/demo-a-contract/api
    newTag: 0.1.0
  - name: ghcr.io/khkim6040/demo-a-platform/admin
    newName: ghcr.io/khkim6040/demo-a-contract/admin
    newTag: 0.1.0
  - name: ghcr.io/khkim6040/demo-a-platform/consumer
    newName: ghcr.io/khkim6040/demo-a-contract/consumer
    newTag: 0.1.0
  - name: ghcr.io/khkim6040/demo-a-platform/batch
    newName: ghcr.io/khkim6040/demo-a-contract/batch
    newTag: 0.1.0
```

- [x] **Step 2: 렌더링 확인**

```bash
cd /Users/gwanhokim/personal-projects/insurance-poc/demo-a-contract
kubectl kustomize deploy/overlays/dev | grep -E 'image:|namespace:' | sort -u
```
Expected: `namespace: contract-dev` 한 줄과 `image: ghcr.io/khkim6040/demo-a-contract/{admin,api,batch,consumer}:0.1.0` 네 줄. `demo-a-platform` 문자열이 없다.

- [x] **Step 3: README 교체**

`README.md` 전체를 다음으로 교체:
```markdown
# demo-a-contract

Insurance platform PoC, A안(clone + upstream merge)의 비즈니스 프로젝트 `contract`.

- upstream: https://github.com/khkim6040/demo-a-platform (`git remote add upstream`, 태그는 가져오지 않음)
- 플랫폼 변경 반영: `git fetch upstream && git merge upstream/main`
- 패키지: `io.github.khkim6040.contract.*` (플랫폼 코드 `io.github.khkim6040.platform.*`은 그대로)

빌드: `./gradlew build` (JDK 25). 릴리스: `deploy/overlays/dev/kustomization.yaml`의 `newTag`를 올려 커밋한 뒤 `git tag api-v0.1.0 && git push origin api-v0.1.0`.

## 수정 금지 (upstream 소유)

`platform/**`, `build-logic/**`, `gradle/**`, 루트 빌드 파일, `apps/*/build.gradle.kts`, `Dockerfile`, `.github/**`, `deploy/base/**`. 이 파일들은 upstream 머지로만 바뀐다. `deploy/base`의 이미지 이름은 overlay의 `newName`으로 덮는다. `rootProject.name`은 `demo-a-platform`으로 남으며 빌드 산출물·이미지 경로에 영향이 없다.

## 프로젝트 소유

`apps/*/src/**`, `libs/**`, `deploy/overlays/**`, 이 README.
```

- [x] **Step 4: 커밋**

```bash
cd /Users/gwanhokim/personal-projects/insurance-poc/demo-a-contract
git add deploy/overlays/dev/kustomization.yaml README.md
git commit -q -m "Point dev overlay and README at the contract project"
git log --oneline -1
git diff upstream/main --stat | tail -1
```
Expected: 마지막 줄 `25 files changed`(kt 23 + overlay 1 + README 1).

### Task 4: 네 앱 기동 확인

**Files:** 없음 (검증만)

**Interfaces:**
- Consumes: Task 2의 `app.jar` 네 개, `insurance-platform-poc/tools/stub-server.py`.
- Produces: 실험 1 성공 기준 "네 앱 기동"의 증거 로그.

- [x] **Step 1: jar 최신화**

```bash
cd /Users/gwanhokim/personal-projects/insurance-poc/demo-a-contract
export JAVA_HOME=$(/usr/libexec/java_home -v 25)
./gradlew bootJar --console=plain -q
ls apps/*/build/libs/app.jar
```
Expected: 네 경로

- [x] **Step 2: api + 스텁**

```bash
S=/private/tmp/claude-501/-Users-gwanhokim-personal-projects/4cd73c96-55d2-443e-ad6b-891bfc33231f/scratchpad
cd /Users/gwanhokim/personal-projects/insurance-poc/insurance-platform-poc
python3 -I tools/stub-server.py 9090 >/dev/null 2>&1 & STUB=$!
cd /Users/gwanhokim/personal-projects/insurance-poc/demo-a-contract
export JAVA_HOME=$(/usr/libexec/java_home -v 25)
java -jar apps/api/build/libs/app.jar > $S/contract-api.log 2>&1 & API=$!
for i in $(seq 1 20); do curl -s -o /dev/null localhost:8080/contracts/x && break; sleep 1; done
ID=$(curl -s -X POST localhost:8080/contracts -H 'Content-Type: application/json' \
  -d '{"holderName":"Kim","insuredAmount":10000000,"startDate":"2026-01-01","endDate":"2027-01-01"}' | sed 's/.*"id":"\([^"]*\)".*/\1/')
curl -s -i "localhost:8080/contracts/$ID/quote" | grep -E 'HTTP/|X-Correlation-Id|quotedPremium'
kill $API $STUB
grep -c 'Tomcat started on port 8080' $S/contract-api.log
```
Expected: `HTTP/1.1 200`, `X-Correlation-Id`, `"quotedPremium":12000`, 마지막 줄 `1`. 패키지는 Task 2 Step 4의 `Start-Class`로 이미 확인했다.

- [x] **Step 3: admin**

```bash
S=/private/tmp/claude-501/-Users-gwanhokim-personal-projects/4cd73c96-55d2-443e-ad6b-891bfc33231f/scratchpad
cd /Users/gwanhokim/personal-projects/insurance-poc/demo-a-contract
export JAVA_HOME=$(/usr/libexec/java_home -v 25)
java -jar apps/admin/build/libs/app.jar > $S/contract-admin.log 2>&1 & ADMIN=$!
for i in $(seq 1 20); do curl -s -o /dev/null localhost:8081/admin/contracts && break; sleep 1; done
curl -s localhost:8081/admin/contracts | grep -o '"id":"C-[0-9]*"' | paste -sd, -
curl -s -o /dev/null -w '%{http_code}\n' -X POST localhost:8081/admin/contracts/C-1001/suspend
curl -s -o /dev/null -w '%{http_code}\n' -X POST localhost:8081/admin/contracts/C-1001/suspend
kill $ADMIN
```
Expected: `"id":"C-1001","id":"C-1002"`, `200`, `409`

- [x] **Step 4: consumer와 batch**

```bash
S=/private/tmp/claude-501/-Users-gwanhokim-personal-projects/4cd73c96-55d2-443e-ad6b-891bfc33231f/scratchpad
cd /Users/gwanhokim/personal-projects/insurance-poc/demo-a-contract
export JAVA_HOME=$(/usr/libexec/java_home -v 25)
java -jar apps/consumer/build/libs/app.jar > $S/contract-consumer.log 2>&1 & C=$!
sleep 10; kill $C
grep -c 'Tomcat' $S/contract-consumer.log
grep -o 'event evt-[0-9]* -> [A-Z_]*' $S/contract-consumer.log | head -3
java -jar apps/batch/build/libs/app.jar > $S/contract-batch.log 2>&1; echo "batch exit=$?"
grep -o 'expired [0-9]* contract(s)' $S/contract-batch.log
```
Expected: `0`(Tomcat 없음), `event evt-1 -> PROCESSED` 등 3줄, `batch exit=0`, `expired 1 contract(s)`

### Task 5: push, CI, 태그 릴리스, upstream 머지 경로 확인

**Files:** 없음 (원격 상태 변경)

**Interfaces:**
- Produces: `khkim6040/demo-a-contract` main에 커밋 13개(플랫폼 11 + Task 2·3). `ci` 성공. `ghcr.io/khkim6040/demo-a-contract/api:0.1.0` 존재(실험 3의 롤백 대상 기준 이미지). `git merge upstream/main`이 "Already up to date".

- [x] **Step 1: push와 CI**

```bash
cd /Users/gwanhokim/personal-projects/insurance-poc/demo-a-contract
git push -q -u origin main
sleep 8
RUN=$(gh run list --workflow ci --limit 1 --json databaseId --jq '.[0].databaseId')
gh run watch --exit-status "$RUN" >/dev/null 2>&1
gh run view "$RUN" --json status,conclusion,url --jq '"\(.status) \(.conclusion) \(.url)"'
```
Expected: `completed success https://github.com/khkim6040/demo-a-contract/actions/runs/<id>`. 실패하면 로그를 읽고 고친다. 이 레포의 워크플로는 upstream과 동일하므로 실패 원인은 Task 2·3의 변경에 있어야 한다.

- [x] **Step 2: 태그 릴리스**

```bash
cd /Users/gwanhokim/personal-projects/insurance-poc/demo-a-contract
git tag api-v0.1.0
git push -q origin api-v0.1.0
sleep 15
RUN=$(gh run list --workflow release --limit 1 --json databaseId --jq '.[0].databaseId')
gh run watch --exit-status "$RUN" >/dev/null 2>&1
gh run view "$RUN" --json status,conclusion,url --jq '"\(.status) \(.conclusion) \(.url)"'
docker manifest inspect ghcr.io/khkim6040/demo-a-contract/api:0.1.0 | grep -m1 '"digest"'
```
Expected: `completed success …`, 다이제스트 한 줄. (gh 토큰에 `read:packages`가 없어 패키지 API 대신 `docker manifest inspect`로 확인한다.)

- [x] **Step 3: upstream 머지 경로 확인**

```bash
cd /Users/gwanhokim/personal-projects/insurance-poc/demo-a-contract
git fetch -q upstream
git merge --no-edit upstream/main
git tag | wc -l
git log --oneline upstream/main..main
```
Expected: `Already up to date.`, 태그 `0`(--no-tags 설정이 동작), 로컬 커밋 2개(`Rename sample packages to contract`, `Point dev overlay and README at the contract project`)

### Task 6: 실험 1 기록 (A 열)

**Files:**
- Create: `insurance-platform-poc/experiments/01-create.md`

**Interfaces:**
- Consumes: Task 1~5의 결과(커밋 SHA, CI·release 실행 URL, 변경 파일 수).
- Produces: 실험 1 기록의 A 열. Phase 3·4가 B·C 열을 같은 파일에 채운다.

- [x] **Step 1: 기록 작성**

`experiments/01-create.md` (꺾쇠 안을 Task 5의 실제 값으로 채운다):
```markdown
# 실험 1: 신규 프로젝트 생성

## 시나리오와 성공 기준

각 안의 절차로 비즈니스 프로젝트 `contract`를 만든다. 성공 기준: `./gradlew build` 통과, 네 앱 기동, CI 녹색, 태그 push로 api 이미지가 `ghcr.io/khkim6040/demo-<x>-contract/api:0.1.0`에 올라감. 측정: 생성 직후 빌드·기동까지 사람이 손댄 수동 단계와 파일 수.

## 결과

| 항목 | A | B | C |
|---|---|---|---|
| 플랫폼 측 수동 단계 수 (목록) | 0 (레포 생성은 Phase 0 부트스트랩, 세 안 공통) | Phase 3에서 기록 | Phase 4에서 기록 |
| 프로젝트 측 수동 단계 수, 프로젝트 1개당 (목록) | 5: ① clone + 리모트 재구성(`clone`, `remote rename`, `remote add`, 태그 삭제, `tagOpt --no-tags`) ② 패키지 치환(디렉터리 10개 `git mv` + `sed`, `.kt` 23개) ③ overlay 수정(네임스페이스 + 이미지 `newName`×4 + `newTag`×4, 파일 1) ④ README 교체(파일 1) ⑤ push + 태그. 손댄 파일 25 | | |
| 머지 충돌 파일 수 | 0 (생성 시점, 머지 없음) | | |
| 의미적 충돌 (빌드·테스트 실패, 동작 변화) | 없음. 치환 직후 `clean build` 통과, 테스트 25개 | | |
| 함께 끌려온 무관한 변경 수 | 해당 없음. 단, clone은 플랫폼의 샘플 코드·`api-v0.1.0` 태그·커밋 이력 11개를 전부 가져온다 | | |
| 검증 방법과 결과 | `clean build` 통과, `Start-Class`가 `contract` 패키지, 네 앱 기동(api quote 12000, admin 200→409, consumer Tomcat 없음, batch exit 0), CI 성공, `api:0.1.0` 매니페스트 확인, `merge upstream/main` = Already up to date | | |

## 근거: 커밋 SHA, PR, CI 실행 링크

- A: https://github.com/khkim6040/demo-a-contract — 패키지 치환 `<sha1>`, overlay·README `<sha2>`, ci <ci run URL>, release <release run URL>, 이미지 `ghcr.io/khkim6040/demo-a-contract/api:0.1.0` (digest `<sha256 앞 12자>`)

## 관찰: 잘못하기 쉬운 지점, 자동화할 수 있는 단계

- A: clone이 upstream 태그(`api-v0.1.0`)를 가져온다. 지우지 않고 `git push --tags`를 하면 contract 레포에서 플랫폼 릴리스가 재실행된다. `remote.upstream.tagOpt=--no-tags`를 생성 절차에 넣어야 한다.
- A: `deploy/base`가 upstream 소유라 이미지 이름이 `demo-a-platform`으로 남는다. overlay에서 `newName`으로 덮는 것을 잊으면 CI(`kubectl kustomize`)는 통과하지만 배포 시 엉뚱한 이미지를 당긴다. 소유권 규약이 만드는 비직관적 지점.
- A: `rootProject.name`이 `demo-a-platform`으로 남는다(루트 빌드 파일 수정 금지). 산출물 이름·이미지 경로에 영향은 없지만 IDE 프로젝트 이름이 플랫폼 이름으로 보인다.
- A: ①~④는 셸 스크립트 하나로 자동화할 수 있다(C안의 `create-project.sh`와 같은 자리). 다만 A안의 본질(이력 공유, 머지로 전파)은 그대로이므로 생성 비용만 줄어들고 이후 실험의 충돌 비용은 변하지 않는다.
- A: 패키지 치환이 git rename으로 인식되는지(`git status`의 `R`) 확인해야 한다. 디렉터리 이동과 내용 치환을 한 커밋에 넣으면 유사도가 높아 rename으로 잡히고, 이후 upstream이 `apps/*/src/**`를 바꾸지 않는 한 머지에 영향이 없다.
```

- [x] **Step 2: 커밋과 push**

```bash
cd /Users/gwanhokim/personal-projects/insurance-poc/insurance-platform-poc
git add experiments/01-create.md
git commit -q -m "Record experiment 1 results for approach A"
git push -q
git log --oneline -1
```

---

## 자체 점검 결과

- **스펙 커버리지 (Phase 2 범위)**: 3장 `demo-a-contract` 생성 방식(Task 1), 5.4 소유권 규약 준수(Global Constraints, Task 2·3은 프로젝트 소유 파일만), 5.5 패키지 이름(Task 2), 6.2~6.4 워크플로·overlay(Task 3·5), 7.1 기록 양식(Task 6), 7.2 실험 1 성공 기준(Task 2 빌드, Task 4 기동, Task 6 수동 단계 수), 9장 Phase 2 완료 기준 "contract 빌드·기동"(Task 2·4).
- **의도적으로 뺀 것**: `rootProject.name`·`spring.application.name` 변경(전자는 규약 위반, 후자는 불필요), 샘플 도메인 코드 수정(contract 프로젝트의 코드로 그대로 승계), GHCR 패키지 공개 설정.
- **알려진 위험**: git이 이동+치환을 rename으로 인식하지 못하면(유사도 50% 미만) Task 2 Step 5의 `R` 개수가 23보다 적게 나온다. 파일 내용 중 바뀌는 것은 `package`·`import` 줄뿐이라 유사도는 충분히 높지만, 적게 나오면 그 사실을 실험 1 관찰에 적고 진행한다. 설계는 바꾸지 않는다.
