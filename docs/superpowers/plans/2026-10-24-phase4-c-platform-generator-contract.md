# Phase 4: C안(퍼블리시 + 제너레이터) 구현 계획

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `demo-c-platform`이 B안과 같은 아티팩트(BOM·카탈로그·스타터)와 reusable 릴리스 워크플로를 `1.0.0`으로 퍼블리시하면서 `templates/multi-service/`와 `tools/create-project.sh`를 함께 제공하고, 스크립트 한 번으로 생성한 `demo-c-contract`가 빌드·기동·CI·이미지 푸시까지 되는 것을 확인한 뒤 실험 1(C)를 기록한다.

**Architecture:** 플랫폼 레포는 `demo-b-platform` `v1.0.0`의 작업 트리를 그대로 복사하고 레포 이름만 바꾼다(스펙 3장 "B와 C의 플랫폼 레포는 라이브러리 코드가 같지만 별도로 유지"). 여기에 `templates/multi-service/`로 `demo-b-template` 작업 트리를 복사해 넣고(레포 참조는 `demo-c-template`/`demo-c-platform`으로), `tools/create-project.sh`가 `git archive`로 템플릿을 꺼내 레포 이름·패키지를 치환하고 `git init` + 첫 커밋까지 만든다. B안에서 사람이 하던 "패키지 치환"과 "레포 이름 `sed`" 두 단계가 스크립트 안으로 들어가는 것이 B와 C의 유일한 차이다. 템플릿은 플랫폼 레포의 `v1.0.0` 태그에 포함되므로 "생성된 프로젝트 = 플랫폼 v1.0.0에서 생성"이 커밋 메시지에 남는다.

**Tech Stack:** Phase 3와 동일(Gradle 9.7.0 `java-platform`·`version-catalog`·`maven-publish`, GitHub Packages, reusable workflow, JDK 25, Kotlin 2.4.21, Spring Boot 4.1.2, GHCR, `kubectl kustomize`) + bash 스크립트(`git archive`, `perl -pi`, `find`/`mv`).

**Spec:** `docs/superpowers/specs/2026-10-24-insurance-platform-poc-design.md` (3장 레포 구성, 4.4 아티팩트, 5.5 패키지, 6.2·6.5 CI, 7.1~7.2 실험 1, 9장 Phase 4)

## Global Constraints

- 모든 레포는 `/Users/gwanhokim/personal-projects/insurance-poc/<레포>` 아래에 둔다. 이 계획은 `demo-c-platform`, `demo-c-contract` 두 디렉터리를 만들고, 기록은 `insurance-platform-poc`에 쓴다. 두 GitHub 레포는 Phase 0 부트스트랩이 빈 레포로 만들어 두었다(`gh repo list`로 확인됨). C안의 스크립트는 로컬에 레포를 만들고 push는 사용자가 하므로 빈 레포가 있어도 문제없다(B안의 템플릿 생성과 다른 점).
- 모든 Gradle·java 명령은 `export JAVA_HOME=$(/usr/libexec/java_home -v 25)` 후 실행한다.
- 버전: Spring Boot `4.1.2`, Kotlin `2.4.21`, Gradle `9.7.0`, JDK `25`. 플랫폼 아티팩트 버전은 git 태그 `v1.0.0`에서 나온 `1.0.0`. Group ID `io.github.khkim6040.platform`. 저장소 `https://maven.pkg.github.com/khkim6040/demo-c-platform`(GitHub Packages는 레포별이므로 B와 좌표가 같아도 충돌 없음).
- **한 번만 작성 원칙**: 플랫폼 모듈·워크플로·Dockerfile은 `demo-b-platform` 태그 `v1.0.0`(커밋 `61f4281`)에서, 템플릿은 `demo-b-template` 커밋 `50e4394`에서 `git archive`로 복사한다. 바뀌는 파일만 이 계획에 전체 내용을 적는다.
- 템플릿 안의 치환 대상은 두 가지다: 레포 이름 `demo-c-template`(→ `<이름>`), 패키지 `io.github.khkim6040.sample`(→ `io.github.khkim6040.<패키지>`). 템플릿은 이 이름으로 그대로 빌드 가능한 완전한 프로젝트여야 한다(토큰 `__NAME__` 같은 자리표시자를 쓰지 않는다).
- 스크립트는 `git archive HEAD:templates/multi-service`로 **커밋된** 템플릿만 꺼낸다. 템플릿을 고치면 커밋한 뒤 스크립트를 실행한다.
- 플랫폼 CI는 템플릿을 빌드하지 않는다. 템플릿은 플랫폼 패키지가 퍼블리시된 뒤에만 빌드할 수 있어(퍼블리시 전엔 `platform-catalog:1.0.0`이 없음) 첫 push에서 닭과 달걀이 되기 때문이다. 템플릿 검증은 생성된 `demo-c-contract`의 빌드로 한다. 이 공백은 실험 1 관찰에 적는다.
- 커밋 메시지는 영어 제목 한 줄. 본문·Co-Authored-By 없음. 빌드가 깨진 상태로 커밋하지 않는다.
- 외부 서비스에 쓰는 행동(push, 태그, 패키지·이미지 퍼블리시)은 스펙과 이 계획의 승인 범위다. 삭제·재생성은 없다.
- `gh`는 항상 `-R khkim6040/<레포>`를 명시한다.
- 실험 1의 측정값은 "수동 단계 수(목록)"다. Task 5에서 사람이 손댄 단계와 파일 수를 세어 Task 6에 적는다. 플랫폼 구축(Task 1~4)은 1회성 비용이므로 `00-baseline.md`(Phase 5)에 들어간다.

---

## 파일 구조

### demo-c-platform

| 파일 | 책임 | 출처 |
|---|---|---|
| `settings.gradle.kts`, `build.gradle.kts`, `gradle.properties`, `gradle/**`, `gradlew*`, `.gitignore` | B와 동일. `rootProject.name`·퍼블리시 URL만 `demo-c-platform` | `demo-b-platform@v1.0.0` 복사 + `sed` |
| `build-logic/**`, `platform-bom/`, `platform-catalog/`, `platform-http-starter/**` | B와 바이트 동일 | 복사 |
| `Dockerfile`, `.dockerignore` | B와 동일 | 복사 |
| `.github/workflows/ci.yml`, `publish.yml` | B와 동일 | 복사 |
| `.github/workflows/release-app.yml` | `repository: khkim6040/demo-c-platform` | 복사 + `sed` |
| `templates/multi-service/**` | 비즈니스 모노레포 템플릿. `demo-b-template` 전체(워크플로·deploy·wrapper 포함). 레포 참조 `demo-c-template`, 플랫폼 URL·`@v1.0.0` 참조 `demo-c-platform` | `demo-b-template@50e4394` 복사 + `sed` |
| `templates/multi-service/README.md` | 생성된 프로젝트의 README. 스크립트 기반 생성 절차 | 신규 |
| `tools/create-project.sh` | 제너레이터. 템플릿 추출 → 이름·패키지 치환 → 잔여 자리표시자 자가 점검 → `git init` + 커밋 | 신규 |
| `README.md` | 아티팩트·워크플로·템플릿·제너레이터 설명 | 신규 |

### demo-c-contract

스크립트 출력 그대로. 사람이 손대는 파일 0개.

### insurance-platform-poc

| 파일 | 변경 |
|---|---|
| `docs/superpowers/plans/2026-10-24-phase4-c-platform-generator-contract.md` | 이 계획 |
| `experiments/01-create.md` | C 열, 근거, 관찰 |

---

### Task 1: demo-c-platform 골격 (B 플랫폼 복사)

**Files:**
- Create: `demo-c-platform/**` (B 플랫폼 `v1.0.0` 작업 트리 전체)
- Modify: `settings.gradle.kts`, `build.gradle.kts`, `.github/workflows/release-app.yml`, `README.md` 안의 `demo-b-platform` → `demo-c-platform`

**Interfaces:**
- Produces: GitHub Packages 좌표 `io.github.khkim6040.platform:{platform-bom,platform-catalog,platform-http-starter}` @ `https://maven.pkg.github.com/khkim6040/demo-c-platform`; reusable 워크플로 `khkim6040/demo-c-platform/.github/workflows/release-app.yml`

- [ ] **Step 1: 복사와 이름 치환**

```bash
cd /Users/gwanhokim/personal-projects/insurance-poc
mkdir demo-c-platform
git -C demo-b-platform archive --format=tar v1.0.0 | tar -xf - -C demo-c-platform
cd demo-c-platform
grep -rlI 'demo-b-platform' . | xargs perl -pi -e 's/demo-b-platform/demo-c-platform/g'
grep -rnI 'demo-b' . ; echo "leftover=$?"
git init -q -b main
git remote add origin https://github.com/khkim6040/demo-c-platform.git
```
Expected: `leftover=1`(`demo-b` 문자열 없음). 치환된 파일은 `settings.gradle.kts`, `build.gradle.kts`, `.github/workflows/release-app.yml`, `README.md` 네 개(`git status`로는 아직 안 보임, 새 레포).

- [ ] **Step 2: 로컬 빌드·퍼블리시 검증**

```bash
cd /Users/gwanhokim/personal-projects/insurance-poc/demo-c-platform
export JAVA_HOME=$(/usr/libexec/java_home -v 25)
./gradlew build publishToMavenLocal -PplatformVersion=0.0.0-LOCAL --console=plain 2>&1 | grep -E 'BUILD|FAILED|tests completed'
ls ~/.m2/repository/io/github/khkim6040/platform/
grep -o 'maven.pkg.github.com/khkim6040/[a-z-]*' build.gradle.kts
```
Expected: `BUILD SUCCESSFUL`, 디렉터리 `platform-bom platform-catalog platform-http-starter`, URL이 `demo-c-platform`.

- [ ] **Step 3: 커밋**

```bash
cd /Users/gwanhokim/personal-projects/insurance-poc/demo-c-platform
git add -A
git commit -q -m "Add platform modules and workflows from demo-b-platform v1.0.0"
git log --oneline
```

---

### Task 2: templates/multi-service

**Files:**
- Create: `demo-c-platform/templates/multi-service/**` (B 템플릿 `50e4394` 작업 트리 전체)
- Modify: 그 안의 `demo-b-template` → `demo-c-template`(`settings.gradle.kts`, `deploy/` 5개, `README.md`), `demo-b-platform` → `demo-c-platform`(`settings.gradle.kts`, `build-logic/settings.gradle.kts`, `.github/workflows/release.yml`)
- Create(덮어쓰기): `templates/multi-service/README.md`

**Interfaces:**
- Consumes: Task 1의 패키지 좌표와 reusable 워크플로 경로
- Produces: 치환 대상 두 가지 — 문자열 `demo-c-template`, 패키지 `io.github.khkim6040.sample`(디렉터리 `*/io/github/khkim6040/sample`, 10개). Task 3의 스크립트가 이 둘을 바꾼다

- [ ] **Step 1: 복사와 참조 치환**

```bash
cd /Users/gwanhokim/personal-projects/insurance-poc/demo-c-platform
mkdir -p templates/multi-service
git -C ../demo-b-template archive --format=tar 50e4394 | tar -xf - -C templates/multi-service
cd templates/multi-service
grep -rlI 'demo-b-template' . | xargs perl -pi -e 's/demo-b-template/demo-c-template/g'
grep -rlI 'demo-b-platform' . | xargs perl -pi -e 's/demo-b-platform/demo-c-platform/g'
grep -rnI 'demo-b' . ; echo "leftover=$?"
grep -rnI 'demo-c-template' . | wc -l
grep -rnI 'demo-c-platform' . | cut -d: -f1 | sort -u
find . -type d -path '*/io/github/khkim6040/sample' | wc -l
find . -name '*.kt' | wc -l
ls -la gradlew .github/workflows
```
Expected: `leftover=1`; `demo-c-template` 참조는 settings 1 + README 3 + overlay 5 + base 4 = `13`줄; `demo-c-platform` 파일은 `./.github/workflows/release.yml`, `./build-logic/settings.gradle.kts`, `./settings.gradle.kts` 세 개; `sample` 디렉터리 `10`; `.kt` `23`; `gradlew`가 실행 가능(`-rwxr-xr-x`), 워크플로 `ci.yml`·`release.yml`.

- [ ] **Step 2: 템플릿 README 교체**

`templates/multi-service/README.md` 전체 내용:

```markdown
# demo-c-template

Insurance platform PoC, C안의 비즈니스 모노레포. `demo-c-platform`의 `tools/create-project.sh`가 `templates/multi-service/`에서 생성한다. 플랫폼 코드는 GitHub Packages 아티팩트(`io.github.khkim6040.platform:*`)로 가져온다.

## 새 프로젝트 만들기

플랫폼 레포 clone 안에서 실행한다(개발자당 1회 `git clone https://github.com/khkim6040/demo-c-platform.git`).

1. `tools/create-project.sh <이름> <패키지> [대상 경로]` — 템플릿 복사, 레포 이름·패키지 치환, `git init` + 첫 커밋까지 한 번에. 치환이 남으면 스크립트가 실패한다
2. 로컬 자격 증명(개발자당 1회): `~/.gradle/gradle.properties`에 `gpr.user`, `gpr.key`(`read:packages` 토큰)
3. `git remote add origin https://github.com/khkim6040/<이름>.git && git push -u origin main` → `ci`
4. 릴리스: `deploy/overlays/dev`의 `newTag` 수정 후 `git tag api-v0.1.0 && git push origin api-v0.1.0`

## 플랫폼 버전 올리기

`gradle.properties`의 `platformVersion`과 `.github/workflows/release.yml`의 `@vX.Y.Z`를 올린다. BOM·카탈로그·스타터는 `platformVersion`을 따라오고, Dockerfile·릴리스 단계는 `@v`를 따라온다.

## 구조

- `apps/{api,admin,consumer,batch}`, `libs/domain`: Phase 1 참조 구현과 동일
- `build-logic`: 컨벤션 플러그인 복사본. 플랫폼 BOM(`libs.platform.bom`)을 적용한다. 중앙 업데이트되지 않는다
- `deploy/`: Kustomize. 전부 프로젝트 소유
- `Dockerfile`은 없다. 릴리스 워크플로가 플랫폼 레포에서 가져온다
```

- [ ] **Step 3: 플랫폼 루트 Gradle이 템플릿을 무시하는지 확인**

```bash
cd /Users/gwanhokim/personal-projects/insurance-poc/demo-c-platform
export JAVA_HOME=$(/usr/libexec/java_home -v 25)
./gradlew projects --console=plain -q | grep -E "Project|template"
git status --short | grep -v '^?? templates/' ; echo "non-template changes=$?"
```
Expected: 프로젝트 목록에 `platform-bom`, `platform-catalog`, `platform-http-starter`만 있고 `template` 줄 없음(루트 `settings.gradle.kts`가 include하지 않으므로). `non-template changes=1`(템플릿 외 변경 없음).

- [ ] **Step 4: 커밋**

```bash
cd /Users/gwanhokim/personal-projects/insurance-poc/demo-c-platform
git add templates
git commit -q -m "Add multi-service project template"
git log --oneline | head -2
```

---

### Task 3: tools/create-project.sh

**Files:**
- Create: `demo-c-platform/tools/create-project.sh`

**Interfaces:**
- Consumes: Task 2의 치환 대상(`demo-c-template`, `io.github.khkim6040.sample`), 커밋된 `templates/multi-service`
- Produces: `tools/create-project.sh <repo-name> <package-segment> [dest-dir]`. 성공 시 `dest-dir`(기본 `$PWD/<repo-name>`)에 `main` 브랜치 커밋 1개가 있는 git 레포. 종료 코드 0. 실패(인자 오류, 대상 존재, 치환 잔여) 시 1

- [ ] **Step 1: 스크립트 작성**

`tools/create-project.sh` 전체 내용:

```bash
#!/usr/bin/env bash
# Generates a business monorepo from the committed templates/multi-service.
# Usage: tools/create-project.sh <repo-name> <package-segment> [dest-dir]
#   repo-name        e.g. demo-c-contract  -> replaces "demo-c-template" everywhere
#   package-segment  e.g. contract         -> io.github.khkim6040.<segment>
#   dest-dir         default: $PWD/<repo-name>
# Only committed template files are used (git archive HEAD), so commit template edits first.
set -euo pipefail

USAGE="usage: tools/create-project.sh <repo-name> <package-segment> [dest-dir]"
NAME=${1:?$USAGE}
PKG=${2:?$USAGE}
DEST=${3:-$PWD/$NAME}
[[ $NAME =~ ^[a-z0-9-]+$ ]] || { echo "repo-name must match [a-z0-9-]+: $NAME" >&2; exit 1; }
[[ $PKG =~ ^[a-z][a-z0-9]*$ ]] || { echo "package-segment must match [a-z][a-z0-9]*: $PKG" >&2; exit 1; }
[[ -e $DEST ]] && { echo "destination already exists: $DEST" >&2; exit 1; }

PLATFORM=$(cd "$(dirname "$0")/.." && pwd)
SHA=$(git -C "$PLATFORM" rev-parse --short HEAD)

mkdir -p "$DEST"
git -C "$PLATFORM" archive --format=tar HEAD:templates/multi-service | tar -xf - -C "$DEST"

# 1. repo name (settings.gradle.kts, deploy/, README)
grep -rlI 'demo-c-template' "$DEST" | xargs -r perl -pi -e "s/demo-c-template/$NAME/g"
# 2. package: move source directories, then rewrite package/import lines
find "$DEST" -type d -path '*/io/github/khkim6040/sample' | while read -r d; do mv "$d" "$(dirname "$d")/$PKG"; done
grep -rlI 'io\.github\.khkim6040\.sample' "$DEST" | xargs -r perl -pi -e "s/io\\.github\\.khkim6040\\.sample/io.github.khkim6040.$PKG/g"

# self-check: fail loudly if any placeholder survived
if grep -rqIE 'demo-c-template|khkim6040[./]sample' "$DEST"; then
  echo "placeholders left behind:" >&2
  grep -rlIE 'demo-c-template|khkim6040[./]sample' "$DEST" >&2
  exit 1
fi

git -C "$DEST" init -q -b main
git -C "$DEST" add -A
git -C "$DEST" commit -q -m "Generate $NAME from demo-c-platform templates/multi-service@$SHA"
echo "generated $DEST (package io.github.khkim6040.$PKG, platform $SHA)"
echo "next: cd $DEST && git remote add origin https://github.com/khkim6040/$NAME.git && git push -u origin main"
```

```bash
cd /Users/gwanhokim/personal-projects/insurance-poc/demo-c-platform
chmod +x tools/create-project.sh
bash -n tools/create-project.sh && echo syntax-ok
```

- [ ] **Step 2: 스크래치에 생성해 구조 검증**

```bash
S=/private/tmp/claude-501/-Users-gwanhokim-personal-projects/4cd73c96-55d2-443e-ad6b-891bfc33231f/scratchpad
cd /Users/gwanhokim/personal-projects/insurance-poc/demo-c-platform
rm -rf $S/zz-probe
tools/create-project.sh zz-probe probe $S/zz-probe; echo "exit=$?"
cd $S/zz-probe
git log --oneline
git status --short | wc -l
grep -n 'rootProject.name' settings.gradle.kts
grep -c 'ghcr.io/khkim6040/zz-probe/' deploy/overlays/dev/kustomization.yaml
head -1 README.md
find . -name '*.kt' | wc -l
find . -name '*.kt' -path '*/io/github/khkim6040/probe/*' | wc -l
find . -type d -path '*/io/github/khkim6040/sample' | wc -l
grep -rhoE '^package [a-z.]+' --include='*.kt' . | sort -u
grep -rnIE 'demo-c-template|khkim6040[./]sample' . ; echo "leftover=$?"
grep -n 'demo-c-platform' .github/workflows/release.yml settings.gradle.kts build-logic/settings.gradle.kts | wc -l
```
Expected: `exit=0`; 커밋 1개 `Generate zz-probe from demo-c-platform templates/multi-service@<sha>`; 미커밋 변경 `0`; `rootProject.name = "zz-probe"`; overlay `4`; README 첫 줄 `# zz-probe`; `.kt` `23`, 전부 `probe` 경로(`23`), `sample` 디렉터리 `0`; 패키지 목록이 `io.github.khkim6040.probe.{admin,api,batch,consumer,domain}` 5줄; `leftover=1`; `demo-c-platform` 참조 `3`(플랫폼 참조는 그대로 남아야 함).

- [ ] **Step 3: 실패 경로 검증**

```bash
S=/private/tmp/claude-501/-Users-gwanhokim-personal-projects/4cd73c96-55d2-443e-ad6b-891bfc33231f/scratchpad
cd /Users/gwanhokim/personal-projects/insurance-poc/demo-c-platform
tools/create-project.sh zz-probe probe $S/zz-probe; echo "exists exit=$?"
tools/create-project.sh Bad_Name probe $S/zz-bad; echo "name exit=$?"
tools/create-project.sh zz-bad 1pkg $S/zz-bad; echo "pkg exit=$?"
tools/create-project.sh; echo "noargs exit=$?"
ls $S/zz-bad 2>&1 | head -1
rm -rf $S/zz-probe
```
Expected: 네 줄 모두 `exit=1`, `zz-bad` 디렉터리 없음(`No such file`).

- [ ] **Step 4: 커밋**

```bash
cd /Users/gwanhokim/personal-projects/insurance-poc/demo-c-platform
git add tools/create-project.sh
git commit -q -m "Add create-project.sh generator"
git log --oneline | head -3
```

---

### Task 4: 플랫폼 README, push, v1.0.0 퍼블리시

**Files:**
- Modify: `demo-c-platform/README.md` (전체 교체)

**Interfaces:**
- Produces: GitHub Packages에 `1.0.0` 세 아티팩트, 태그 `v1.0.0`(템플릿·스크립트 포함). Task 5의 `platformVersion=1.0.0`과 `release.yml@v1.0.0`이 이것을 가리킨다

- [ ] **Step 1: README 교체**

`README.md` 전체 내용:

```markdown
# demo-c-platform

Insurance platform PoC, C안(퍼블리시 + 제너레이터)의 플랫폼 레포. 아티팩트·워크플로는 B안(`demo-b-platform`)과 같고, 템플릿을 GitHub Template 레포 대신 이 레포의 `templates/`와 `tools/create-project.sh`로 전달한다.

## 퍼블리시 아티팩트 (GitHub Packages, group `io.github.khkim6040.platform`)

| 아티팩트 | 내용 |
|---|---|
| `platform-bom` | `spring-boot-dependencies` import + 플랫폼 스타터 버전 제약. 전이 의존성 버전 강제 수단 |
| `platform-catalog` | `gradle/libs.versions.toml` + `platform` 버전 별칭 + `platform-bom`·`platform-http-starter` 라이브러리 별칭. 플러그인 버전의 중앙 출처 |
| `platform-http-starter` | Correlation ID 필터, ProblemDetail 핸들러, `platform-defaults.yml` |

버전은 git 태그 `vX.Y.Z` = 아티팩트 `X.Y.Z`. `git tag v1.0.0 && git push origin v1.0.0` → `publish` 워크플로. 같은 태그에 템플릿과 스크립트가 들어 있으므로 "플랫폼 vX.Y.Z로 생성"이 성립한다.

## 워크플로

- `ci.yml`: 빌드·테스트·로컬 퍼블리시 검증. 템플릿은 빌드하지 않는다(퍼블리시된 패키지가 있어야 빌드 가능)
- `publish.yml`: `v*` 태그 → GitHub Packages
- `release-app.yml`: `workflow_call`. 비즈니스 레포가 `uses: khkim6040/demo-c-platform/.github/workflows/release-app.yml@vX.Y.Z`로 호출. 이 레포의 `Dockerfile`·`.dockerignore`를 같은 커밋에서 가져다 쓴다

## 템플릿과 제너레이터

- `templates/multi-service/`: 비즈니스 모노레포 템플릿. 그 자체로 빌드 가능한 완전한 프로젝트(`rootProject.name = "demo-c-template"`, 패키지 `io.github.khkim6040.sample`)
- `tools/create-project.sh <이름> <패키지> [대상 경로]`: 커밋된 템플릿을 `git archive`로 꺼내 레포 이름·패키지를 치환하고 `git init` + 첫 커밋을 만든다. 치환이 남으면 실패한다. push는 사용자가 한다

```
git clone https://github.com/khkim6040/demo-c-platform.git   # 개발자당 1회
cd demo-c-platform
tools/create-project.sh demo-c-contract contract ../demo-c-contract
cd ../demo-c-contract && git remote add origin https://github.com/khkim6040/demo-c-contract.git && git push -u origin main
```

## 소비 측

`gradle.properties`의 `platformVersion` 하나로 카탈로그를 가져오고, 카탈로그 별칭 `libs.platform.bom`, `libs.platform.http.starter`를 쓴다. 컨벤션 플러그인(`build-logic`)은 템플릿에 복사되며 중앙 업데이트되지 않는다.

로컬 자격 증명: `~/.gradle/gradle.properties`에 `gpr.user`, `gpr.key`(`read:packages` 토큰).
```

```bash
cd /Users/gwanhokim/personal-projects/insurance-poc/demo-c-platform
git add README.md
git commit -q -m "Document platform artifacts, template and generator"
git log --oneline
```
Expected: 커밋 4개.

- [ ] **Step 2: push, CI, 태그, publish**

```bash
cd /Users/gwanhokim/personal-projects/insurance-poc/demo-c-platform
git push -q -u origin main
sleep 8
R=khkim6040/demo-c-platform
RUN=$(gh run list -R $R --workflow ci --limit 1 --json databaseId --jq '.[0].databaseId')
gh run watch -R $R --exit-status "$RUN" >/dev/null 2>&1
gh run view -R $R "$RUN" --json status,conclusion,url --jq '"ci: \(.status) \(.conclusion) \(.url)"'
git tag v1.0.0
git push -q origin v1.0.0
sleep 15
RUN=$(gh run list -R $R --workflow publish --limit 1 --json databaseId --jq '.[0].databaseId')
gh run watch -R $R --exit-status "$RUN" >/dev/null 2>&1
gh run view -R $R "$RUN" --json status,conclusion,url --jq '"publish: \(.status) \(.conclusion) \(.url)"'
git rev-parse --short v1.0.0
```
Expected: 둘 다 `completed success`. `v1.0.0` SHA를 Task 6에 적는다.

- [ ] **Step 3: 패키지 존재 확인**

```bash
BASE=https://maven.pkg.github.com/khkim6040/demo-c-platform/io/github/khkim6040/platform
for a in platform-bom/1.0.0/platform-bom-1.0.0.pom platform-catalog/1.0.0/platform-catalog-1.0.0.toml platform-http-starter/1.0.0/platform-http-starter-1.0.0.jar; do
  curl -sL -o /dev/null -w "%{http_code} $a\n" -u "khkim6040:$(gh auth token)" "$BASE/$a"
done
```
Expected: `200` 세 줄(302를 따라간 뒤).

---

### Task 5: demo-c-contract 생성 (실험 1-C 측정 구간)

**Files:**
- Create: `demo-c-contract/**` (스크립트 출력)

**Interfaces:**
- Consumes: Task 3의 스크립트, Task 4의 `1.0.0` 패키지와 `v1.0.0` 태그
- Produces: 실험 1 C 열의 수동 단계 목록. 이 Task에서 사람이 직접 친 명령만 센다

- [ ] **Step 1: 생성 (단계 ①)**

```bash
cd /Users/gwanhokim/personal-projects/insurance-poc/demo-c-platform
git status --short | wc -l
tools/create-project.sh demo-c-contract contract /Users/gwanhokim/personal-projects/insurance-poc/demo-c-contract
cd ../demo-c-contract
git log --oneline
git show --stat HEAD | tail -1
grep -rnIE 'demo-c-template|khkim6040[./]sample' . ; echo "leftover=$?"
grep -n platformVersion gradle.properties
grep -n 'uses:' .github/workflows/release.yml
```
Expected: 플랫폼 작업 트리 깨끗(`0`), `Generate demo-c-contract from demo-c-platform templates/multi-service@<v1.0.0 SHA>`, 파일 수 한 줄(기록용), `leftover=1`, `platformVersion=1.0.0`, `@v1.0.0`.

- [ ] **Step 2: 빌드와 네 앱 기동**

```bash
S=/private/tmp/claude-501/-Users-gwanhokim-personal-projects/4cd73c96-55d2-443e-ad6b-891bfc33231f/scratchpad
cd /Users/gwanhokim/personal-projects/insurance-poc/demo-c-contract
export JAVA_HOME=$(/usr/libexec/java_home -v 25)
./gradlew clean build --console=plain 2>&1 | grep -E 'BUILD|FAILED'
grep -ho 'tests="[0-9]*"' */*/build/test-results/test/*.xml | grep -o '[0-9]*' | paste -sd+ - | bc
./gradlew :apps:api:dependencies --configuration runtimeClasspath --console=plain -q | grep -E 'platform-http-starter|platform-bom' | head -3
for app in api admin consumer batch; do unzip -p apps/$app/build/libs/app.jar META-INF/MANIFEST.MF | grep Start-Class; done
(cd /Users/gwanhokim/personal-projects/insurance-poc/insurance-platform-poc && python3 -I tools/stub-server.py 9090 >/dev/null 2>&1) & STUB=$!
java -jar apps/api/build/libs/app.jar > $S/c-api.log 2>&1 & API=$!
for i in $(seq 1 20); do curl -s -o /dev/null localhost:8080/contracts/x && break; sleep 1; done
ID=$(curl -s -X POST localhost:8080/contracts -H 'Content-Type: application/json' \
  -d '{"holderName":"Kim","insuredAmount":10000000,"startDate":"2026-01-01","endDate":"2027-01-01"}' | sed 's/.*"id":"\([^"]*\)".*/\1/')
curl -s -i "localhost:8080/contracts/$ID/quote" | grep -E 'HTTP/|X-Correlation-Id|quotedPremium'
kill $API; pkill -f 'stub-server.py 9090' || true
java -jar apps/admin/build/libs/app.jar > $S/c-admin.log 2>&1 & ADMIN=$!
for i in $(seq 1 20); do curl -s -o /dev/null localhost:8081/admin/contracts && break; sleep 1; done
curl -s -o /dev/null -w '%{http_code}\n' -X POST localhost:8081/admin/contracts/C-1001/suspend
curl -s -o /dev/null -w '%{http_code}\n' -X POST localhost:8081/admin/contracts/C-1001/suspend
kill $ADMIN
java -jar apps/consumer/build/libs/app.jar > $S/c-consumer.log 2>&1 & C=$!
sleep 10; kill $C
echo "tomcat_lines=$(grep -c 'Tomcat' $S/c-consumer.log)"
grep -o 'event evt-[0-9]* -> [A-Z_]*' $S/c-consumer.log | head -3
java -jar apps/batch/build/libs/app.jar > $S/c-batch.log 2>&1; echo "batch exit=$?"
grep -o 'expired [0-9]* contract(s)' $S/c-batch.log
```
Expected: `BUILD SUCCESSFUL`, 테스트 `20`, `platform-http-starter:1.0.0`·`platform-bom:1.0.0`(저장소는 `demo-c-platform`), `Start-Class`가 `io.github.khkim6040.contract.<app>…` 네 줄, api `200` + `X-Correlation-Id` + `"quotedPremium":12000`, admin `200` 그리고 `409`, `tomcat_lines=0`, consumer 이벤트 3줄, `batch exit=0`, `expired 1 contract(s)`.

빌드가 실패하면: 원인이 템플릿이면 `demo-c-platform/templates/multi-service`를 고쳐 커밋하고 `v1.0.1`로 다시 퍼블리시한 뒤 `demo-c-contract`를 지우고 Step 1부터 다시 한다. 이 경우 관찰에 "템플릿 검증 공백이 실제로 비용을 냈다"고 적는다.

- [ ] **Step 3: push, CI, 태그 릴리스 (단계 ②)**

```bash
cd /Users/gwanhokim/personal-projects/insurance-poc/demo-c-contract
git remote add origin https://github.com/khkim6040/demo-c-contract.git
git push -q -u origin main
sleep 8
R=khkim6040/demo-c-contract
RUN=$(gh run list -R $R --workflow ci --limit 1 --json databaseId --jq '.[0].databaseId')
gh run watch -R $R --exit-status "$RUN" >/dev/null 2>&1
gh run view -R $R "$RUN" --json status,conclusion,url --jq '"ci: \(.status) \(.conclusion) \(.url)"'
grep -n 'newTag' deploy/overlays/dev/kustomization.yaml | head -1
git tag api-v0.1.0
git push -q origin api-v0.1.0
sleep 15
RUN=$(gh run list -R $R --workflow release --limit 1 --json databaseId --jq '.[0].databaseId')
gh run watch -R $R --exit-status "$RUN" >/dev/null 2>&1
gh run view -R $R "$RUN" --json status,conclusion,url --jq '"release: \(.status) \(.conclusion) \(.url)"'
gh run view -R $R "$RUN" --log 2>/dev/null | grep -oE 'job_workflow_sha[^"]*|ref: [0-9a-f]{40}' | head -2
docker manifest inspect ghcr.io/khkim6040/demo-c-contract/api:0.1.0 | grep -m1 '"digest"'
git status --short | wc -l
```
Expected: `ci: completed success`, `newTag: "0.1.0"`(템플릿 그대로라 수정 불필요), `release: completed success`, 다이제스트 한 줄, 작업 트리 깨끗(`0`). release가 실패하면 `gh run view -R $R <id> --log | grep -iE 'error|denied|401' | head`로 원인을 본다.

- [ ] **Step 4: 수동 단계 집계**

이 Task에서 사람이 친 명령은 두 묶음이다. 집계값을 Task 6에 옮긴다.

- ① `tools/create-project.sh demo-c-contract contract <경로>` (명령 1개. 스크립트가 치환한 파일: 이름 7 + `.kt` 23 = 30, 사람 손 0)
- ② `git remote add origin` + `git push -u origin main` + `git tag api-v0.1.0` + `git push origin api-v0.1.0`
- 손댄 파일 **0**. 전제 조건(개발자당 1회, B와 공통): `~/.gradle/gradle.properties` 토큰. C만의 전제: 플랫폼 레포 clone.

---

### Task 6: 실험 1 기록 (C 열)

**Files:**
- Modify: `insurance-platform-poc/experiments/01-create.md` (C 열 세 번째 칸들, 근거에 C 항목, 관찰에 C 항목)
- Modify: `insurance-platform-poc/docs/superpowers/plans/2026-10-24-phase4-c-platform-generator-contract.md` (체크박스)

- [ ] **Step 1: 결과 표 C 열 채우기**

`experiments/01-create.md` 결과 표의 각 행에서 마지막(C) 칸을 아래로 채운다. `<...>`는 Task 4·5의 실제 값으로 바꾼다.

| 항목 | C |
|---|---|
| 플랫폼 측 수동 단계 수 (목록) | 0 (템플릿·스크립트·아티팩트는 1회성 플랫폼 구축, baseline에 기록) |
| 프로젝트 측 수동 단계 수, 프로젝트 1개당 (목록) | 2: ① `tools/create-project.sh demo-c-contract contract <경로>` 한 명령(템플릿 추출·이름 치환 7파일·패키지 치환 `.kt` 23 + 디렉터리 10·`git init`·첫 커밋을 스크립트가 수행) ② `remote add` + push + 태그. 손댄 파일 **0**. 별도로 개발자 환경 1회: `~/.gradle/gradle.properties` 토큰(B와 공통) + 플랫폼 레포 clone(C만) |
| 머지 충돌 파일 수 | 0 (머지 개념 없음) |
| 의미적 충돌 (빌드·테스트 실패, 동작 변화) | 없음. `clean build` 통과, 테스트 20개 |
| 함께 끌려온 무관한 변경 수 | 해당 없음. 커밋 1개, 태그 없음. 커밋 메시지에 원본 플랫폼 커밋(`templates/multi-service@<v1.0.0 SHA>`)이 남는다 |
| 검증 방법과 결과 | B와 같은 기동 검증 통과, `runtimeClasspath`에 `platform-http-starter:1.0.0`·`platform-bom:1.0.0`(`demo-c-platform` 패키지), CI 성공, reusable `release-app.yml@v1.0.0`(demo-c-platform)로 `api:0.1.0` 푸시 |

- [ ] **Step 2: 근거와 관찰 추가**

근거 절에 추가:

```markdown
- C: https://github.com/khkim6040/demo-c-contract — 생성 커밋 `<sha>`(`Generate demo-c-contract from demo-c-platform templates/multi-service@<v1.0.0 sha>`), ci https://github.com/khkim6040/demo-c-contract/actions/runs/<id>, release https://github.com/khkim6040/demo-c-contract/actions/runs/<id>, 이미지 `ghcr.io/khkim6040/demo-c-contract/api:0.1.0` (digest `sha256:<12자>`). 플랫폼: https://github.com/khkim6040/demo-c-platform `v1.0.0` = `<sha>`, publish https://github.com/khkim6040/demo-c-platform/actions/runs/<id>
```

관찰 절에 추가(실행 중 드러난 사실로 보강한다):

```markdown
- C: B안의 수동 단계 ②(패키지 치환)·③(이름 `sed`)이 스크립트로 들어가 프로젝트 측 단계가 4 → 2, 손댄 파일 30 → 0이 됐다. 스크립트 끝의 잔여 자리표시자 검사가 치환 누락을 생성 시점에 잡는다.
- C: 생성에 플랫폼 레포 clone이 필요하다. GitHub Template(B)은 브라우저·`gh`만으로 되지만, C는 "플랫폼 레포를 받아서 스크립트를 실행"하는 전제가 붙는다. 대신 템플릿이 플랫폼 태그에 묶여 "v1.0.0에서 생성됨"이 커밋 메시지에 남는다. B는 템플릿 레포의 어느 커밋에서 생성됐는지 기록이 없다.
- C: 템플릿이 플랫폼 레포 안에 있지만 플랫폼 CI가 템플릿을 빌드하지 않는다. 퍼블리시 전에는 템플릿이 참조하는 패키지가 없어 빌드할 수 없기 때문이다(닭과 달걀). 템플릿이 깨져도 생성된 프로젝트의 첫 빌드에서야 드러난다. 보완책(publish 후 템플릿 빌드 잡, 또는 `mavenLocal` init script)은 실험 7·8에서 템플릿 변경이 생길 때 필요성을 본다.
- C: 스크립트는 커밋된 템플릿만 쓴다(`git archive HEAD`). 템플릿을 고치고 커밋을 잊으면 옛 템플릿으로 생성된다. 생성 커밋 메시지의 SHA로 사후 확인은 된다.
- C: 빈 레포가 미리 있어도 문제없다(B와 반대). 스크립트는 로컬에만 쓰고 push는 사용자가 하므로 부트스트랩이 레포를 먼저 만드는 운영 방식과 맞는다.
- C: 플랫폼 버전 숫자 두 개(`platformVersion`, `@v`) 문제는 B와 동일하다. 템플릿이 `v1.0.0` 태그에서 나오므로 생성 시점에는 두 숫자가 자동으로 일치하지만, 이후 올릴 때는 B와 같은 두 곳 수정이다.
```

- [ ] **Step 3: 계획 체크박스 반영 후 커밋**

```bash
cd /Users/gwanhokim/personal-projects/insurance-poc/insurance-platform-poc
git add experiments/01-create.md
git commit -q -m "Record experiment 1 result for C"
git add docs/superpowers/plans/2026-10-24-phase4-c-platform-generator-contract.md
git commit -q -m "Mark Phase 4 plan complete"
git push -q origin main
git log --oneline | head -3
for d in demo-c-platform demo-c-contract insurance-platform-poc; do echo "$d: $(git -C ../$d status --short | wc -l | tr -d ' ') uncommitted"; done
```
Expected: 커밋 2개 push, 세 레포 모두 `0 uncommitted`.

---

## 자체 점검 결과

- **스펙 커버리지**: 3장 `demo-c-platform` = B 코드 + `templates/multi-service/` + `tools/create-project.sh` → Task 1~3. `demo-c-contract` = 스크립트 결과 push → Task 5. 4.4 "demo-c-platform은 여기에 templates/ + tools/ 추가" → Task 2~3. 5.5 "B/C는 생성 시 치환" → Task 3 스크립트(C에서는 진짜로 생성 시점에 치환됨). 6.2 B/C `release.yml` 한 줄 호출 → 템플릿 그대로(`demo-c-platform@v1.0.0`). 6.5 publish·자격 증명 → Task 4, 템플릿 `settings.gradle.kts`. 7.2 실험 1 → Task 5 측정, Task 6 기록. 9장 Phase 4 완료 기준 "스크립트 한 번으로 생성된 프로젝트 빌드·기동" → Task 5 Step 1~2. 11장 "B와 C의 차이는 템플릿 전달 방식뿐" → 아티팩트·워크플로를 B에서 바이트 복사해 그 전제를 유지.
- **자리표시자**: 코드 블록은 전체 내용. `<...>`는 실행 중 얻는 실제 값(SHA, run id, digest) 자리이며 Task 6 Step 1~2에만 있다.
- **일관성**: 치환 대상 문자열(`demo-c-template`, `io.github.khkim6040.sample`)이 Task 2 Produces, Task 3 스크립트, Task 3 검증 grep, Task 5 Step 1 grep에서 같다. 스크립트 인자 순서 `<repo-name> <package-segment> [dest-dir]`가 Task 3·4 README·5에서 같다. 플랫폼 커밋 4개(모듈/템플릿/스크립트/README), 태그 `v1.0.0`은 README 커밋 뒤에 찍는다.
- **알려진 위험**: 템플릿을 퍼블리시 전에 빌드로 검증하지 못한다(Global Constraints). 템플릿이 검증된 B 템플릿의 복사본이고 바뀐 것은 레포 URL 세 곳뿐이라 수용한다. 실패 시 경로는 Task 5 Step 2에 적었다.
