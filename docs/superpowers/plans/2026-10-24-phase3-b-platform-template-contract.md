# Phase 3: B안(퍼블리시 + 템플릿) 구현 계획

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `demo-b-platform`이 BOM·버전 카탈로그·`platform-http-starter`를 GitHub Packages에 `1.0.0`으로 퍼블리시하고 reusable 릴리스 워크플로를 제공하며, `demo-b-template`(GitHub Template 레포)에서 생성한 `demo-b-contract`가 그 아티팩트만으로 빌드·기동·CI·이미지 푸시까지 되는 것을 확인한 뒤 실험 1(B)를 기록한다.

**Architecture:** 플랫폼 레포는 세 모듈(`platform-bom`, `platform-catalog`, `platform-http-starter`)을 `maven-publish`로 GitHub Packages에 올린다. 비즈니스 레포는 `gradle.properties`의 `platformVersion` 숫자 하나로 카탈로그를 가져오고, 카탈로그 안의 별칭으로 BOM과 스타터 버전을 얻는다. 컨벤션 플러그인(`build-logic`)은 스펙대로 템플릿에 **복사**되며, A안과 다른 점은 Boot BOM 대신 플랫폼 BOM을 적용하는 한 줄뿐이다. 릴리스는 비즈니스 레포의 `release.yml`이 플랫폼의 `release-app.yml@v1.0.0`을 호출하고, 그 워크플로가 플랫폼 레포를 같은 커밋으로 checkout해 Dockerfile과 `.dockerignore`를 가져다 쓴다.

**Tech Stack:** Gradle 9.7.0 `java-platform`·`version-catalog`·`maven-publish` 플러그인, GitHub Packages(Maven), GitHub Template repository, GitHub Actions reusable workflow(`workflow_call`), 나머지는 Phase 1과 동일(JDK 25, Kotlin 2.4.21, Spring Boot 4.1.2, GHCR, `kubectl kustomize`).

**Spec:** `docs/superpowers/specs/2026-10-24-insurance-platform-poc-design.md` (3장 레포 구성, 4.1·4.4 아티팩트, 5.5 패키지, 6.1~6.5 CI·배포, 7.1~7.2 실험 1, 9장 Phase 3)

## Global Constraints

- 모든 레포는 `/Users/gwanhokim/personal-projects/insurance-poc/<레포>` 아래에 둔다. 이 계획은 `demo-b-platform`, `demo-b-template`, `demo-b-contract` 세 디렉터리를 만들고, 기록은 `insurance-platform-poc`에 쓴다.
- 모든 Gradle·java 명령은 `export JAVA_HOME=$(/usr/libexec/java_home -v 25)` 후 실행한다.
- 버전: Spring Boot `4.1.2`, Kotlin `2.4.21`, Gradle `9.7.0`, JDK `25`. 플랫폼 아티팩트 버전은 git 태그 `v1.0.0`에서 나온 `1.0.0`. Group ID `io.github.khkim6040.platform`.
- 아티팩트 세 개: `platform-bom`(java-platform), `platform-catalog`(version-catalog), `platform-http-starter`(jar). 저장소 `https://maven.pkg.github.com/khkim6040/demo-b-platform`.
- **한 번만 작성 원칙**: 스타터·도메인·앱 소스·`deploy/`·컨벤션 플러그인은 `demo-a-platform`에서 `cp`로 복사한다. 바뀌는 파일만 이 계획에 전체 내용을 적는다. 복사 원본은 `demo-a-platform` 커밋 `95d383a`.
- 비즈니스 레포가 올리는 숫자는 `gradle.properties`의 `platformVersion` **하나**다. 루트 `settings.gradle.kts`와 `build-logic/settings.gradle.kts`가 모두 이 값을 읽는다.
- GitHub Packages는 공개 패키지도 토큰이 필요하다. 로컬은 `~/.gradle/gradle.properties`의 `gpr.user`/`gpr.key`, CI는 `GITHUB_ACTOR`/`GITHUB_TOKEN` 환경 변수. Gradle 설정은 두 출처를 `orElse`로 묶는다.
- 템플릿 패키지는 `io.github.khkim6040.sample.*`로 두고, 생성 후 프로젝트가 `io.github.khkim6040.contract.*`로 치환한다(스펙 5.5 "B/C는 생성 시 치환": GitHub Template은 치환 기능이 없으므로 생성 직후 수동 단계로 수행하고 실험 1에 센다).
- B안 비즈니스 레포에는 upstream 소유 파일이 없다. 생성 후 모든 파일이 프로젝트 소유다.
- 커밋 메시지는 영어 제목 한 줄. 본문·Co-Authored-By 없음. 빌드가 깨진 상태로 커밋하지 않는다.
- 외부 서비스에 쓰는 행동(push, 태그, 패키지·이미지 퍼블리시, 템플릿 지정, `demo-b-contract` 빈 레포 삭제 후 템플릿으로 재생성)은 스펙과 이 계획의 승인 범위다. `demo-b-contract`는 Phase 0이 빈 레포로 미리 만들어 두었는데, GitHub 템플릿 생성은 기존 레포를 대상으로 할 수 없으므로 빈 레포를 지우고 다시 만든다(Task 7).
- `gh`는 리모트가 하나뿐인 레포에서도 항상 `-R khkim6040/<레포>`를 명시한다(Phase 2 관찰).
- 실험 1의 측정값은 "수동 단계 수(목록)"다. Task 7에서 사람이 손댄 단계와 파일 수를 세어 Task 8에 적는다. 플랫폼 구축(Task 2~6)은 1회성 비용이므로 실험 1이 아니라 `00-baseline.md`(Phase 5)에 들어간다.

---

## 파일 구조

### demo-b-platform

| 파일 | 책임 | 출처 |
|---|---|---|
| `settings.gradle.kts` | `includeBuild("build-logic")`, 모듈 3개 include | 신규 |
| `build.gradle.kts` | 모든 서브프로젝트에 group·version·GitHub Packages 퍼블리시 저장소 | 신규 |
| `gradle.properties`, `.gitignore`, `gradle/wrapper/*`, `gradlew*` | Phase 1과 동일 | 복사 |
| `gradle/libs.versions.toml` | 버전 단일 출처. 카탈로그 아티팩트의 원본 | 복사 |
| `build-logic/**` | 컨벤션 플러그인 2개 (A안과 동일) | 복사 |
| `platform-bom/build.gradle.kts` | `spring-boot-dependencies` import + 스타터 버전 제약 | 신규 |
| `platform-catalog/build.gradle.kts` | toml 파일 + `platform` 버전 별칭 + BOM·스타터 라이브러리 별칭 | 신규 |
| `platform-http-starter/**` | A안 `platform/http-starter` + 퍼블리케이션 선언 | 복사 + 수정 |
| `Dockerfile`, `.dockerignore` | 비즈니스 레포의 릴리스 워크플로가 checkout해서 쓴다 | 복사 |
| `.github/workflows/ci.yml` | main push/PR: `build publishToMavenLocal` | 신규 |
| `.github/workflows/publish.yml` | `v*` 태그: `publish -PplatformVersion` | 신규 |
| `.github/workflows/release-app.yml` | `workflow_call`: 비즈니스 레포 앱 이미지 빌드·푸시 | 신규 |
| `README.md` | 아티팩트·워크플로 사용법 | 신규 |

### demo-b-template

| 파일 | 책임 | 출처 |
|---|---|---|
| `settings.gradle.kts` | GitHub Packages 저장소 + 카탈로그 `from(artifact)` + 모듈 include | 신규 |
| `gradle.properties` | `platformVersion=1.0.0` + 빌드 옵션 | 신규 |
| `build-logic/settings.gradle.kts` | 루트 `gradle.properties`의 `platformVersion`으로 같은 카탈로그 import | 신규 |
| `build-logic/build.gradle.kts`, `platform.spring-boot-app.gradle.kts` | A안과 동일 | 복사 |
| `build-logic/src/main/kotlin/platform.kotlin-library.gradle.kts` | `libs.platform.bom` 적용, `repositories {}` 제거 | 수정 |
| `libs/domain/**`, `apps/*/src/**`, `apps/{consumer,batch}/build.gradle.kts`, `deploy/**`, `.gitignore`, wrapper | A안과 동일 | 복사 |
| `apps/{api,admin}/build.gradle.kts` | `project(":platform:http-starter")` → `libs.platform.http.starter` | 수정 |
| `deploy/base/*/`, `deploy/overlays/dev/kustomization.yaml` | 이미지 이름 `demo-b-template`, 네임스페이스 `demo-b-template-dev` | 복사 + sed |
| `.github/workflows/ci.yml` | A안 + `GITHUB_TOKEN` 환경 변수 | 수정 |
| `.github/workflows/release.yml` | `uses: khkim6040/demo-b-platform/.github/workflows/release-app.yml@v1.0.0` | 신규 |
| `README.md` | 생성 후 절차 안내 | 신규 |

`Dockerfile`과 `.dockerignore`는 템플릿에 없다(플랫폼이 공급).

### demo-b-contract

템플릿에서 생성한 뒤 패키지 치환과 레포 이름 치환만 한다. 신규 파일 없음.

### insurance-platform-poc

| 파일 | 책임 |
|---|---|
| `experiments/01-create.md` | B 열 채움 |

---

### Task 1: GitHub 토큰 스코프와 로컬 Gradle 자격 증명

**Files:**
- Modify: `~/.gradle/gradle.properties` (없으면 생성)

**Interfaces:**
- Produces: `gh auth token`이 `read:packages`, `delete_repo` 스코프를 가진다. `~/.gradle/gradle.properties`에 `gpr.user=khkim6040`, `gpr.key=<token>`. 이후 모든 Gradle 빌드가 GitHub Packages를 읽을 수 있다.

- [ ] **Step 1: 스코프 추가 (사용자가 직접 실행, 브라우저 인증)**

이 단계는 대화형이라 에이전트가 실행할 수 없다. 사용자가 프롬프트에 다음을 입력한다.
```bash
! gh auth refresh -h github.com -s read:packages,delete_repo
```
Expected: 브라우저 인증 후 `✓ Authentication complete.`

- [ ] **Step 2: 스코프 확인**

```bash
gh auth status 2>&1 | grep -E 'Token scopes'
```
Expected: `read:packages`와 `delete_repo`가 목록에 있다.

- [ ] **Step 3: Gradle 자격 증명 파일**

```bash
mkdir -p ~/.gradle
touch ~/.gradle/gradle.properties
grep -q '^gpr.user=' ~/.gradle/gradle.properties || printf 'gpr.user=khkim6040\n' >> ~/.gradle/gradle.properties
grep -q '^gpr.key=' ~/.gradle/gradle.properties || printf 'gpr.key=%s\n' "$(gh auth token)" >> ~/.gradle/gradle.properties
grep -c '^gpr\.' ~/.gradle/gradle.properties
```
Expected: `2`. 토큰 값은 출력하지 않는다. 커밋 없음.

### Task 2: demo-b-platform 골격과 퍼블리시 설정

**Files:**
- Create: `demo-b-platform/settings.gradle.kts`
- Create: `demo-b-platform/build.gradle.kts`
- Copy: `demo-b-platform/{gradle.properties,.gitignore,gradlew,gradlew.bat,gradle/wrapper/*,gradle/libs.versions.toml,build-logic/**}` ← `demo-a-platform`

**Interfaces:**
- Produces: 루트 프로젝트 `demo-b-platform`, 서브프로젝트 `platform-bom`·`platform-catalog`·`platform-http-starter`(디렉터리만). 모든 서브프로젝트의 `group = io.github.khkim6040.platform`, `version = -PplatformVersion` 또는 `0.0.0-LOCAL`, `maven-publish`가 적용된 모듈에 `GitHubPackages` 저장소. 플러그인 id `platform.kotlin-library`, `platform.spring-boot-app`, 카탈로그 별칭 `libs.spring.boot.bom`.

- [ ] **Step 1: 레포 초기화와 복사**

```bash
A=/Users/gwanhokim/personal-projects/insurance-poc/demo-a-platform
B=/Users/gwanhokim/personal-projects/insurance-poc/demo-b-platform
mkdir -p $B && cd $B
git init -q -b main
git remote add origin https://github.com/khkim6040/demo-b-platform.git
cp $A/gradle.properties $A/.gitignore $A/gradlew $A/gradlew.bat .
mkdir -p gradle && cp -R $A/gradle/wrapper $A/gradle/libs.versions.toml gradle/
cp -R $A/build-logic .
rm -rf build-logic/build build-logic/.gradle build-logic/.kotlin
mkdir -p platform-bom platform-catalog platform-http-starter
ls -a; ls build-logic build-logic/src/main/kotlin
```
Expected: `build-logic/src/main/kotlin`에 `platform.kotlin-library.gradle.kts`, `platform.spring-boot-app.gradle.kts`.

- [ ] **Step 2: 루트 설정**

`settings.gradle.kts`:
```kotlin
pluginManagement {
    includeBuild("build-logic")
}

rootProject.name = "demo-b-platform"

include(
    "platform-bom",
    "platform-catalog",
    "platform-http-starter",
)
```

`build.gradle.kts`:
```kotlin
// Shared publishing setup. Each module declares its own publication; this block
// gives every module the same coordinates and the GitHub Packages repository.
subprojects {
    group = "io.github.khkim6040.platform"
    version = providers.gradleProperty("platformVersion").orElse("0.0.0-LOCAL").get()

    repositories {
        mavenCentral()
    }

    plugins.withId("maven-publish") {
        configure<PublishingExtension> {
            repositories {
                maven {
                    name = "GitHubPackages"
                    setUrl("https://maven.pkg.github.com/khkim6040/demo-b-platform")
                    credentials {
                        username = providers.gradleProperty("gpr.user")
                            .orElse(providers.environmentVariable("GITHUB_ACTOR")).orNull
                        password = providers.gradleProperty("gpr.key")
                            .orElse(providers.environmentVariable("GITHUB_TOKEN")).orNull
                    }
                }
            }
        }
    }
}
```

- [ ] **Step 3: 설정 로드 확인**

```bash
cd /Users/gwanhokim/personal-projects/insurance-poc/demo-b-platform
export JAVA_HOME=$(/usr/libexec/java_home -v 25)
./gradlew projects --console=plain 2>&1 | grep -E "Project ':|BUILD"
```
Expected: `platform-bom`, `platform-catalog`, `platform-http-starter` 세 줄과 `BUILD SUCCESSFUL`.

- [ ] **Step 4: 커밋**

```bash
cd /Users/gwanhokim/personal-projects/insurance-poc/demo-b-platform
git add -A
git commit -q -m "Add Gradle skeleton with shared publishing configuration"
git log --oneline -1
```

### Task 3: platform-http-starter 복사와 퍼블리케이션

**Files:**
- Copy: `demo-b-platform/platform-http-starter/src/**` ← `demo-a-platform/platform/http-starter/src/**`
- Create: `demo-b-platform/platform-http-starter/build.gradle.kts`

**Interfaces:**
- Consumes: Task 2의 플러그인과 퍼블리시 저장소.
- Produces: 아티팩트 `io.github.khkim6040.platform:platform-http-starter:<version>`. POM의 compile 의존성에 `spring-boot-starter-webmvc`, `spring-boot-starter-restclient`, `jackson-module-kotlin`, `kotlin-reflect`; `dependencyManagement`에 `spring-boot-dependencies` import. 동작은 Phase 1과 같다(Correlation ID, ProblemDetail, `platform-defaults.yml`).

- [ ] **Step 1: 소스 복사**

```bash
A=/Users/gwanhokim/personal-projects/insurance-poc/demo-a-platform
cd /Users/gwanhokim/personal-projects/insurance-poc/demo-b-platform
cp -R $A/platform/http-starter/src platform-http-starter/
find platform-http-starter -type f | sort
```
Expected: main 5 Kotlin + 3 리소스, test 2 Kotlin = 파일 10개.

- [ ] **Step 2: 빌드 파일**

`platform-http-starter/build.gradle.kts`:
```kotlin
plugins {
    id("platform.kotlin-library")
    `maven-publish`
}

dependencies {
    api("org.springframework.boot:spring-boot-starter-webmvc")
    api("org.springframework.boot:spring-boot-starter-restclient")
    api("tools.jackson.module:jackson-module-kotlin")
    api("org.jetbrains.kotlin:kotlin-reflect")

    testImplementation("org.springframework.boot:spring-boot-starter-test")
    testImplementation("org.springframework.boot:spring-boot-starter-webmvc-test")
}

publishing {
    publications {
        create<MavenPublication>("starter") {
            from(components["java"])
        }
    }
}
```

- [ ] **Step 3: 테스트와 로컬 퍼블리시로 검증**

```bash
cd /Users/gwanhokim/personal-projects/insurance-poc/demo-b-platform
export JAVA_HOME=$(/usr/libexec/java_home -v 25)
./gradlew :platform-http-starter:test :platform-http-starter:publishToMavenLocal -PplatformVersion=0.0.1-LOCAL --console=plain 2>&1 | grep -E 'BUILD|FAILED'
grep -ho 'tests="[0-9]*"\|failures="[0-9]*"' platform-http-starter/build/test-results/test/*.xml
POM=~/.m2/repository/io/github/khkim6040/platform/platform-http-starter/0.0.1-LOCAL/platform-http-starter-0.0.1-LOCAL.pom
grep -c '<artifactId>spring-boot-starter-webmvc</artifactId>' $POM
grep -A3 '<dependencyManagement>' $POM | grep -c 'spring-boot-dependencies'
```
Expected: `BUILD SUCCESSFUL`, `tests="5"`, `failures="0"`, `1`, `1`.

- [ ] **Step 4: 커밋**

```bash
cd /Users/gwanhokim/personal-projects/insurance-poc/demo-b-platform
git add platform-http-starter
git commit -q -m "Add platform-http-starter module with Maven publication"
git log --oneline -1
```

### Task 4: platform-bom과 platform-catalog

**Files:**
- Create: `demo-b-platform/platform-bom/build.gradle.kts`
- Create: `demo-b-platform/platform-catalog/build.gradle.kts`

**Interfaces:**
- Consumes: `gradle/libs.versions.toml`(Task 2), 스타터 좌표(Task 3).
- Produces:
  - `io.github.khkim6040.platform:platform-bom:<version>`: `spring-boot-dependencies:4.1.2` import + `platform-http-starter:<version>` 제약.
  - `io.github.khkim6040.platform:platform-catalog:<version>`(toml): `libs.versions.toml`의 모든 항목 + `[versions] platform = "<version>"` + `[libraries] platform-bom`, `platform-http-starter`(`version.ref = "platform"`). 소비 측 접근자: `libs.platform.bom`, `libs.platform.http.starter`, `libs.versions.platform`.

- [ ] **Step 1: BOM**

`platform-bom/build.gradle.kts`:
```kotlin
plugins {
    `java-platform`
    `maven-publish`
}

javaPlatform {
    allowDependencies()
}

dependencies {
    api(platform(libs.spring.boot.bom))
    constraints {
        api("io.github.khkim6040.platform:platform-http-starter:${project.version}")
    }
}

publishing {
    publications {
        create<MavenPublication>("bom") {
            from(components["javaPlatform"])
        }
    }
}
```

- [ ] **Step 2: 카탈로그**

`platform-catalog/build.gradle.kts`:
```kotlin
plugins {
    `version-catalog`
    `maven-publish`
}

catalog {
    versionCatalog {
        from(files("../gradle/libs.versions.toml"))
        version("platform", project.version.toString())
        library("platform-bom", "io.github.khkim6040.platform", "platform-bom").versionRef("platform")
        library("platform-http-starter", "io.github.khkim6040.platform", "platform-http-starter").versionRef("platform")
    }
}

publishing {
    publications {
        create<MavenPublication>("catalog") {
            from(components["versionCatalog"])
        }
    }
}
```

- [ ] **Step 3: 로컬 퍼블리시로 내용 검증**

```bash
cd /Users/gwanhokim/personal-projects/insurance-poc/demo-b-platform
export JAVA_HOME=$(/usr/libexec/java_home -v 25)
./gradlew publishToMavenLocal -PplatformVersion=0.0.1-LOCAL --console=plain 2>&1 | grep -E 'BUILD|FAILED'
M=~/.m2/repository/io/github/khkim6040/platform
ls $M
grep -E 'spring-boot-dependencies|platform-http-starter|<version>' $M/platform-bom/0.0.1-LOCAL/platform-bom-0.0.1-LOCAL.pom | sed 's/^ *//' | sort -u
T=$M/platform-catalog/0.0.1-LOCAL/platform-catalog-0.0.1-LOCAL.toml
grep -E '^platform|^kotlin|^spring-boot ' $T
```
Expected: 디렉터리 3개. BOM pom에 `spring-boot-dependencies`, `<version>4.1.2</version>`, `platform-http-starter`, `<version>0.0.1-LOCAL</version>`. toml에 `platform = "0.0.1-LOCAL"`, `kotlin = "2.4.21"`, `spring-boot = "4.1.2"`, `platform-bom = {…}`, `platform-http-starter = {…}`.

- [ ] **Step 4: 커밋**

```bash
cd /Users/gwanhokim/personal-projects/insurance-poc/demo-b-platform
git add platform-bom platform-catalog
git commit -q -m "Add platform BOM and version catalog modules"
git log --oneline -1
```

### Task 5: 플랫폼 워크플로, Dockerfile, README

**Files:**
- Copy: `demo-b-platform/Dockerfile`, `demo-b-platform/.dockerignore` ← `demo-a-platform`
- Create: `demo-b-platform/.github/workflows/ci.yml`
- Create: `demo-b-platform/.github/workflows/publish.yml`
- Create: `demo-b-platform/.github/workflows/release-app.yml`
- Create: `demo-b-platform/README.md`

**Interfaces:**
- Produces:
  - `ci`: main push/PR에 `./gradlew build publishToMavenLocal`.
  - `publish`: `v*` 태그 push → 세 아티팩트를 GitHub Packages에 `<태그에서 v 제거>` 버전으로 퍼블리시.
  - `release-app`(`workflow_call`, 입력 없음): 호출 레포의 `<app>-v<semver>` 태그를 파싱 → 호출 레포 checkout → 플랫폼 레포를 `github.job_workflow_sha`(호출 측 `@v1.0.0`이 가리키는 커밋)로 `platform/`에 checkout → `./gradlew :apps:<app>:bootJar`(GitHub Packages 읽기용 `GITHUB_TOKEN`) → `platform/.dockerignore`를 루트로 복사 → `platform/Dockerfile`로 빌드 → `ghcr.io/<호출 레포>/<app>:<semver>` 푸시, 라벨 `org.opencontainers.image.revision=<호출 레포 sha>`.

- [ ] **Step 1: Dockerfile 복사**

```bash
A=/Users/gwanhokim/personal-projects/insurance-poc/demo-a-platform
cd /Users/gwanhokim/personal-projects/insurance-poc/demo-b-platform
cp $A/Dockerfile $A/.dockerignore .
cat Dockerfile .dockerignore
```
Expected: Phase 1과 동일한 4줄 + 2줄.

- [ ] **Step 2: ci.yml**

`.github/workflows/ci.yml`:
```yaml
name: ci
on:
  push:
    branches: [main]
  pull_request:

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v7
      - uses: actions/setup-java@v6
        with:
          distribution: temurin
          java-version: "25"
      - uses: gradle/actions/setup-gradle@v6
      - run: ./gradlew build publishToMavenLocal -PplatformVersion=0.0.0-CI --console=plain
```

- [ ] **Step 3: publish.yml**

`.github/workflows/publish.yml`:
```yaml
name: publish
on:
  push:
    tags: ["v*"]

permissions:
  contents: read
  packages: write

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v7
      - uses: actions/setup-java@v6
        with:
          distribution: temurin
          java-version: "25"
      - uses: gradle/actions/setup-gradle@v6
      - run: ./gradlew publish -PplatformVersion="${GITHUB_REF_NAME#v}" --console=plain
        env:
          GITHUB_ACTOR: ${{ github.actor }}
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

- [ ] **Step 4: release-app.yml**

`.github/workflows/release-app.yml`:
```yaml
name: release-app
on:
  workflow_call:

jobs:
  image:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
    steps:
      - uses: actions/checkout@v7
      - name: Checkout platform at the same ref as this workflow
        uses: actions/checkout@v7
        with:
          repository: khkim6040/demo-b-platform
          ref: ${{ github.job_workflow_sha }}
          path: platform
      - name: Parse app and version from tag
        id: tag
        run: |
          echo "app=${GITHUB_REF_NAME%-v*}" >> "$GITHUB_OUTPUT"
          echo "version=${GITHUB_REF_NAME##*-v}" >> "$GITHUB_OUTPUT"
      - uses: actions/setup-java@v6
        with:
          distribution: temurin
          java-version: "25"
      - uses: gradle/actions/setup-gradle@v6
      - run: ./gradlew :apps:${{ steps.tag.outputs.app }}:bootJar --console=plain
        env:
          GITHUB_ACTOR: ${{ github.actor }}
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      - name: Use platform Dockerfile and dockerignore
        run: cp platform/.dockerignore .dockerignore
      - uses: docker/login-action@v4
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      - uses: docker/build-push-action@v7
        with:
          context: .
          file: platform/Dockerfile
          push: true
          build-args: APP=${{ steps.tag.outputs.app }}
          tags: ghcr.io/${{ github.repository }}/${{ steps.tag.outputs.app }}:${{ steps.tag.outputs.version }}
          labels: org.opencontainers.image.revision=${{ github.sha }}
```

- [ ] **Step 5: README**

`README.md`:
```markdown
# demo-b-platform

Insurance platform PoC, B안(퍼블리시 + 템플릿)의 플랫폼 레포.

## 퍼블리시 아티팩트 (GitHub Packages, group `io.github.khkim6040.platform`)

| 아티팩트 | 내용 |
|---|---|
| `platform-bom` | `spring-boot-dependencies` import + 플랫폼 스타터 버전 제약. 전이 의존성 버전 강제 수단 |
| `platform-catalog` | `gradle/libs.versions.toml` + `platform` 버전 별칭 + `platform-bom`·`platform-http-starter` 라이브러리 별칭. 플러그인 버전의 중앙 출처 |
| `platform-http-starter` | Correlation ID 필터, ProblemDetail 핸들러, `platform-defaults.yml` |

버전은 git 태그 `vX.Y.Z` = 아티팩트 `X.Y.Z`. `git tag v1.0.0 && git push origin v1.0.0` → `publish` 워크플로.

## 워크플로

- `ci.yml`: 빌드·테스트·로컬 퍼블리시 검증
- `publish.yml`: `v*` 태그 → GitHub Packages
- `release-app.yml`: `workflow_call`. 비즈니스 레포가 `uses: khkim6040/demo-b-platform/.github/workflows/release-app.yml@vX.Y.Z`로 호출. 이 레포의 `Dockerfile`·`.dockerignore`를 같은 커밋에서 가져다 쓴다

## 소비 측 (demo-b-template 참고)

`gradle.properties`의 `platformVersion` 하나로 카탈로그를 가져오고, 카탈로그 별칭 `libs.platform.bom`, `libs.platform.http.starter`를 쓴다. 컨벤션 플러그인(`build-logic`)은 템플릿에 복사되며 중앙 업데이트되지 않는다.

로컬 자격 증명: `~/.gradle/gradle.properties`에 `gpr.user`, `gpr.key`(`read:packages` 토큰).
```

- [ ] **Step 6: 커밋, push, CI, 태그 퍼블리시**

```bash
cd /Users/gwanhokim/personal-projects/insurance-poc/demo-b-platform
git add -A
git commit -q -m "Add CI, publish and reusable release workflows"
git push -q -u origin main
sleep 8
R=khkim6040/demo-b-platform
RUN=$(gh run list -R $R --workflow ci --limit 1 --json databaseId --jq '.[0].databaseId')
gh run watch -R $R --exit-status "$RUN" >/dev/null 2>&1
gh run view -R $R "$RUN" --json status,conclusion,url --jq '"ci: \(.status) \(.conclusion) \(.url)"'
git tag v1.0.0
git push -q origin v1.0.0
sleep 15
RUN=$(gh run list -R $R --workflow publish --limit 1 --json databaseId --jq '.[0].databaseId')
gh run watch -R $R --exit-status "$RUN" >/dev/null 2>&1
gh run view -R $R "$RUN" --json status,conclusion,url --jq '"publish: \(.status) \(.conclusion) \(.url)"'
```
Expected: 둘 다 `completed success`.

- [ ] **Step 7: 패키지 존재 확인**

```bash
BASE=https://maven.pkg.github.com/khkim6040/demo-b-platform/io/github/khkim6040/platform
for a in platform-bom/1.0.0/platform-bom-1.0.0.pom platform-catalog/1.0.0/platform-catalog-1.0.0.toml platform-http-starter/1.0.0/platform-http-starter-1.0.0.jar; do
  curl -s -o /dev/null -w "%{http_code} $a\n" -u "khkim6040:$(gh auth token)" "$BASE/$a"
done
```
Expected: `200` 세 줄. (401/404면 publish 로그를 본다. 토큰에 `read:packages`가 없으면 Task 1부터 다시.)

### Task 6: demo-b-template

**Files:**
- Create: `demo-b-template/settings.gradle.kts`
- Create: `demo-b-template/gradle.properties`
- Create: `demo-b-template/build-logic/settings.gradle.kts`
- Modify(복사 후): `demo-b-template/build-logic/src/main/kotlin/platform.kotlin-library.gradle.kts`
- Modify(복사 후): `demo-b-template/apps/api/build.gradle.kts`, `demo-b-template/apps/admin/build.gradle.kts`
- Modify(복사 후 sed): `demo-b-template/deploy/**`
- Create: `demo-b-template/.github/workflows/ci.yml`, `release.yml`
- Create: `demo-b-template/README.md`
- Copy: 나머지(`.gitignore`, wrapper, `build-logic/build.gradle.kts`, `platform.spring-boot-app.gradle.kts`, `libs/domain/**`, `apps/*/src/**`, `apps/{consumer,batch}/build.gradle.kts`) ← `demo-a-platform`

**Interfaces:**
- Consumes: GitHub Packages의 `1.0.0` 아티팩트 세 개(Task 5), `release-app.yml@v1.0.0`.
- Produces: GitHub Template 레포 `khkim6040/demo-b-template`. `./gradlew build`가 플랫폼 모듈 없이 통과(테스트 20개). 생성 후 절차는 README에 있다.

- [ ] **Step 1: 복사**

```bash
A=/Users/gwanhokim/personal-projects/insurance-poc/demo-a-platform
T=/Users/gwanhokim/personal-projects/insurance-poc/demo-b-template
mkdir -p $T && cd $T
git init -q -b main
git remote add origin https://github.com/khkim6040/demo-b-template.git
cp $A/.gitignore $A/gradlew $A/gradlew.bat .
mkdir -p gradle build-logic/src/main/kotlin apps libs
cp -R $A/gradle/wrapper gradle/
cp $A/build-logic/build.gradle.kts build-logic/
cp $A/build-logic/src/main/kotlin/platform.spring-boot-app.gradle.kts build-logic/src/main/kotlin/
cp -R $A/libs/domain libs/
for app in api admin consumer batch; do cp -R $A/apps/$app apps/; done
cp -R $A/deploy .
find . -name build -type d -prune -exec rm -rf {} + ; find . -name .gradle -type d -prune -exec rm -rf {} + ; find . -name .kotlin -type d -prune -exec rm -rf {} +
ls; ls apps libs build-logic/src/main/kotlin
```
Expected: `platform/` 없음. `apps`에 네 앱, `libs/domain`, `build-logic/src/main/kotlin`에 `platform.spring-boot-app.gradle.kts`만.

- [ ] **Step 2: 루트 설정**

`gradle.properties`:
```properties
# The only number a project bumps to take a new platform version.
platformVersion=1.0.0

org.gradle.caching=true
org.gradle.parallel=true
kotlin.code.style=official
```

`settings.gradle.kts`:
```kotlin
pluginManagement {
    includeBuild("build-logic")
}

dependencyResolutionManagement {
    repositories {
        mavenCentral()
        maven {
            name = "GitHubPackages"
            setUrl("https://maven.pkg.github.com/khkim6040/demo-b-platform")
            credentials {
                username = providers.gradleProperty("gpr.user")
                    .orElse(providers.environmentVariable("GITHUB_ACTOR")).orNull
                password = providers.gradleProperty("gpr.key")
                    .orElse(providers.environmentVariable("GITHUB_TOKEN")).orNull
            }
            content { includeGroup("io.github.khkim6040.platform") }
        }
    }
    versionCatalogs {
        create("libs") {
            from("io.github.khkim6040.platform:platform-catalog:${providers.gradleProperty("platformVersion").get()}")
        }
    }
}

rootProject.name = "demo-b-template"

include(
    "libs:domain",
    "apps:api",
    "apps:admin",
    "apps:consumer",
    "apps:batch",
)
```

- [ ] **Step 3: build-logic**

`build-logic/settings.gradle.kts`:
```kotlin
// Reads platformVersion from the root gradle.properties so the number lives in one place.
val rootProperties = java.util.Properties().apply {
    settingsDir.resolve("../gradle.properties").inputStream().use(::load)
}
val platformVersion: String = rootProperties.getProperty("platformVersion")

dependencyResolutionManagement {
    repositories {
        mavenCentral()
        gradlePluginPortal()
        maven {
            name = "GitHubPackages"
            setUrl("https://maven.pkg.github.com/khkim6040/demo-b-platform")
            credentials {
                username = providers.gradleProperty("gpr.user")
                    .orElse(providers.environmentVariable("GITHUB_ACTOR")).orNull
                password = providers.gradleProperty("gpr.key")
                    .orElse(providers.environmentVariable("GITHUB_TOKEN")).orNull
            }
            content { includeGroup("io.github.khkim6040.platform") }
        }
    }
    versionCatalogs {
        create("libs") {
            from("io.github.khkim6040.platform:platform-catalog:$platformVersion")
        }
    }
}

rootProject.name = "build-logic"
```

`build-logic/src/main/kotlin/platform.kotlin-library.gradle.kts` (A안 대비: `repositories {}` 제거, BOM을 플랫폼 BOM으로):
```kotlin
import org.gradle.accessors.dm.LibrariesForLibs

plugins {
    id("org.jetbrains.kotlin.jvm")
    id("org.jetbrains.kotlin.plugin.spring")
}

val libs = the<LibrariesForLibs>()

kotlin {
    jvmToolchain(25)
}

dependencies {
    implementation(platform(libs.platform.bom))
    testImplementation(libs.kotlin.test.junit5)
    testRuntimeOnly("org.junit.platform:junit-platform-launcher")
}

tasks.withType<Test>().configureEach {
    useJUnitPlatform()
}
```

- [ ] **Step 4: api·admin 빌드 파일과 deploy 이름**

`apps/api/build.gradle.kts`와 `apps/admin/build.gradle.kts` 둘 다 다음 내용으로 교체:
```kotlin
plugins {
    id("platform.spring-boot-app")
}

dependencies {
    implementation(project(":libs:domain"))
    implementation(libs.platform.http.starter)

    testImplementation("org.springframework.boot:spring-boot-starter-webmvc-test")
}
```

deploy 이름 치환:
```bash
cd /Users/gwanhokim/personal-projects/insurance-poc/demo-b-template
grep -rl 'demo-a-platform' deploy | xargs sed -i '' 's/demo-a-platform/demo-b-template/g'
sed -i '' 's/namespace: demo-a-dev/namespace: demo-b-template-dev/' deploy/overlays/dev/kustomization.yaml
grep -rn 'demo-a\|demo-b' deploy | sed 's/^ *//' | sort | uniq -c | sort -rn | head
kubectl kustomize deploy/overlays/dev | grep -E 'image:|namespace:' | sed 's/^ *//' | sort -u
```
Expected: `demo-a` 없음. 이미지 네 개 `ghcr.io/khkim6040/demo-b-template/<app>:0.1.0`, `namespace: demo-b-template-dev`.

- [ ] **Step 5: 빌드 검증 (GitHub Packages 아티팩트 사용)**

```bash
cd /Users/gwanhokim/personal-projects/insurance-poc/demo-b-template
export JAVA_HOME=$(/usr/libexec/java_home -v 25)
./gradlew build --console=plain 2>&1 | grep -E 'BUILD|FAILED|Could not|401|403' | head -5
grep -ho 'tests="[0-9]*"' */*/build/test-results/test/*.xml | grep -o '[0-9]*' | paste -sd+ - | bc
./gradlew :apps:api:dependencies --configuration runtimeClasspath --console=plain -q | grep -E 'platform-http-starter|platform-bom' | head -3
```
Expected: `BUILD SUCCESSFUL`, 테스트 `20`, 의존성 트리에 `io.github.khkim6040.platform:platform-http-starter:1.0.0`과 `platform-bom:1.0.0`.

실패 유형별 대응:
- `401`/`Could not resolve io.github.khkim6040.platform:platform-catalog` → `~/.gradle/gradle.properties`의 `gpr.*` 확인(Task 1).
- `Unresolved reference: platform` in `platform.kotlin-library.gradle.kts` → `build-logic/settings.gradle.kts`가 카탈로그를 못 읽은 것. `settingsDir.resolve("../gradle.properties")` 경로 확인.

- [ ] **Step 6: 워크플로**

`.github/workflows/ci.yml`:
```yaml
name: ci
on:
  push:
    branches: [main]
  pull_request:

permissions:
  contents: read
  packages: read

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v7
      - uses: actions/setup-java@v6
        with:
          distribution: temurin
          java-version: "25"
      - uses: gradle/actions/setup-gradle@v6
      - run: ./gradlew build --console=plain
        env:
          GITHUB_ACTOR: ${{ github.actor }}
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      - name: Validate manifests
        run: kubectl kustomize deploy/overlays/dev > /dev/null
```

`.github/workflows/release.yml`:
```yaml
name: release
on:
  push:
    tags: ["*-v*"]

permissions:
  contents: read
  packages: write

jobs:
  release:
    uses: khkim6040/demo-b-platform/.github/workflows/release-app.yml@v1.0.0
    secrets: inherit
```

- [ ] **Step 7: README**

`README.md`:
```markdown
# demo-b-template

Insurance platform PoC, B안의 비즈니스 모노레포 템플릿. 플랫폼 코드는 GitHub Packages 아티팩트(`io.github.khkim6040.platform:*`)로 가져온다.

## 새 프로젝트 만들기

1. `gh repo create khkim6040/<이름> --template khkim6040/demo-b-template --public --clone`
2. 패키지 치환: `io.github.khkim6040.sample` → `io.github.khkim6040.<이름>` (`apps/*/src`, `libs`)
3. 레포 이름 치환: `demo-b-template` → `<이름>` (`settings.gradle.kts`, `deploy/`, 이 README)
4. 로컬 자격 증명(개발자당 1회): `~/.gradle/gradle.properties`에 `gpr.user`, `gpr.key`(`read:packages` 토큰)
5. push → `ci`. 릴리스: `deploy/overlays/dev`의 `newTag` 수정 후 `git tag api-v0.1.0 && git push origin api-v0.1.0`

## 플랫폼 버전 올리기

`gradle.properties`의 `platformVersion`과 `.github/workflows/release.yml`의 `@vX.Y.Z`를 올린다. BOM·카탈로그·스타터는 `platformVersion`을 따라오고, Dockerfile·릴리스 단계는 `@v`를 따라온다.

## 구조

- `apps/{api,admin,consumer,batch}`, `libs/domain`: Phase 1 참조 구현과 동일
- `build-logic`: 컨벤션 플러그인 복사본. 플랫폼 BOM(`libs.platform.bom`)을 적용한다. 중앙 업데이트되지 않는다
- `deploy/`: Kustomize. 전부 프로젝트 소유
- `Dockerfile`은 없다. 릴리스 워크플로가 플랫폼 레포에서 가져온다
```

- [ ] **Step 8: 커밋, push, CI, 템플릿 지정**

```bash
cd /Users/gwanhokim/personal-projects/insurance-poc/demo-b-template
git add -A
git commit -q -m "Add business monorepo template consuming platform artifacts"
git push -q -u origin main
sleep 8
R=khkim6040/demo-b-template
RUN=$(gh run list -R $R --workflow ci --limit 1 --json databaseId --jq '.[0].databaseId')
gh run watch -R $R --exit-status "$RUN" >/dev/null 2>&1
gh run view -R $R "$RUN" --json status,conclusion,url --jq '"ci: \(.status) \(.conclusion) \(.url)"'
gh repo edit $R --template
gh repo view $R --json isTemplate --jq '.isTemplate'
```
Expected: `ci: completed success …`, `true`.

CI가 `401`로 실패하면(다른 레포의 `GITHUB_TOKEN`으로 패키지를 못 읽는 경우) 사용자 토큰을 시크릿으로 넣고 워크플로의 `GITHUB_TOKEN` 값을 `${{ secrets.GPR_TOKEN || secrets.GITHUB_TOKEN }}`으로 바꾼 뒤 다시 push한다. 이 사실은 실험 1 관찰에 적는다.
```bash
gh secret set GPR_TOKEN -R khkim6040/demo-b-template --body "$(gh auth token)"
```

### Task 7: demo-b-contract 생성 (실험 1-B 측정 구간)

**Files:**
- Create: `/Users/gwanhokim/personal-projects/insurance-poc/demo-b-contract/` (템플릿에서 생성)
- Modify: 패키지 디렉터리·`.kt` 23개, `settings.gradle.kts`, `deploy/**`, `README.md`

**Interfaces:**
- Consumes: 템플릿(Task 6), 아티팩트 `1.0.0`(Task 5).
- Produces: `khkim6040/demo-b-contract` main에 커밋 3개(템플릿 초기 커밋 + 치환 2개). CI 성공. `ghcr.io/khkim6040/demo-b-contract/api:0.1.0`. 여기서 센 단계·파일 수가 Task 8의 B 열이다.

- [ ] **Step 1: 빈 레포 삭제 후 템플릿으로 생성 (단계 ①)**

```bash
cd /Users/gwanhokim/personal-projects/insurance-poc
gh repo view khkim6040/demo-b-contract --json isEmpty --jq '.isEmpty'
gh repo delete khkim6040/demo-b-contract --yes
gh repo create khkim6040/demo-b-contract --template khkim6040/demo-b-template --public --clone
cd demo-b-contract
sleep 5; git pull -q --ff-only origin main 2>/dev/null || true
git log --oneline | cat
ls
```
Expected: 첫 줄 `true`(빈 레포인지 확인한 뒤에만 삭제). 생성 후 커밋 1개(`Initial commit`), 템플릿 파일 전부.

- [ ] **Step 2: 패키지 치환 (단계 ②)**

```bash
cd /Users/gwanhokim/personal-projects/insurance-poc/demo-b-contract
for d in $(find apps libs -type d -path '*/io/github/khkim6040/sample' -not -path '*/build/*'); do
  git mv "$d" "$(dirname "$d")/contract"
done
grep -rl 'io.github.khkim6040.sample' apps libs --include='*.kt' | xargs sed -i '' 's/io\.github\.khkim6040\.sample/io.github.khkim6040.contract/g'
grep -rln 'khkim6040.sample' . --exclude-dir=.git --exclude-dir=build | wc -l
git add -A apps libs
git status --short | grep -c '^R'
git commit -q -m "Rename sample packages to contract"
```
Expected: `0`, rename `23`.

- [ ] **Step 3: 레포 이름 치환 (단계 ③)**

```bash
cd /Users/gwanhokim/personal-projects/insurance-poc/demo-b-contract
grep -rl 'demo-b-template' settings.gradle.kts deploy README.md | xargs sed -i '' 's/demo-b-template/demo-b-contract/g'
grep -rn 'demo-b-template' . --exclude-dir=.git | wc -l
kubectl kustomize deploy/overlays/dev | grep -E 'image:|namespace:' | sed 's/^ *//' | sort -u
git add -A
git status --short
git commit -q -m "Rename template references to demo-b-contract"
git log --oneline | cat
```
Expected: `0`. 이미지 네 개 `ghcr.io/khkim6040/demo-b-contract/<app>:0.1.0`, `namespace: demo-b-contract-dev`. 변경 파일: `settings.gradle.kts`, `deploy/base/*/deployment.yaml`×3, `deploy/base/batch/cronjob.yaml`, `deploy/overlays/dev/kustomization.yaml`, `README.md` = 7.

- [ ] **Step 4: 빌드와 네 앱 기동**

```bash
S=/private/tmp/claude-501/-Users-gwanhokim-personal-projects/4cd73c96-55d2-443e-ad6b-891bfc33231f/scratchpad
cd /Users/gwanhokim/personal-projects/insurance-poc/demo-b-contract
export JAVA_HOME=$(/usr/libexec/java_home -v 25)
./gradlew clean build --console=plain 2>&1 | grep -E 'BUILD|FAILED'
grep -ho 'tests="[0-9]*"' */*/build/test-results/test/*.xml | grep -o '[0-9]*' | paste -sd+ - | bc
for app in api admin consumer batch; do unzip -p apps/$app/build/libs/app.jar META-INF/MANIFEST.MF | grep Start-Class; done
(cd /Users/gwanhokim/personal-projects/insurance-poc/insurance-platform-poc && python3 -I tools/stub-server.py 9090 >/dev/null 2>&1) & STUB=$!
java -jar apps/api/build/libs/app.jar > $S/b-api.log 2>&1 & API=$!
for i in $(seq 1 20); do curl -s -o /dev/null localhost:8080/contracts/x && break; sleep 1; done
ID=$(curl -s -X POST localhost:8080/contracts -H 'Content-Type: application/json' \
  -d '{"holderName":"Kim","insuredAmount":10000000,"startDate":"2026-01-01","endDate":"2027-01-01"}' | sed 's/.*"id":"\([^"]*\)".*/\1/')
curl -s -i "localhost:8080/contracts/$ID/quote" | grep -E 'HTTP/|X-Correlation-Id|quotedPremium'
kill $API; pkill -f 'stub-server.py 9090' || true
java -jar apps/admin/build/libs/app.jar > $S/b-admin.log 2>&1 & ADMIN=$!
for i in $(seq 1 20); do curl -s -o /dev/null localhost:8081/admin/contracts && break; sleep 1; done
curl -s -o /dev/null -w '%{http_code}\n' -X POST localhost:8081/admin/contracts/C-1001/suspend
curl -s -o /dev/null -w '%{http_code}\n' -X POST localhost:8081/admin/contracts/C-1001/suspend
kill $ADMIN
java -jar apps/consumer/build/libs/app.jar > $S/b-consumer.log 2>&1 & C=$!
sleep 10; kill $C
echo "tomcat_lines=$(grep -c 'Tomcat' $S/b-consumer.log)"
grep -o 'event evt-[0-9]* -> [A-Z_]*' $S/b-consumer.log | head -3
java -jar apps/batch/build/libs/app.jar > $S/b-batch.log 2>&1; echo "batch exit=$?"
grep -o 'expired [0-9]* contract(s)' $S/b-batch.log
```
Expected: `BUILD SUCCESSFUL`, 테스트 `20`, `Start-Class`가 `io.github.khkim6040.contract.<app>…` 네 줄, api `200` + `X-Correlation-Id` + `"quotedPremium":12000`, admin `200` 그리고 `409`, `tomcat_lines=0`, consumer 이벤트 3줄, `batch exit=0`, `expired 1 contract(s)`.

- [ ] **Step 5: push, CI, 태그 릴리스 (단계 ④)**

```bash
cd /Users/gwanhokim/personal-projects/insurance-poc/demo-b-contract
R=khkim6040/demo-b-contract
git push -q origin main
sleep 8
RUN=$(gh run list -R $R --workflow ci --limit 1 --json databaseId --jq '.[0].databaseId')
gh run watch -R $R --exit-status "$RUN" >/dev/null 2>&1
gh run view -R $R "$RUN" --json status,conclusion,url --jq '"ci: \(.status) \(.conclusion) \(.url)"'
git tag api-v0.1.0
git push -q origin api-v0.1.0
sleep 15
RUN=$(gh run list -R $R --workflow release --limit 1 --json databaseId --jq '.[0].databaseId')
gh run watch -R $R --exit-status "$RUN" >/dev/null 2>&1
gh run view -R $R "$RUN" --json status,conclusion,url --jq '"release: \(.status) \(.conclusion) \(.url)"'
docker manifest inspect ghcr.io/khkim6040/demo-b-contract/api:0.1.0 | grep -m1 '"digest"'
```
Expected: `ci: completed success`, `release: completed success`, 다이제스트 한 줄. release가 실패하면 `gh run view -R $R <id> --log | grep -iE 'error|denied|401' | head`로 원인을 본다. 가능성: ① `github.job_workflow_sha` 미지원 → `ref: v1.0.0`으로 고정하고 관찰에 적는다 ② 다른 레포 `GITHUB_TOKEN`의 패키지 읽기 거부 → Task 6 Step 8의 `GPR_TOKEN` 대응을 `demo-b-contract`에도 적용.

### Task 8: 실험 1 기록 (B 열)

**Files:**
- Modify: `insurance-platform-poc/experiments/01-create.md`

**Interfaces:**
- Consumes: Task 7의 단계·파일 수, 커밋 SHA, 실행 URL, 다이제스트.
- Produces: B 열이 채워진 실험 1 기록. C 열은 Phase 4.

- [ ] **Step 1: 기록 갱신**

`experiments/01-create.md`의 `## 결과` 표를 다음으로 교체하고(A 열은 그대로), `## 근거`와 `## 관찰`에 B 항목을 추가한다. 꺾쇠는 Task 7의 실제 값으로 채운다.

```markdown
| 항목 | A | B | C |
|---|---|---|---|
| 플랫폼 측 수동 단계 수 (목록) | 0 (레포 생성은 Phase 0 부트스트랩, 세 안 공통) | 0 (템플릿·아티팩트는 1회성 플랫폼 구축, baseline에 기록) | Phase 4에서 기록 |
| 프로젝트 측 수동 단계 수, 프로젝트 1개당 (목록) | 5: ① clone + 리모트 재구성(`clone`, `remote rename`, `remote add`, upstream 태그 삭제, `tagOpt --no-tags`) ② 패키지 치환(디렉터리 10개 `git mv` + `sed`, `.kt` 23개) ③ overlay 수정(네임스페이스 + 이미지 `newName`×4 + `newTag`×4, 파일 1) ④ README 교체(파일 1) ⑤ push + 태그. 손댄 파일 25 | 4: ① `gh repo create --template --clone` ② 패키지 치환(디렉터리 10개 `git mv` + `sed`, `.kt` 23개) ③ 레포 이름 `sed`(`settings.gradle.kts`, `deploy/` 5, README = 7) ④ push + 태그. 손댄 파일 30. 별도로 개발자 환경 1회: `~/.gradle/gradle.properties`에 GitHub Packages 토큰 | |
| 머지 충돌 파일 수 | 0 (생성 시점, 머지 없음) | 0 (머지 개념 없음) | |
| 의미적 충돌 (빌드·테스트 실패, 동작 변화) | 없음. 치환 직후 `clean build` 통과, 테스트 25개 | 없음. `clean build` 통과, 테스트 20개(스타터 테스트 5개는 플랫폼 레포에 있음) | |
| 함께 끌려온 무관한 변경 수 | 해당 없음. 단, clone은 플랫폼의 샘플 코드·`api-v0.1.0` 태그·커밋 이력 11개를 전부 가져온다 | 해당 없음. 템플릿 생성은 이력 없이 파일만 복사(커밋 1개), 태그 없음 | |
| 검증 방법과 결과 | `clean build` 통과, 네 jar의 `Start-Class`가 `contract` 패키지, 네 앱 기동(api quote 12000 + `X-Correlation-Id`, admin 목록 2건·suspend 200→409, consumer Tomcat 없음·PROCESSED/DUPLICATE/DEAD_LETTERED, batch `expired 1` exit 0), CI 성공, `api:0.1.0` 매니페스트 확인, `merge upstream/main` = Already up to date | A와 같은 기동 검증 통과, `runtimeClasspath`에 `platform-http-starter:1.0.0`·`platform-bom:1.0.0`, CI 성공(다른 레포 `GITHUB_TOKEN`으로 패키지 읽기 <성공/실패→GPR_TOKEN>), reusable `release-app.yml@v1.0.0`로 `api:0.1.0` 푸시 | |
```

근거 추가:
```markdown
- B: https://github.com/khkim6040/demo-b-contract — 템플릿 초기 커밋 `<sha0>`, 패키지 치환 `<sha1>`, 이름 치환 `<sha2>`, ci <ci run URL>, release <release run URL>, 이미지 `ghcr.io/khkim6040/demo-b-contract/api:0.1.0` (digest `<sha256 앞 12자>`). 플랫폼: https://github.com/khkim6040/demo-b-platform `v1.0.0` publish <publish run URL>, 템플릿 https://github.com/khkim6040/demo-b-template ci <ci run URL>
```

관찰 추가(실제로 겪은 것만 남기고 나머지는 지운다):
```markdown
- B: GitHub 템플릿 생성은 기존 레포를 대상으로 못 한다. Phase 0이 `demo-b-contract`를 미리 만들어 둔 탓에 삭제 후 재생성했다(`delete_repo` 스코프 필요). 실무에서는 템플릿 생성이 레포 생성 자체이므로 부트스트랩이 비즈니스 레포를 미리 만들면 안 된다.
- B: 패키지 치환은 A와 같은 수동 단계다. GitHub Template에는 치환 기능이 없다. 이 단계는 C안의 스크립트가 흡수한다.
- B: 레포 이름이 `settings.gradle.kts`·`deploy/`·README 세 곳에 박혀 있어 `sed` 한 번이 필요하다. A안은 `deploy/base`를 못 건드려 overlay `newName`으로 우회했지만, B안은 전부 프로젝트 소유라 직접 바꾼다.
- B: 로컬 빌드에 GitHub Packages 토큰이 필요하다. 사내 Nexus도 같은 조건이지만, 토큰 없이는 `./gradlew build`조차 안 되므로 온보딩 문서의 첫 줄이 된다.
- B: CI에서 다른 레포 패키지 읽기는 <`GITHUB_TOKEN`으로 됐다 / 안 되어 `GPR_TOKEN` 시크릿을 넣었다>.
- B: 플랫폼 버전을 올릴 때 숫자 두 개(`gradle.properties`의 `platformVersion`, `release.yml`의 `@v`)를 맞춰야 한다. 스펙은 "하나"를 목표로 했지만 reusable workflow 참조는 Gradle 프로퍼티로 못 만든다. 실험 7·8에서 두 숫자가 어긋났을 때의 비용을 본다.
```

- [ ] **Step 2: 커밋과 push**

```bash
cd /Users/gwanhokim/personal-projects/insurance-poc/insurance-platform-poc
git add experiments/01-create.md
git commit -q -m "Record experiment 1 results for approach B"
git push -q
git log --oneline -1
```

---

## 자체 점검 결과

- **스펙 커버리지 (Phase 3 범위)**: 3장 `demo-b-platform`·`demo-b-template`·`demo-b-contract` 생성 방식(Task 2·6·7), 4.1 카탈로그 단일 출처·컨벤션 플러그인 복사(Task 4·6), 4.4 아티팩트 세 개·group·태그 버전·카탈로그 안 BOM 별칭(Task 3·4·5), 5.5 패키지 치환(Task 7), 6.1 Dockerfile 공급(Task 5 `release-app.yml`), 6.2 B안 `release.yml` 한 줄 호출(Task 6), 6.5 `publish.yml`·비즈니스 레포 자격 증명(Task 1·5·6), 7.1~7.2 실험 1 B 열(Task 8), 9장 Phase 3 완료 기준 "GitHub Packages 아티팩트로 contract 빌드·기동"(Task 7 Step 4).
- **스펙과의 차이 두 곳**: ① 스펙 4.4는 "비즈니스 레포가 올리는 숫자는 `settings.gradle.kts`의 카탈로그 버전 하나"라고 했지만, `build-logic`도 같은 카탈로그가 필요해 숫자를 `gradle.properties`로 옮겨 두 settings가 읽게 했다. 숫자는 여전히 하나다. ② reusable workflow의 `@v1.0.0`은 Gradle 프로퍼티로 묶을 수 없어 두 번째 숫자가 된다. Task 8 관찰에 적는다.
- **의도적으로 뺀 것**: 소스 jar·javadoc 퍼블리시, 컨벤션 플러그인 퍼블리시(실험 7 뒤 판단), `ci.yml`의 reusable화(스펙은 release만), 패키지 공개 설정 변경.
- **알려진 위험**: ① `github.job_workflow_sha`가 reusable workflow 컨텍스트에서 비어 있으면 플랫폼 checkout이 실패한다 → `ref: v1.0.0` 고정으로 대체. ② 다른 레포의 `GITHUB_TOKEN`으로 GitHub Packages 읽기가 거부될 수 있다 → `GPR_TOKEN` 시크릿. ③ `version-catalog` 플러그인에서 `from(files(...))` 뒤에 `version()`·`library()` 추가가 거부되면 toml을 복사해 항목을 덧붙이는 방식으로 바꾼다. 세 경우 모두 설계는 유지하고 실험 1 관찰에 적는다.
