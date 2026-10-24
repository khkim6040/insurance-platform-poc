# Phase 0 + Phase 1: 참조 모노레포(demo-a-platform) 구현 계획

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Spring Boot 4.1.2 + Kotlin 기반의 참조 모노레포 `demo-a-platform`(API/Admin/Consumer/Batch + `libs/domain` + `platform/http-starter` + Dockerfile + CI + Kustomize)을 완성하고, GitHub Actions에서 태그 push로 api 이미지가 GHCR에 올라가는 것까지 확인한다.

**Architecture:** 하나의 Gradle 멀티 프로젝트. `build-logic` 포함 빌드의 컨벤션 플러그인 두 개가 모든 모듈의 빌드 설정을 담당한다. `platform/http-starter`는 Spring Boot auto-configuration으로 Correlation ID 필터·예외 핸들러·기본 프로퍼티를 제공한다. 네 앱은 각각 독립된 Spring Boot 실행 진입점이고, api·admin만 Servlet 웹 서버를 띄운다. 저장소는 전부 인메모리다.

**Tech Stack:** JDK 25, Kotlin 2.4.21, Gradle 9.7.0, Spring Boot 4.1.2 (Spring Framework 7.0.x, Spring Batch 6.0.x, Jackson 3), JUnit 5 + AssertJ + MockMvcTester, Docker, Kustomize(`kubectl kustomize`), GitHub Actions, GHCR.

**Spec:** `docs/superpowers/specs/2026-10-24-insurance-platform-poc-design.md` (이 레포 `insurance-platform-poc` 안)

## Global Constraints

- 모든 레포는 `/Users/gwanhokim/personal-projects/insurance-poc/<레포>` 아래에 둔다. 이 계획의 코드는 `demo-a-platform`에, 스크립트·스텁·기록은 `insurance-platform-poc`에 들어간다.
- 버전: Spring Boot `4.1.2`, Kotlin `2.4.21`, Gradle `9.7.0`, JDK `25`. 다른 라이브러리 버전은 Spring Boot BOM(`spring-boot-dependencies`)이 관리하며 직접 적지 않는다.
- Spring Boot 4 모듈 이름: `spring-boot-starter-webmvc`, `spring-boot-starter-webmvc-test`, `spring-boot-starter-restclient`, `spring-boot-starter-batch`, `spring-boot-starter-test`. `spring-boot-starter-web`은 쓰지 않는다.
- 패키지: 플랫폼 코드 `io.github.khkim6040.platform.*`, 샘플 앱·도메인 `io.github.khkim6040.sample.*`.
- `libs/domain`은 Spring·Jakarta·Jackson에 의존하지 않는다.
- consumer·batch는 `platform/http-starter`에 의존하지 않고, 클래스패스에 `jakarta.servlet.Servlet`이 없어야 한다.
- 커밋 메시지는 영어 제목 한 줄. 본문·Co-Authored-By 없음. 빌드가 깨진 상태로 커밋하지 않는다.
- 외부 서비스에 쓰는 행동(GitHub 레포 생성, push, 이미지 푸시)은 스펙에서 이미 승인되었다. 공개 레포다.
- Spring Boot 4 / Spring Batch 6에서 클래스 패키지가 바뀐 경우가 있다. 컴파일이 import 때문에 실패하면 다음 명령으로 실제 위치를 찾아 import만 고친다. 설계는 바꾸지 않는다.
  ```bash
  cd /Users/gwanhokim/personal-projects/insurance-poc/demo-a-platform
  find ~/.gradle/caches/modules-2/files-2.1 -name '<artifact>-*.jar' | grep -v sources | head -1 | xargs -I{} unzip -l {} | grep '<ClassName>.class'
  ```

---

## 파일 구조

### insurance-platform-poc (보고서 레포)

| 파일 | 책임 |
|---|---|
| `tools/bootstrap-repos.sh` | 8개 공개 GitHub 레포 생성 (멱등) |
| `tools/stub-server.py` | 외부 rating API 스텁. `GET /rate?delayMs=N` → `{"rate":1.2}` |
| `docs/superpowers/plans/…` | 이 계획 |

### demo-a-platform (참조 모노레포)

| 파일 | 책임 |
|---|---|
| `settings.gradle.kts` | 포함 빌드 `build-logic`, 모듈 include |
| `gradle/libs.versions.toml` | 모든 버전의 단일 출처 |
| `gradle.properties` | 빌드 캐시·병렬 |
| `build-logic/settings.gradle.kts`, `build-logic/build.gradle.kts` | 컨벤션 플러그인 빌드 |
| `build-logic/src/main/kotlin/platform.kotlin-library.gradle.kts` | Kotlin JVM, JDK 25 툴체인, Boot BOM, 테스트 기본 |
| `build-logic/src/main/kotlin/platform.spring-boot-app.gradle.kts` | Boot 앱: 플러그인, `app.jar`, 테스트 스타터 |
| `libs/domain/…/Contract.kt` | `Contract`, `ContractStatus`, 규칙 메서드 |
| `libs/domain/…/PremiumCalculator.kt` | 보험료 규칙 |
| `libs/domain/…/ContractEvent.kt` | `ContractEvent`, `ContractEventType` |
| `libs/domain/…/ContractRepository.kt` | 인터페이스 + `InMemoryContractRepository` |
| `libs/domain/…/SampleContracts.kt` | admin·batch 시드 데이터 |
| `platform/http-starter/…/http/CorrelationId.kt` | 헤더·MDC 키 상수 (프레임워크 중립) |
| `platform/http-starter/…/http/PlatformDefaultsEnvironmentPostProcessor.kt` | `platform-defaults.yml`을 최저 우선순위로 등록 |
| `platform/http-starter/…/http/servlet/CorrelationIdFilter.kt` | 요청 헤더 읽기/생성, MDC, 응답 헤더 |
| `platform/http-starter/…/http/servlet/PlatformExceptionHandler.kt` | 400/404/409 ProblemDetail + correlationId |
| `platform/http-starter/…/http/servlet/PlatformServletAutoConfiguration.kt` | Servlet 조건부 빈 등록 |
| `platform/http-starter/src/main/resources/platform-defaults.yml` | VT, ProblemDetail, 클라이언트 타임아웃 기본값 |
| `platform/http-starter/src/main/resources/META-INF/spring/…AutoConfiguration.imports` | auto-config 등록 |
| `platform/http-starter/src/main/resources/META-INF/spring.factories` | EnvironmentPostProcessor 등록 |
| `apps/api/…/ApiApplication.kt`, `ContractController.kt`, `QuoteClient.kt`, `ApiConfig.kt` | REST API |
| `apps/admin/…/AdminApplication.kt`, `AdminContractController.kt`, `AdminConfig.kt` | 관리 API |
| `apps/consumer/…/ConsumerApplication.kt`, `ContractEventHandler.kt`, `FakeEventSource.kt`, `ConsumerConfig.kt` | 이벤트 처리 |
| `apps/batch/…/BatchApplication.kt`, `ContractExpiryJobConfig.kt` | 만기 Job |
| `Dockerfile` | 공통 런타임 이미지 |
| `deploy/base/{api,admin,consumer,batch}/*`, `deploy/overlays/dev/kustomization.yaml` | Kustomize |
| `.github/workflows/ci.yml`, `.github/workflows/release.yml` | CI, 태그 릴리스 |

경로 표기 `…`는 `src/main/kotlin/io/github/khkim6040/<platform|sample>/<module>`를 뜻한다. 각 Task의 Files 항목에 전체 경로를 적는다.

---

## Phase 0

### Task 1: JDK 25 설치와 세션 환경

**Files:** 없음 (시스템 설치)

**Interfaces:**
- Produces: `/usr/libexec/java_home -v 25`가 JDK 25 경로를 반환한다. 이후 모든 Gradle 명령은 `JAVA_HOME`을 25로 두고 실행한다.

- [x] **Step 1: 설치**

```bash
brew install --cask temurin@25
```

- [x] **Step 2: 확인**

```bash
/usr/libexec/java_home -v 25
JAVA_HOME=$(/usr/libexec/java_home -v 25) java -version
```
Expected: 경로 출력 후 `openjdk version "25...`

- [x] **Step 3: 이 세션과 이후 Bash 호출에 적용**

모든 Gradle 명령 앞에 `export JAVA_HOME=$(/usr/libexec/java_home -v 25)`를 붙인다. 커밋 없음.

### Task 2: 외부 rating API 스텁 서버

**Files:**
- Create: `insurance-platform-poc/tools/stub-server.py`

**Interfaces:**
- Produces: `GET http://127.0.0.1:9090/rate[?delayMs=N]` → `200 {"rate": 1.2}`. 환경 변수 `STUB_DELAY_MS`로 기본 지연 설정. 그 외 경로 404. api 앱의 `QuoteClient`가 이 응답 스키마에 의존한다.

- [x] **Step 1: 스크립트 작성**

```python
#!/usr/bin/env python3
"""External rating API stub. GET /rate?delayMs=N -> {"rate": 1.2} after N ms.
Default delay comes from STUB_DELAY_MS (ms). Port from argv[1], default 9090."""
import json
import os
import sys
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        url = urlparse(self.path)
        if url.path != "/rate":
            self.send_error(404)
            return
        default_delay = os.environ.get("STUB_DELAY_MS", "0")
        delay_ms = int(parse_qs(url.query).get("delayMs", [default_delay])[0])
        time.sleep(delay_ms / 1000)
        body = json.dumps({"rate": 1.2}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 9090
    print(f"stub listening on 127.0.0.1:{port}", flush=True)
    ThreadingHTTPServer(("127.0.0.1", port), Handler).serve_forever()
```

- [x] **Step 2: 동작 확인**

```bash
cd /Users/gwanhokim/personal-projects/insurance-poc/insurance-platform-poc
chmod +x tools/stub-server.py
python3 -I tools/stub-server.py 9090 & STUB=$!
sleep 1
curl -s -w ' %{http_code} %{time_total}s\n' 'http://127.0.0.1:9090/rate?delayMs=300'
curl -s -o /dev/null -w '%{http_code}\n' 'http://127.0.0.1:9090/nope'
kill $STUB
```
Expected: `{"rate": 1.2} 200 0.3xxs` 그리고 `404`

- [x] **Step 3: 커밋**

```bash
git add tools/stub-server.py
git commit -m "Add external rating API stub server"
```

### Task 3: GitHub 레포 부트스트랩과 보고서 레포 push

**Files:**
- Create: `insurance-platform-poc/tools/bootstrap-repos.sh`
- Create: `insurance-platform-poc/README.md`

**Interfaces:**
- Produces: GitHub에 공개 레포 8개 존재. `insurance-platform-poc`는 `origin`이 연결되고 main이 push됨. `demo-a-platform` 로컬 디렉터리는 **만들지 않는다**(Task 4에서 init).

- [x] **Step 1: 스크립트 작성**

```bash
#!/usr/bin/env bash
# Creates the public GitHub repos for the PoC. Idempotent: existing repos are skipped.
# Local clones are NOT created here; each phase initializes its own repo directory.
set -euo pipefail
OWNER=khkim6040
REPOS=(insurance-platform-poc demo-a-platform demo-a-contract demo-b-platform demo-b-template demo-b-contract demo-c-platform demo-c-contract)
for repo in "${REPOS[@]}"; do
  if gh repo view "$OWNER/$repo" >/dev/null 2>&1; then
    echo "exists  $OWNER/$repo"
  else
    gh repo create "$OWNER/$repo" --public --description "Insurance platform PoC: $repo" >/dev/null
    echo "created $OWNER/$repo"
  fi
done
```

- [x] **Step 2: README 작성**

```markdown
# insurance-platform-poc

보험 도메인 백엔드 플랫폼 아키텍처 PoC의 설계 스펙, 실험 기록, 최종 보고서.

- 스펙: `docs/superpowers/specs/`
- 구현 계획: `docs/superpowers/plans/`
- 실험 기록과 Phase 완료 기록: `experiments/`
- 도구: `tools/bootstrap-repos.sh`(레포 생성), `tools/stub-server.py`(외부 API 스텁)

비교 대상 레포: `demo-a-platform`/`demo-a-contract`, `demo-b-platform`/`demo-b-template`/`demo-b-contract`, `demo-c-platform`/`demo-c-contract` (모두 `khkim6040` 계정).
```

- [x] **Step 3: 실행과 확인**

```bash
cd /Users/gwanhokim/personal-projects/insurance-poc/insurance-platform-poc
chmod +x tools/bootstrap-repos.sh
tools/bootstrap-repos.sh
tools/bootstrap-repos.sh   # 두 번째 실행은 전부 exists
gh repo list khkim6040 --limit 50 --json name --jq '.[].name' | grep -E '^(demo-|insurance-platform-poc)' | sort
```
Expected: 8개 이름 출력

- [x] **Step 4: 커밋과 push**

```bash
git add tools/bootstrap-repos.sh README.md
git commit -m "Add repo bootstrap script and README"
git remote add origin https://github.com/khkim6040/insurance-platform-poc.git
git push -u origin main
```

---

## Phase 1

모든 Gradle 명령은 `/Users/gwanhokim/personal-projects/insurance-poc/demo-a-platform`에서 `export JAVA_HOME=$(/usr/libexec/java_home -v 25)` 후 실행한다.

### Task 4: Gradle 골격과 컨벤션 플러그인

**Files:**
- Create: `demo-a-platform/settings.gradle.kts`
- Create: `demo-a-platform/gradle.properties`
- Create: `demo-a-platform/gradle/libs.versions.toml`
- Create: `demo-a-platform/build-logic/settings.gradle.kts`
- Create: `demo-a-platform/build-logic/build.gradle.kts`
- Create: `demo-a-platform/build-logic/src/main/kotlin/platform.kotlin-library.gradle.kts`
- Create: `demo-a-platform/build-logic/src/main/kotlin/platform.spring-boot-app.gradle.kts`
- Create: `demo-a-platform/.gitignore`
- Create: Gradle wrapper (`gradlew`, `gradle/wrapper/*`)

**Interfaces:**
- Produces: 플러그인 id `platform.kotlin-library`(라이브러리·스타터용), `platform.spring-boot-app`(앱용). 카탈로그 별칭 `libs.spring.boot.bom`. 모든 모듈은 Boot BOM이 `implementation` 플랫폼으로 적용된 상태에서 시작한다. 앱 모듈의 `bootJar` 산출물 이름은 `app.jar`이고 plain `jar`는 비활성화된다.

- [x] **Step 1: 레포 초기화**

```bash
mkdir -p /Users/gwanhokim/personal-projects/insurance-poc/demo-a-platform
cd /Users/gwanhokim/personal-projects/insurance-poc/demo-a-platform
git init -q -b main
git remote add origin https://github.com/khkim6040/demo-a-platform.git
```

- [x] **Step 2: 버전 카탈로그**

`gradle/libs.versions.toml`:
```toml
[versions]
kotlin = "2.4.21"
spring-boot = "4.1.2"

[libraries]
spring-boot-bom = { module = "org.springframework.boot:spring-boot-dependencies", version.ref = "spring-boot" }
spring-boot-gradle-plugin = { module = "org.springframework.boot:spring-boot-gradle-plugin", version.ref = "spring-boot" }
kotlin-gradle-plugin = { module = "org.jetbrains.kotlin:kotlin-gradle-plugin", version.ref = "kotlin" }
kotlin-allopen = { module = "org.jetbrains.kotlin:kotlin-allopen", version.ref = "kotlin" }
kotlin-test-junit5 = { module = "org.jetbrains.kotlin:kotlin-test-junit5", version.ref = "kotlin" }

[plugins]
kotlin-jvm = { id = "org.jetbrains.kotlin.jvm", version.ref = "kotlin" }
kotlin-spring = { id = "org.jetbrains.kotlin.plugin.spring", version.ref = "kotlin" }
spring-boot = { id = "org.springframework.boot", version.ref = "spring-boot" }
```

- [x] **Step 3: 루트 설정**

`settings.gradle.kts`:
```kotlin
pluginManagement {
    includeBuild("build-logic")
}

rootProject.name = "demo-a-platform"

include(
    "libs:domain",
    "platform:http-starter",
    "apps:api",
    "apps:admin",
    "apps:consumer",
    "apps:batch",
)
```

`gradle.properties`:
```properties
org.gradle.caching=true
org.gradle.parallel=true
kotlin.code.style=official
```

`.gitignore`:
```gitignore
.gradle/
build/
.idea/
*.iml
.DS_Store
.kotlin/
```

- [x] **Step 4: build-logic**

`build-logic/settings.gradle.kts`:
```kotlin
dependencyResolutionManagement {
    repositories {
        mavenCentral()
        gradlePluginPortal()
    }
    versionCatalogs {
        create("libs") {
            from(files("../gradle/libs.versions.toml"))
        }
    }
}

rootProject.name = "build-logic"
```

`build-logic/build.gradle.kts`:
```kotlin
plugins {
    `kotlin-dsl`
}

dependencies {
    implementation(libs.kotlin.gradle.plugin)
    implementation(libs.kotlin.allopen)
    implementation(libs.spring.boot.gradle.plugin)
    // Makes the generated LibrariesForLibs accessor available to precompiled script plugins.
    implementation(files(libs.javaClass.superclass.protectionDomain.codeSource.location))
}
```

`build-logic/src/main/kotlin/platform.kotlin-library.gradle.kts`:
```kotlin
import org.gradle.accessors.dm.LibrariesForLibs

plugins {
    id("org.jetbrains.kotlin.jvm")
}

val libs = the<LibrariesForLibs>()

repositories {
    mavenCentral()
}

kotlin {
    jvmToolchain(25)
}

dependencies {
    implementation(platform(libs.spring.boot.bom))
    testImplementation(libs.kotlin.test.junit5)
    testRuntimeOnly("org.junit.platform:junit-platform-launcher")
}

tasks.withType<Test>().configureEach {
    useJUnitPlatform()
}
```

`build-logic/src/main/kotlin/platform.spring-boot-app.gradle.kts`:
```kotlin
import org.springframework.boot.gradle.tasks.bundling.BootJar

plugins {
    id("platform.kotlin-library")
    id("org.springframework.boot")
    id("org.jetbrains.kotlin.plugin.spring")
}

dependencies {
    implementation("org.jetbrains.kotlin:kotlin-reflect")
    testImplementation("org.springframework.boot:spring-boot-starter-test")
}

tasks.named<BootJar>("bootJar") {
    archiveFileName.set("app.jar")
}

tasks.named<Jar>("jar") {
    enabled = false
}
```

참고: `the<LibrariesForLibs>()`는 precompiled script plugin에서 버전 카탈로그에 타입 안전하게 접근하는 Gradle의 공식 우회 방법이고, `build-logic/build.gradle.kts`의 `files(...)` 한 줄이 그 접근자를 플러그인 클래스패스에 올린다.

- [x] **Step 5: 임시 모듈 디렉터리와 wrapper 생성**

include된 여섯 모듈의 디렉터리가 없으면 Gradle은 빈 프로젝트로 취급하므로 디렉터리만 만든다.
```bash
mkdir -p libs/domain platform/http-starter apps/api apps/admin apps/consumer apps/batch
export JAVA_HOME=$(/usr/libexec/java_home -v 25)
gradle wrapper --gradle-version 9.7.0 --distribution-type bin
./gradlew projects --console=plain
```
Expected: 여섯 프로젝트가 트리로 출력되고 BUILD SUCCESSFUL. `build-logic`이 컴파일되며 `platform.kotlin-library`, `platform.spring-boot-app` 플러그인이 만들어진다.

- [x] **Step 6: 커밋**

```bash
git add -A
git commit -m "Add Gradle multi-project skeleton with convention plugins"
```

### Task 5: libs/domain

**Files:**
- Create: `demo-a-platform/libs/domain/build.gradle.kts`
- Create: `demo-a-platform/libs/domain/src/main/kotlin/io/github/khkim6040/sample/domain/Contract.kt`
- Create: `demo-a-platform/libs/domain/src/main/kotlin/io/github/khkim6040/sample/domain/PremiumCalculator.kt`
- Create: `demo-a-platform/libs/domain/src/main/kotlin/io/github/khkim6040/sample/domain/ContractEvent.kt`
- Create: `demo-a-platform/libs/domain/src/main/kotlin/io/github/khkim6040/sample/domain/ContractRepository.kt`
- Create: `demo-a-platform/libs/domain/src/main/kotlin/io/github/khkim6040/sample/domain/SampleContracts.kt`
- Test: `demo-a-platform/libs/domain/src/test/kotlin/io/github/khkim6040/sample/domain/ContractTest.kt`

**Interfaces:**
- Produces (패키지 `io.github.khkim6040.sample.domain`):
  - `enum class ContractStatus { ACTIVE, SUSPENDED, EXPIRED }`
  - `data class Contract(id: String, holderName: String, insuredAmount: Long, startDate: LocalDate, endDate: LocalDate, status: ContractStatus = ACTIVE)` — `init`에서 `insuredAmount > 0`, `endDate > startDate`, `holderName` 비어 있지 않음을 `require`. `fun suspend(): Contract`(ACTIVE가 아니면 `IllegalStateException`), `fun expireIfDue(today: LocalDate): Contract`
  - `object PremiumCalculator { fun monthlyPremium(contract: Contract): Long }` — `insuredAmount / 1000`, 최소 1000
  - `enum class ContractEventType { CREATED, SUSPENDED, EXPIRED }`, `data class ContractEvent(eventId: String, contractId: String, type: ContractEventType)`
  - `interface ContractRepository { fun save(c): Contract; fun findById(id): Contract; fun findAll(): List<Contract> }` — `findById`는 없으면 `NoSuchElementException`
  - `class InMemoryContractRepository : ContractRepository`
  - `object SampleContracts { fun all(): List<Contract> }` — `C-1001`(ACTIVE, 1년 뒤 만기), `C-1002`(ACTIVE, 어제 만기 → 만기 처리 대상)

- [x] **Step 1: 빌드 파일**

`libs/domain/build.gradle.kts`:
```kotlin
plugins {
    id("platform.kotlin-library")
}
```

- [x] **Step 2: 실패하는 테스트 작성**

`libs/domain/src/test/kotlin/io/github/khkim6040/sample/domain/ContractTest.kt`:
```kotlin
package io.github.khkim6040.sample.domain

import java.time.LocalDate
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertFailsWith
import kotlin.test.assertSame

class ContractTest {
    private val today = LocalDate.of(2026, 10, 24)
    private fun contract(end: LocalDate = today.plusYears(1), amount: Long = 10_000_000) =
        Contract("C-1", "Kim", amount, today.minusDays(30), end)

    @Test
    fun `rejects non-positive insured amount`() {
        assertFailsWith<IllegalArgumentException> { contract(amount = 0) }
    }

    @Test
    fun `rejects end date not after start date`() {
        assertFailsWith<IllegalArgumentException> { contract(end = today.minusDays(30)) }
    }

    @Test
    fun `suspend only from active`() {
        val suspended = contract().suspend()
        assertEquals(ContractStatus.SUSPENDED, suspended.status)
        assertFailsWith<IllegalStateException> { suspended.suspend() }
    }

    @Test
    fun `expires when end date reached`() {
        val due = contract(end = today)
        assertEquals(ContractStatus.EXPIRED, due.expireIfDue(today).status)
        val notDue = contract()
        assertSame(notDue, notDue.expireIfDue(today))
    }

    @Test
    fun `monthly premium is one per mille with floor`() {
        assertEquals(10_000, PremiumCalculator.monthlyPremium(contract()))
        assertEquals(1_000, PremiumCalculator.monthlyPremium(contract(amount = 500)))
    }

    @Test
    fun `in-memory repository finds and fails`() {
        val repo = InMemoryContractRepository()
        repo.save(contract())
        assertEquals("C-1", repo.findById("C-1").id)
        assertFailsWith<NoSuchElementException> { repo.findById("nope") }
    }

    @Test
    fun `sample contracts contain exactly one due for expiry`() {
        val due = SampleContracts.all().count { it.expireIfDue(LocalDate.now()).status == ContractStatus.EXPIRED }
        assertEquals(1, due)
    }
}
```

- [x] **Step 3: 실패 확인**

```bash
./gradlew :libs:domain:test --console=plain
```
Expected: 컴파일 실패 (`Contract` 미정의)

- [x] **Step 4: 구현**

`Contract.kt`:
```kotlin
package io.github.khkim6040.sample.domain

import java.time.LocalDate

enum class ContractStatus { ACTIVE, SUSPENDED, EXPIRED }

data class Contract(
    val id: String,
    val holderName: String,
    val insuredAmount: Long,
    val startDate: LocalDate,
    val endDate: LocalDate,
    val status: ContractStatus = ContractStatus.ACTIVE,
) {
    init {
        require(holderName.isNotBlank()) { "holderName must not be blank" }
        require(insuredAmount > 0) { "insuredAmount must be positive" }
        require(endDate.isAfter(startDate)) { "endDate must be after startDate" }
    }

    fun suspend(): Contract {
        check(status == ContractStatus.ACTIVE) { "contract $id is $status, only ACTIVE can be suspended" }
        return copy(status = ContractStatus.SUSPENDED)
    }

    fun expireIfDue(today: LocalDate): Contract =
        if (status != ContractStatus.EXPIRED && !endDate.isAfter(today)) copy(status = ContractStatus.EXPIRED) else this
}
```

`PremiumCalculator.kt`:
```kotlin
package io.github.khkim6040.sample.domain

object PremiumCalculator {
    private const val MINIMUM_PREMIUM = 1_000L

    fun monthlyPremium(contract: Contract): Long = maxOf(contract.insuredAmount / 1_000, MINIMUM_PREMIUM)
}
```

`ContractEvent.kt`:
```kotlin
package io.github.khkim6040.sample.domain

enum class ContractEventType { CREATED, SUSPENDED, EXPIRED }

data class ContractEvent(
    val eventId: String,
    val contractId: String,
    val type: ContractEventType,
)
```

`ContractRepository.kt`:
```kotlin
package io.github.khkim6040.sample.domain

import java.util.concurrent.ConcurrentHashMap

interface ContractRepository {
    fun save(contract: Contract): Contract
    fun findById(id: String): Contract
    fun findAll(): List<Contract>
}

class InMemoryContractRepository : ContractRepository {
    private val store = ConcurrentHashMap<String, Contract>()

    override fun save(contract: Contract): Contract {
        store[contract.id] = contract
        return contract
    }

    override fun findById(id: String): Contract =
        store[id] ?: throw NoSuchElementException("contract $id not found")

    override fun findAll(): List<Contract> = store.values.sortedBy { it.id }
}
```

`SampleContracts.kt`:
```kotlin
package io.github.khkim6040.sample.domain

import java.time.LocalDate

object SampleContracts {
    fun all(): List<Contract> {
        val today = LocalDate.now()
        return listOf(
            Contract("C-1001", "Kim Gwanho", 50_000_000, today.minusMonths(6), today.plusYears(1)),
            Contract("C-1002", "Lee Minji", 20_000_000, today.minusYears(1), today.minusDays(1)),
        )
    }
}
```

- [x] **Step 5: 통과 확인**

```bash
./gradlew :libs:domain:test --console=plain
```
Expected: BUILD SUCCESSFUL, 7 tests

- [x] **Step 6: 커밋**

```bash
git add libs/domain
git commit -m "Add contract domain model with rules and in-memory repository"
```

### Task 6: platform/http-starter

**Files:**
- Create: `demo-a-platform/platform/http-starter/build.gradle.kts`
- Create: `demo-a-platform/platform/http-starter/src/main/kotlin/io/github/khkim6040/platform/http/CorrelationId.kt`
- Create: `demo-a-platform/platform/http-starter/src/main/kotlin/io/github/khkim6040/platform/http/PlatformDefaultsEnvironmentPostProcessor.kt`
- Create: `demo-a-platform/platform/http-starter/src/main/kotlin/io/github/khkim6040/platform/http/servlet/CorrelationIdFilter.kt`
- Create: `demo-a-platform/platform/http-starter/src/main/kotlin/io/github/khkim6040/platform/http/servlet/PlatformExceptionHandler.kt`
- Create: `demo-a-platform/platform/http-starter/src/main/kotlin/io/github/khkim6040/platform/http/servlet/PlatformServletAutoConfiguration.kt`
- Create: `demo-a-platform/platform/http-starter/src/main/resources/platform-defaults.yml`
- Create: `demo-a-platform/platform/http-starter/src/main/resources/META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports`
- Create: `demo-a-platform/platform/http-starter/src/main/resources/META-INF/spring.factories`
- Test: `demo-a-platform/platform/http-starter/src/test/kotlin/io/github/khkim6040/platform/http/StarterTestApplication.kt`
- Test: `demo-a-platform/platform/http-starter/src/test/kotlin/io/github/khkim6040/platform/http/PlatformHttpStarterTest.kt`

**Interfaces:**
- Consumes: 없음
- Produces:
  - 의존하는 앱은 `implementation(project(":platform:http-starter"))` 한 줄로 webmvc, restclient, jackson-module-kotlin을 얻는다.
  - 모든 응답에 `X-Correlation-Id` 헤더. 요청에 있으면 그대로, 없으면 UUID. MDC 키 `correlationId`.
  - `IllegalArgumentException`→400, `NoSuchElementException`→404, `IllegalStateException`→409. 본문은 ProblemDetail(`application/problem+json`)에 `correlationId` 필드 추가.
  - 기본 프로퍼티(앱이 덮어쓸 수 있음): `spring.threads.virtual.enabled=true`, `spring.mvc.problemdetails.enabled=true`, `spring.http.clients.connect-timeout=2s`, `spring.http.clients.read-timeout=5s`.
  - 상수 `CorrelationId.HEADER = "X-Correlation-Id"`, `CorrelationId.MDC_KEY = "correlationId"`.

- [x] **Step 1: 빌드 파일**

`platform/http-starter/build.gradle.kts`:
```kotlin
plugins {
    id("platform.kotlin-library")
    id("org.jetbrains.kotlin.plugin.spring")
}

dependencies {
    api("org.springframework.boot:spring-boot-starter-webmvc")
    api("org.springframework.boot:spring-boot-starter-restclient")
    api("tools.jackson.module:jackson-module-kotlin")
    api("org.jetbrains.kotlin:kotlin-reflect")

    testImplementation("org.springframework.boot:spring-boot-starter-test")
    testImplementation("org.springframework.boot:spring-boot-starter-webmvc-test")
}
```

- [x] **Step 2: 테스트용 앱과 실패하는 테스트 작성**

`src/test/kotlin/io/github/khkim6040/platform/http/StarterTestApplication.kt`:
```kotlin
package io.github.khkim6040.platform.http

import org.springframework.boot.autoconfigure.SpringBootApplication
import org.springframework.web.bind.annotation.GetMapping
import org.springframework.web.bind.annotation.RestController

@SpringBootApplication
class StarterTestApplication

@RestController
class ProbeController {
    @GetMapping("/ok")
    fun ok() = mapOf("ok" to true)

    @GetMapping("/bad")
    fun bad(): Nothing = throw IllegalArgumentException("bad input")

    @GetMapping("/missing")
    fun missing(): Nothing = throw NoSuchElementException("nothing here")

    @GetMapping("/conflict")
    fun conflict(): Nothing = throw IllegalStateException("wrong state")
}
```

`src/test/kotlin/io/github/khkim6040/platform/http/PlatformHttpStarterTest.kt`:
```kotlin
package io.github.khkim6040.platform.http

import org.assertj.core.api.Assertions.assertThat
import org.junit.jupiter.api.Test
import org.springframework.beans.factory.annotation.Autowired
import org.springframework.boot.test.context.SpringBootTest
import org.springframework.boot.webmvc.test.autoconfigure.AutoConfigureMockMvc
import org.springframework.core.env.Environment
import org.springframework.http.HttpStatus
import org.springframework.test.web.servlet.assertj.MockMvcTester

@SpringBootTest(properties = ["spring.http.clients.read-timeout=9s"])
@AutoConfigureMockMvc
class PlatformHttpStarterTest {
    @Autowired lateinit var mvc: MockMvcTester
    @Autowired lateinit var env: Environment

    @Test
    fun `generates correlation id when absent`() {
        val result = mvc.get().uri("/ok").exchange()
        assertThat(result).hasStatusOk()
        assertThat(result.response.getHeader(CorrelationId.HEADER)).isNotBlank()
    }

    @Test
    fun `echoes incoming correlation id`() {
        val result = mvc.get().uri("/ok").header(CorrelationId.HEADER, "abc-123").exchange()
        assertThat(result.response.getHeader(CorrelationId.HEADER)).isEqualTo("abc-123")
    }

    @Test
    fun `maps IllegalArgumentException to 400 problem detail with correlation id`() {
        val result = mvc.get().uri("/bad").header(CorrelationId.HEADER, "corr-400").exchange()
        assertThat(result).hasStatus(HttpStatus.BAD_REQUEST)
        assertThat(result).bodyJson().extractingPath("$.correlationId").isEqualTo("corr-400")
        assertThat(result).bodyJson().extractingPath("$.detail").isEqualTo("bad input")
    }

    @Test
    fun `maps NoSuchElementException to 404 and IllegalStateException to 409`() {
        assertThat(mvc.get().uri("/missing").exchange()).hasStatus(HttpStatus.NOT_FOUND)
        assertThat(mvc.get().uri("/conflict").exchange()).hasStatus(HttpStatus.CONFLICT)
    }

    @Test
    fun `platform defaults apply with lowest precedence`() {
        assertThat(env.getProperty("spring.threads.virtual.enabled")).isEqualTo("true")
        assertThat(env.getProperty("spring.mvc.problemdetails.enabled")).isEqualTo("true")
        assertThat(env.getProperty("spring.http.clients.connect-timeout")).isEqualTo("2s")
        assertThat(env.getProperty("spring.http.clients.read-timeout")).isEqualTo("9s")
    }
}
```

- [x] **Step 3: 실패 확인**

```bash
./gradlew :platform:http-starter:test --console=plain
```
Expected: 컴파일 실패 (`CorrelationId` 미정의)

- [x] **Step 4: 구현**

`src/main/kotlin/io/github/khkim6040/platform/http/CorrelationId.kt`:
```kotlin
package io.github.khkim6040.platform.http

object CorrelationId {
    const val HEADER = "X-Correlation-Id"
    const val MDC_KEY = "correlationId"
}
```

`src/main/kotlin/io/github/khkim6040/platform/http/PlatformDefaultsEnvironmentPostProcessor.kt`:
```kotlin
package io.github.khkim6040.platform.http

import org.springframework.boot.EnvironmentPostProcessor
import org.springframework.boot.SpringApplication
import org.springframework.boot.env.YamlPropertySourceLoader
import org.springframework.core.env.ConfigurableEnvironment
import org.springframework.core.io.ClassPathResource

/** Registers platform-defaults.yml with the lowest precedence so every app property wins. */
class PlatformDefaultsEnvironmentPostProcessor : EnvironmentPostProcessor {
    override fun postProcessEnvironment(environment: ConfigurableEnvironment, application: SpringApplication) {
        YamlPropertySourceLoader()
            .load("platform-defaults", ClassPathResource("platform-defaults.yml"))
            .forEach { environment.propertySources.addLast(it) }
    }
}
```

`src/main/kotlin/io/github/khkim6040/platform/http/servlet/CorrelationIdFilter.kt`:
```kotlin
package io.github.khkim6040.platform.http.servlet

import io.github.khkim6040.platform.http.CorrelationId
import jakarta.servlet.FilterChain
import jakarta.servlet.http.HttpServletRequest
import jakarta.servlet.http.HttpServletResponse
import org.slf4j.MDC
import org.springframework.web.filter.OncePerRequestFilter
import java.util.UUID

class CorrelationIdFilter : OncePerRequestFilter() {
    override fun doFilterInternal(request: HttpServletRequest, response: HttpServletResponse, chain: FilterChain) {
        val id = request.getHeader(CorrelationId.HEADER)?.takeIf { it.isNotBlank() } ?: UUID.randomUUID().toString()
        MDC.put(CorrelationId.MDC_KEY, id)
        response.setHeader(CorrelationId.HEADER, id)
        try {
            chain.doFilter(request, response)
        } finally {
            MDC.remove(CorrelationId.MDC_KEY)
        }
    }
}
```

`src/main/kotlin/io/github/khkim6040/platform/http/servlet/PlatformExceptionHandler.kt`:
```kotlin
package io.github.khkim6040.platform.http.servlet

import io.github.khkim6040.platform.http.CorrelationId
import org.slf4j.MDC
import org.springframework.http.HttpStatus
import org.springframework.http.ProblemDetail
import org.springframework.web.bind.annotation.ExceptionHandler
import org.springframework.web.bind.annotation.RestControllerAdvice

@RestControllerAdvice
class PlatformExceptionHandler {
    @ExceptionHandler(IllegalArgumentException::class)
    fun badRequest(e: IllegalArgumentException) = problem(HttpStatus.BAD_REQUEST, e)

    @ExceptionHandler(NoSuchElementException::class)
    fun notFound(e: NoSuchElementException) = problem(HttpStatus.NOT_FOUND, e)

    @ExceptionHandler(IllegalStateException::class)
    fun conflict(e: IllegalStateException) = problem(HttpStatus.CONFLICT, e)

    private fun problem(status: HttpStatus, e: Exception): ProblemDetail =
        ProblemDetail.forStatusAndDetail(status, e.message ?: status.reasonPhrase).apply {
            setProperty("correlationId", MDC.get(CorrelationId.MDC_KEY))
        }
}
```
의도적으로 `Exception` 전체를 잡는 핸들러는 두지 않는다. 프레임워크 예외(404 정적 자원, 본문 파싱 실패 등)는 `spring.mvc.problemdetails.enabled=true`로 Spring이 직접 ProblemDetail을 만든다.

`src/main/kotlin/io/github/khkim6040/platform/http/servlet/PlatformServletAutoConfiguration.kt`:
```kotlin
package io.github.khkim6040.platform.http.servlet

import org.springframework.boot.autoconfigure.AutoConfiguration
import org.springframework.boot.autoconfigure.condition.ConditionalOnWebApplication
import org.springframework.context.annotation.Bean
import org.springframework.core.Ordered
import org.springframework.core.annotation.Order

@AutoConfiguration
@ConditionalOnWebApplication(type = ConditionalOnWebApplication.Type.SERVLET)
class PlatformServletAutoConfiguration {
    @Bean
    @Order(Ordered.HIGHEST_PRECEDENCE)
    fun correlationIdFilter() = CorrelationIdFilter()

    @Bean
    fun platformExceptionHandler() = PlatformExceptionHandler()
}
```

`src/main/resources/platform-defaults.yml`:
```yaml
# Platform defaults. Lowest precedence: any app property overrides these.
spring:
  threads:
    virtual:
      enabled: true
  mvc:
    problemdetails:
      enabled: true
  http:
    clients:
      connect-timeout: 2s
      read-timeout: 5s
```

`src/main/resources/META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports`:
```text
io.github.khkim6040.platform.http.servlet.PlatformServletAutoConfiguration
```

`src/main/resources/META-INF/spring.factories`:
```properties
org.springframework.boot.EnvironmentPostProcessor=\
io.github.khkim6040.platform.http.PlatformDefaultsEnvironmentPostProcessor
```

- [x] **Step 5: 통과 확인**

```bash
./gradlew :platform:http-starter:test --console=plain
```
Expected: BUILD SUCCESSFUL, 5 tests. `YamlPropertySourceLoader` import가 실패하면 Global Constraints의 명령으로 `spring-boot` jar 안의 실제 패키지를 찾아 고친다.

- [x] **Step 6: 커밋**

```bash
git add platform/http-starter
git commit -m "Add platform-http-starter with correlation id, problem details and defaults"
```

### Task 7: apps/api

**Files:**
- Create: `demo-a-platform/apps/api/build.gradle.kts`
- Create: `demo-a-platform/apps/api/src/main/kotlin/io/github/khkim6040/sample/api/ApiApplication.kt`
- Create: `demo-a-platform/apps/api/src/main/kotlin/io/github/khkim6040/sample/api/ApiConfig.kt`
- Create: `demo-a-platform/apps/api/src/main/kotlin/io/github/khkim6040/sample/api/ContractController.kt`
- Create: `demo-a-platform/apps/api/src/main/kotlin/io/github/khkim6040/sample/api/QuoteClient.kt`
- Create: `demo-a-platform/apps/api/src/main/resources/application.yml`
- Test: `demo-a-platform/apps/api/src/test/kotlin/io/github/khkim6040/sample/api/ApiApplicationTest.kt`

**Interfaces:**
- Consumes: `ContractRepository`, `InMemoryContractRepository`, `Contract`, `PremiumCalculator` (Task 5). 스타터의 헤더·예외 매핑 (Task 6). 스텁 `/rate` 스키마 (Task 2).
- Produces: `POST /contracts` (201, 본문 `CreateContractRequest`), `GET /contracts/{id}`, `GET /contracts/{id}/quote` → `QuoteResponse(contractId, monthlyPremium, quotedPremium)`. 포트 8080. 프로퍼티 `external.rating.base-url`(기본 `http://localhost:9090`).

- [x] **Step 1: 빌드 파일과 설정**

`apps/api/build.gradle.kts`:
```kotlin
plugins {
    id("platform.spring-boot-app")
}

dependencies {
    implementation(project(":libs:domain"))
    implementation(project(":platform:http-starter"))
}
```

`apps/api/src/main/resources/application.yml`:
```yaml
spring:
  application:
    name: api
server:
  port: 8080
external:
  rating:
    base-url: http://localhost:9090
```

- [x] **Step 2: 실패하는 테스트 작성**

`apps/api/src/test/kotlin/io/github/khkim6040/sample/api/ApiApplicationTest.kt`:
```kotlin
package io.github.khkim6040.sample.api

import org.assertj.core.api.Assertions.assertThat
import org.junit.jupiter.api.Test
import org.mockito.BDDMockito.given
import org.springframework.beans.factory.annotation.Autowired
import org.springframework.boot.test.context.SpringBootTest
import org.springframework.boot.webmvc.test.autoconfigure.AutoConfigureMockMvc
import org.springframework.context.ApplicationContext
import org.springframework.http.HttpStatus
import org.springframework.http.MediaType
import org.springframework.test.context.bean.override.mockito.MockitoBean
import org.springframework.test.web.servlet.assertj.MockMvcTester
import org.springframework.web.context.WebApplicationContext

@SpringBootTest
@AutoConfigureMockMvc
class ApiApplicationTest {
    @Autowired lateinit var context: ApplicationContext
    @Autowired lateinit var mvc: MockMvcTester
    @MockitoBean lateinit var quoteClient: QuoteClient

    private val validBody = """
        {"holderName":"Kim","insuredAmount":10000000,"startDate":"2026-01-01","endDate":"2027-01-01"}
    """.trimIndent()

    @Test
    fun `runs as a servlet web application`() {
        assertThat(context).isInstanceOf(WebApplicationContext::class.java)
    }

    @Test
    fun `creates and reads a contract with correlation header`() {
        val created = mvc.post().uri("/contracts").contentType(MediaType.APPLICATION_JSON).content(validBody).exchange()
        assertThat(created).hasStatus(HttpStatus.CREATED)
        assertThat(created.response.getHeader("X-Correlation-Id")).isNotBlank()
        val id = created.response.contentAsString.substringAfter("\"id\":\"").substringBefore("\"")

        val read = mvc.get().uri("/contracts/{id}", id).exchange()
        assertThat(read).hasStatusOk()
        assertThat(read).bodyJson().extractingPath("$.holderName").isEqualTo("Kim")
    }

    @Test
    fun `domain rule violation becomes 400 problem detail`() {
        val body = validBody.replace("10000000", "0")
        val result = mvc.post().uri("/contracts").contentType(MediaType.APPLICATION_JSON).content(body).exchange()
        assertThat(result).hasStatus(HttpStatus.BAD_REQUEST)
        assertThat(result).bodyJson().extractingPath("$.correlationId").isNotNull()
    }

    @Test
    fun `unknown contract becomes 404`() {
        assertThat(mvc.get().uri("/contracts/nope").exchange()).hasStatus(HttpStatus.NOT_FOUND)
    }

    @Test
    fun `quote multiplies premium by external rate`() {
        given(quoteClient.currentRate()).willReturn(1.5)
        val created = mvc.post().uri("/contracts").contentType(MediaType.APPLICATION_JSON).content(validBody).exchange()
        val id = created.response.contentAsString.substringAfter("\"id\":\"").substringBefore("\"")

        val quote = mvc.get().uri("/contracts/{id}/quote", id).exchange()
        assertThat(quote).hasStatusOk()
        assertThat(quote).bodyJson().extractingPath("$.monthlyPremium").isEqualTo(10000)
        assertThat(quote).bodyJson().extractingPath("$.quotedPremium").isEqualTo(15000)
    }
}
```

- [x] **Step 3: 실패 확인**

```bash
./gradlew :apps:api:test --console=plain
```
Expected: 컴파일 실패 (`QuoteClient` 미정의)

- [x] **Step 4: 구현**

`ApiApplication.kt`:
```kotlin
package io.github.khkim6040.sample.api

import org.springframework.boot.autoconfigure.SpringBootApplication
import org.springframework.boot.runApplication

@SpringBootApplication
class ApiApplication

fun main(args: Array<String>) {
    runApplication<ApiApplication>(*args)
}
```

`ApiConfig.kt`:
```kotlin
package io.github.khkim6040.sample.api

import io.github.khkim6040.sample.domain.ContractRepository
import io.github.khkim6040.sample.domain.InMemoryContractRepository
import org.springframework.context.annotation.Bean
import org.springframework.context.annotation.Configuration

@Configuration(proxyBeanMethods = false)
class ApiConfig {
    @Bean
    fun contractRepository(): ContractRepository = InMemoryContractRepository()
}
```

`QuoteClient.kt`:
```kotlin
package io.github.khkim6040.sample.api

import org.springframework.beans.factory.annotation.Value
import org.springframework.stereotype.Component
import org.springframework.web.client.RestClient

@Component
class QuoteClient(
    builder: RestClient.Builder,
    @Value("\${external.rating.base-url}") baseUrl: String,
) {
    private val client = builder.baseUrl(baseUrl).build()

    fun currentRate(): Double =
        client.get().uri("/rate").retrieve().body(RateResponse::class.java)?.rate
            ?: throw IllegalStateException("rating service returned no body")

    data class RateResponse(val rate: Double)
}
```

`ContractController.kt`:
```kotlin
package io.github.khkim6040.sample.api

import io.github.khkim6040.sample.domain.Contract
import io.github.khkim6040.sample.domain.ContractRepository
import io.github.khkim6040.sample.domain.PremiumCalculator
import org.springframework.http.HttpStatus
import org.springframework.web.bind.annotation.GetMapping
import org.springframework.web.bind.annotation.PathVariable
import org.springframework.web.bind.annotation.PostMapping
import org.springframework.web.bind.annotation.RequestBody
import org.springframework.web.bind.annotation.RequestMapping
import org.springframework.web.bind.annotation.ResponseStatus
import org.springframework.web.bind.annotation.RestController
import java.time.LocalDate
import java.util.UUID

data class CreateContractRequest(
    val holderName: String,
    val insuredAmount: Long,
    val startDate: LocalDate,
    val endDate: LocalDate,
)

data class QuoteResponse(val contractId: String, val monthlyPremium: Long, val quotedPremium: Long)

@RestController
@RequestMapping("/contracts")
class ContractController(
    private val repository: ContractRepository,
    private val quoteClient: QuoteClient,
) {
    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    fun create(@RequestBody request: CreateContractRequest): Contract =
        repository.save(
            Contract(
                id = UUID.randomUUID().toString(),
                holderName = request.holderName,
                insuredAmount = request.insuredAmount,
                startDate = request.startDate,
                endDate = request.endDate,
            ),
        )

    @GetMapping("/{id}")
    fun get(@PathVariable id: String): Contract = repository.findById(id)

    @GetMapping("/{id}/quote")
    fun quote(@PathVariable id: String): QuoteResponse {
        val contract = repository.findById(id)
        val premium = PremiumCalculator.monthlyPremium(contract)
        val rate = quoteClient.currentRate()
        return QuoteResponse(contract.id, premium, (premium * rate).toLong())
    }
}
```

- [x] **Step 5: 통과 확인**

```bash
./gradlew :apps:api:test --console=plain
```
Expected: BUILD SUCCESSFUL, 5 tests

- [x] **Step 6: 스텁과 함께 실제 기동 확인**

```bash
cd /Users/gwanhokim/personal-projects/insurance-poc/insurance-platform-poc
python3 -I tools/stub-server.py 9090 & STUB=$!
cd /Users/gwanhokim/personal-projects/insurance-poc/demo-a-platform
./gradlew :apps:api:bootJar --console=plain -q
java -jar apps/api/build/libs/app.jar & API=$!
sleep 6
ID=$(curl -s -X POST localhost:8080/contracts -H 'Content-Type: application/json' \
  -d '{"holderName":"Kim","insuredAmount":10000000,"startDate":"2026-01-01","endDate":"2027-01-01"}' | sed 's/.*"id":"\([^"]*\)".*/\1/')
curl -s -i "localhost:8080/contracts/$ID/quote" | grep -E 'HTTP/|X-Correlation-Id|quotedPremium'
kill $API $STUB
```
Expected: `HTTP/1.1 200`, `X-Correlation-Id: <uuid>`, 본문에 `"quotedPremium":12000`

- [x] **Step 7: 커밋**

```bash
git add apps/api
git commit -m "Add api app with contract endpoints and external rating client"
```

### Task 8: apps/admin

**Files:**
- Create: `demo-a-platform/apps/admin/build.gradle.kts`
- Create: `demo-a-platform/apps/admin/src/main/kotlin/io/github/khkim6040/sample/admin/AdminApplication.kt`
- Create: `demo-a-platform/apps/admin/src/main/kotlin/io/github/khkim6040/sample/admin/AdminConfig.kt`
- Create: `demo-a-platform/apps/admin/src/main/kotlin/io/github/khkim6040/sample/admin/AdminContractController.kt`
- Create: `demo-a-platform/apps/admin/src/main/resources/application.yml`
- Test: `demo-a-platform/apps/admin/src/test/kotlin/io/github/khkim6040/sample/admin/AdminApplicationTest.kt`

**Interfaces:**
- Consumes: `ContractRepository`, `InMemoryContractRepository`, `SampleContracts` (Task 5), 스타터 (Task 6).
- Produces: `GET /admin/contracts`, `POST /admin/contracts/{id}/suspend`. 포트 8081. 기동 시 `SampleContracts.all()`을 시드.

- [x] **Step 1: 빌드 파일과 설정**

`apps/admin/build.gradle.kts`:
```kotlin
plugins {
    id("platform.spring-boot-app")
}

dependencies {
    implementation(project(":libs:domain"))
    implementation(project(":platform:http-starter"))
}
```

`apps/admin/src/main/resources/application.yml`:
```yaml
spring:
  application:
    name: admin
server:
  port: 8081
```

- [x] **Step 2: 실패하는 테스트 작성**

`apps/admin/src/test/kotlin/io/github/khkim6040/sample/admin/AdminApplicationTest.kt`:
```kotlin
package io.github.khkim6040.sample.admin

import org.assertj.core.api.Assertions.assertThat
import org.junit.jupiter.api.Test
import org.springframework.beans.factory.annotation.Autowired
import org.springframework.boot.test.context.SpringBootTest
import org.springframework.boot.webmvc.test.autoconfigure.AutoConfigureMockMvc
import org.springframework.context.ApplicationContext
import org.springframework.http.HttpStatus
import org.springframework.test.web.servlet.assertj.MockMvcTester
import org.springframework.web.context.WebApplicationContext

@SpringBootTest
@AutoConfigureMockMvc
class AdminApplicationTest {
    @Autowired lateinit var context: ApplicationContext
    @Autowired lateinit var mvc: MockMvcTester

    @Test
    fun `runs as a servlet web application`() {
        assertThat(context).isInstanceOf(WebApplicationContext::class.java)
    }

    @Test
    fun `lists seeded contracts`() {
        val result = mvc.get().uri("/admin/contracts").exchange()
        assertThat(result).hasStatusOk()
        assertThat(result).bodyJson().extractingPath("$.length()").isEqualTo(2)
    }

    @Test
    fun `suspends once then conflicts`() {
        assertThat(mvc.post().uri("/admin/contracts/C-1001/suspend").exchange()).hasStatusOk()
        val second = mvc.post().uri("/admin/contracts/C-1001/suspend").exchange()
        assertThat(second).hasStatus(HttpStatus.CONFLICT)
        assertThat(second).bodyJson().extractingPath("$.correlationId").isNotNull()
    }
}
```

- [x] **Step 3: 실패 확인**

```bash
./gradlew :apps:admin:test --console=plain
```
Expected: 컴파일 실패 또는 컨텍스트 로드 실패

- [x] **Step 4: 구현**

`AdminApplication.kt`:
```kotlin
package io.github.khkim6040.sample.admin

import org.springframework.boot.autoconfigure.SpringBootApplication
import org.springframework.boot.runApplication

@SpringBootApplication
class AdminApplication

fun main(args: Array<String>) {
    runApplication<AdminApplication>(*args)
}
```

`AdminConfig.kt`:
```kotlin
package io.github.khkim6040.sample.admin

import io.github.khkim6040.sample.domain.ContractRepository
import io.github.khkim6040.sample.domain.InMemoryContractRepository
import io.github.khkim6040.sample.domain.SampleContracts
import org.springframework.context.annotation.Bean
import org.springframework.context.annotation.Configuration

@Configuration(proxyBeanMethods = false)
class AdminConfig {
    @Bean
    fun contractRepository(): ContractRepository =
        InMemoryContractRepository().apply { SampleContracts.all().forEach(::save) }
}
```

`AdminContractController.kt`:
```kotlin
package io.github.khkim6040.sample.admin

import io.github.khkim6040.sample.domain.Contract
import io.github.khkim6040.sample.domain.ContractRepository
import org.springframework.web.bind.annotation.GetMapping
import org.springframework.web.bind.annotation.PathVariable
import org.springframework.web.bind.annotation.PostMapping
import org.springframework.web.bind.annotation.RequestMapping
import org.springframework.web.bind.annotation.RestController

@RestController
@RequestMapping("/admin/contracts")
class AdminContractController(private val repository: ContractRepository) {
    @GetMapping
    fun list(): List<Contract> = repository.findAll()

    @PostMapping("/{id}/suspend")
    fun suspend(@PathVariable id: String): Contract = repository.save(repository.findById(id).suspend())
}
```

- [x] **Step 5: 통과 확인**

```bash
./gradlew :apps:admin:test --console=plain
```
Expected: BUILD SUCCESSFUL, 3 tests

- [x] **Step 6: 커밋**

```bash
git add apps/admin
git commit -m "Add admin app with contract listing and suspension"
```

### Task 9: apps/consumer

**Files:**
- Create: `demo-a-platform/apps/consumer/build.gradle.kts`
- Create: `demo-a-platform/apps/consumer/src/main/kotlin/io/github/khkim6040/sample/consumer/ConsumerApplication.kt`
- Create: `demo-a-platform/apps/consumer/src/main/kotlin/io/github/khkim6040/sample/consumer/ConsumerConfig.kt`
- Create: `demo-a-platform/apps/consumer/src/main/kotlin/io/github/khkim6040/sample/consumer/ContractEventHandler.kt`
- Create: `demo-a-platform/apps/consumer/src/main/kotlin/io/github/khkim6040/sample/consumer/FakeEventSource.kt`
- Create: `demo-a-platform/apps/consumer/src/main/resources/application.yml`
- Test: `demo-a-platform/apps/consumer/src/test/kotlin/io/github/khkim6040/sample/consumer/ConsumerApplicationTest.kt`

**Interfaces:**
- Consumes: `ContractEvent`, `ContractEventType`, `ContractRepository`, `SampleContracts` (Task 5).
- Produces: `ContractEventHandler.handle(event): HandleResult` (`PROCESSED | DUPLICATE | DEAD_LETTERED`). 프로퍼티 `consumer.max-attempts`(기본 3), `consumer.fake-source.interval`(ISO-8601, 기본 `PT2S`). 웹 서버 없음. 실험 10에서 `FakeEventSource`를 Kafka 리스너로 교체한다.

- [x] **Step 1: 빌드 파일과 설정**

`apps/consumer/build.gradle.kts`:
```kotlin
plugins {
    id("platform.spring-boot-app")
}

dependencies {
    implementation(project(":libs:domain"))
    implementation("org.springframework.boot:spring-boot-starter")
}
```

`apps/consumer/src/main/resources/application.yml`:
```yaml
spring:
  application:
    name: consumer
consumer:
  max-attempts: 3
  fake-source:
    interval: PT2S
```

- [x] **Step 2: 실패하는 테스트 작성**

`apps/consumer/src/test/kotlin/io/github/khkim6040/sample/consumer/ConsumerApplicationTest.kt`:
```kotlin
package io.github.khkim6040.sample.consumer

import io.github.khkim6040.sample.domain.ContractEvent
import io.github.khkim6040.sample.domain.ContractEventType
import io.github.khkim6040.sample.domain.ContractRepository
import io.github.khkim6040.sample.domain.ContractStatus
import org.assertj.core.api.Assertions.assertThat
import org.assertj.core.api.Assertions.assertThatThrownBy
import org.junit.jupiter.api.Test
import org.springframework.beans.factory.annotation.Autowired
import org.springframework.boot.test.context.SpringBootTest
import org.springframework.context.ApplicationContext
import org.springframework.context.annotation.AnnotationConfigApplicationContext

@SpringBootTest(properties = ["consumer.fake-source.interval=PT1H"])
class ConsumerApplicationTest {
    @Autowired lateinit var context: ApplicationContext
    @Autowired lateinit var handler: ContractEventHandler
    @Autowired lateinit var repository: ContractRepository

    @Test
    fun `has no servlet on the classpath and runs as a plain context`() {
        assertThatThrownBy { Class.forName("jakarta.servlet.Servlet") }.isInstanceOf(ClassNotFoundException::class.java)
        assertThat(context).isInstanceOf(AnnotationConfigApplicationContext::class.java)
    }

    @Test
    fun `processes once and ignores duplicates`() {
        val event = ContractEvent("evt-1", "C-1001", ContractEventType.SUSPENDED)
        assertThat(handler.handle(event)).isEqualTo(HandleResult.PROCESSED)
        assertThat(repository.findById("C-1001").status).isEqualTo(ContractStatus.SUSPENDED)
        assertThat(handler.handle(event)).isEqualTo(HandleResult.DUPLICATE)
    }

    @Test
    fun `dead-letters after max attempts`() {
        val event = ContractEvent("evt-2", "unknown", ContractEventType.SUSPENDED)
        assertThat(handler.handle(event)).isEqualTo(HandleResult.DEAD_LETTERED)
        assertThat(handler.attemptsFor("evt-2")).isEqualTo(3)
    }
}
```

- [x] **Step 3: 실패 확인**

```bash
./gradlew :apps:consumer:test --console=plain
```
Expected: 컴파일 실패 (`ContractEventHandler` 미정의)

- [x] **Step 4: 구현**

`ConsumerApplication.kt`:
```kotlin
package io.github.khkim6040.sample.consumer

import org.springframework.boot.autoconfigure.SpringBootApplication
import org.springframework.boot.runApplication
import org.springframework.scheduling.annotation.EnableScheduling

@SpringBootApplication
@EnableScheduling
class ConsumerApplication

fun main(args: Array<String>) {
    runApplication<ConsumerApplication>(*args)
}
```

`ConsumerConfig.kt`:
```kotlin
package io.github.khkim6040.sample.consumer

import io.github.khkim6040.sample.domain.ContractRepository
import io.github.khkim6040.sample.domain.InMemoryContractRepository
import io.github.khkim6040.sample.domain.SampleContracts
import org.springframework.context.annotation.Bean
import org.springframework.context.annotation.Configuration

@Configuration(proxyBeanMethods = false)
class ConsumerConfig {
    @Bean
    fun contractRepository(): ContractRepository =
        InMemoryContractRepository().apply { SampleContracts.all().forEach(::save) }
}
```

`ContractEventHandler.kt`:
```kotlin
package io.github.khkim6040.sample.consumer

import io.github.khkim6040.sample.domain.ContractEvent
import io.github.khkim6040.sample.domain.ContractEventType
import io.github.khkim6040.sample.domain.ContractRepository
import org.slf4j.LoggerFactory
import org.springframework.beans.factory.annotation.Value
import org.springframework.stereotype.Component
import java.time.LocalDate
import java.util.concurrent.ConcurrentHashMap

enum class HandleResult { PROCESSED, DUPLICATE, DEAD_LETTERED }

@Component
class ContractEventHandler(
    private val repository: ContractRepository,
    @Value("\${consumer.max-attempts}") private val maxAttempts: Int,
) {
    private val log = LoggerFactory.getLogger(javaClass)
    private val attempts = ConcurrentHashMap<String, Int>()

    fun handle(event: ContractEvent): HandleResult {
        if (attempts.putIfAbsent(event.eventId, 0) != null) return HandleResult.DUPLICATE
        repeat(maxAttempts) { attempt ->
            attempts[event.eventId] = attempt + 1
            try {
                process(event)
                return HandleResult.PROCESSED
            } catch (e: Exception) {
                log.warn("event {} attempt {}/{} failed: {}", event.eventId, attempt + 1, maxAttempts, e.message)
            }
        }
        log.error("event {} dead-lettered after {} attempts", event.eventId, maxAttempts)
        return HandleResult.DEAD_LETTERED
    }

    fun attemptsFor(eventId: String): Int = attempts[eventId] ?: 0

    private fun process(event: ContractEvent) {
        when (event.type) {
            ContractEventType.CREATED -> repository.findById(event.contractId)
            ContractEventType.SUSPENDED -> repository.save(repository.findById(event.contractId).suspend())
            ContractEventType.EXPIRED -> repository.save(repository.findById(event.contractId).expireIfDue(LocalDate.now()))
        }
    }
}
```

`FakeEventSource.kt`:
```kotlin
package io.github.khkim6040.sample.consumer

import io.github.khkim6040.sample.domain.ContractEvent
import io.github.khkim6040.sample.domain.ContractEventType
import org.slf4j.LoggerFactory
import org.springframework.scheduling.annotation.Scheduled
import org.springframework.stereotype.Component
import java.util.concurrent.atomic.AtomicLong

/** Stand-in for a message broker. Replaced by a Kafka listener in experiment 10. */
@Component
class FakeEventSource(private val handler: ContractEventHandler) {
    private val log = LoggerFactory.getLogger(javaClass)
    private val counter = AtomicLong()

    @Scheduled(fixedDelayString = "\${consumer.fake-source.interval}")
    fun emit() {
        val n = counter.incrementAndGet()
        val event = when {
            n % 3 == 0L -> ContractEvent("evt-$n", "unknown", ContractEventType.SUSPENDED)
            n % 2 == 0L -> ContractEvent("evt-1", "C-1001", ContractEventType.CREATED)
            else -> ContractEvent("evt-$n", "C-1001", ContractEventType.CREATED)
        }
        log.info("event {} -> {}", event.eventId, handler.handle(event))
    }
}
```

- [x] **Step 5: 통과 확인**

```bash
./gradlew :apps:consumer:test --console=plain
```
Expected: BUILD SUCCESSFUL, 3 tests

- [x] **Step 6: 실제 기동 확인 (웹 서버 없이 살아 있는지)**

```bash
./gradlew :apps:consumer:bootJar --console=plain -q
timeout 12 java -jar apps/consumer/build/libs/app.jar 2>&1 | grep -E 'Tomcat|event evt' | head -5
```
Expected: `Tomcat` 줄 없음, `event evt-1 -> PROCESSED`, `event evt-3 -> DEAD_LETTERED` 등이 보임. (`timeout`이 없으면 `brew install coreutils` 후 `gtimeout`)

- [x] **Step 7: 커밋**

```bash
git add apps/consumer
git commit -m "Add consumer app with idempotent retrying event handler"
```

### Task 10: apps/batch

**Files:**
- Create: `demo-a-platform/apps/batch/build.gradle.kts`
- Create: `demo-a-platform/apps/batch/src/main/kotlin/io/github/khkim6040/sample/batch/BatchApplication.kt`
- Create: `demo-a-platform/apps/batch/src/main/kotlin/io/github/khkim6040/sample/batch/ContractExpiryJobConfig.kt`
- Create: `demo-a-platform/apps/batch/src/main/resources/application.yml`
- Test: `demo-a-platform/apps/batch/src/test/kotlin/io/github/khkim6040/sample/batch/ContractExpiryJobTest.kt`

**Interfaces:**
- Consumes: `ContractRepository`, `InMemoryContractRepository`, `SampleContracts`, `Contract.expireIfDue` (Task 5).
- Produces: Job `contractExpiryJob`, Step `expireContracts`. 만기 처리 건수를 `StepContribution.writeCount`에 기록. 프로세스 종료 코드는 Job 결과를 따른다(COMPLETED → 0).

- [x] **Step 1: 빌드 파일과 설정**

`apps/batch/build.gradle.kts`:
```kotlin
plugins {
    id("platform.spring-boot-app")
}

dependencies {
    implementation(project(":libs:domain"))
    implementation("org.springframework.boot:spring-boot-starter-batch")
}
```

`apps/batch/src/main/resources/application.yml`:
```yaml
spring:
  application:
    name: batch
  batch:
    job:
      name: contractExpiryJob
```

- [x] **Step 2: 실패하는 테스트 작성**

`apps/batch/src/test/kotlin/io/github/khkim6040/sample/batch/ContractExpiryJobTest.kt`:
```kotlin
package io.github.khkim6040.sample.batch

import io.github.khkim6040.sample.domain.ContractRepository
import io.github.khkim6040.sample.domain.ContractStatus
import org.assertj.core.api.Assertions.assertThat
import org.assertj.core.api.Assertions.assertThatThrownBy
import org.junit.jupiter.api.Test
import org.springframework.batch.core.ExitStatus
import org.springframework.batch.core.job.Job
import org.springframework.batch.core.job.parameters.JobParameters
import org.springframework.batch.core.launch.JobOperator
import org.springframework.beans.factory.annotation.Autowired
import org.springframework.boot.test.context.SpringBootTest
import org.springframework.context.ApplicationContext
import org.springframework.context.annotation.AnnotationConfigApplicationContext

@SpringBootTest(properties = ["spring.batch.job.enabled=false"])
class ContractExpiryJobTest {
    @Autowired lateinit var context: ApplicationContext
    @Autowired lateinit var jobOperator: JobOperator
    @Autowired lateinit var job: Job
    @Autowired lateinit var repository: ContractRepository

    @Test
    fun `has no servlet on the classpath and runs as a plain context`() {
        assertThatThrownBy { Class.forName("jakarta.servlet.Servlet") }.isInstanceOf(ClassNotFoundException::class.java)
        assertThat(context).isInstanceOf(AnnotationConfigApplicationContext::class.java)
    }

    @Test
    fun `expires due contracts and completes`() {
        val execution = jobOperator.start(job, JobParameters())
        assertThat(execution.exitStatus).isEqualTo(ExitStatus.COMPLETED)
        assertThat(execution.stepExecutions.single().writeCount).isEqualTo(1L)
        assertThat(repository.findById("C-1002").status).isEqualTo(ContractStatus.EXPIRED)
        assertThat(repository.findById("C-1001").status).isEqualTo(ContractStatus.ACTIVE)
    }
}
```
Spring Batch 6은 `Job`, `JobParameters`, `StepContribution` 같은 핵심 타입을 `job`/`step` 하위 패키지로 옮겼다. 위 import가 실패하면 Global Constraints의 명령으로 `spring-batch-core` jar에서 위치를 찾아 import만 고친다.

- [x] **Step 3: 실패 확인**

```bash
./gradlew :apps:batch:test --console=plain
```
Expected: 컴파일 실패 또는 컨텍스트 로드 실패 (`Job` 빈 없음)

- [x] **Step 4: 구현**

`BatchApplication.kt`:
```kotlin
package io.github.khkim6040.sample.batch

import org.springframework.boot.SpringApplication
import org.springframework.boot.autoconfigure.SpringBootApplication
import org.springframework.boot.runApplication
import kotlin.system.exitProcess

@SpringBootApplication
class BatchApplication

fun main(args: Array<String>) {
    exitProcess(SpringApplication.exit(runApplication<BatchApplication>(*args)))
}
```

`ContractExpiryJobConfig.kt`:
```kotlin
package io.github.khkim6040.sample.batch

import io.github.khkim6040.sample.domain.ContractRepository
import io.github.khkim6040.sample.domain.InMemoryContractRepository
import io.github.khkim6040.sample.domain.SampleContracts
import org.slf4j.LoggerFactory
import org.springframework.batch.core.job.Job
import org.springframework.batch.core.job.builder.JobBuilder
import org.springframework.batch.core.repository.JobRepository
import org.springframework.batch.core.step.Step
import org.springframework.batch.core.step.builder.StepBuilder
import org.springframework.batch.core.step.tasklet.Tasklet
import org.springframework.batch.repeat.RepeatStatus
import org.springframework.context.annotation.Bean
import org.springframework.context.annotation.Configuration
import java.time.LocalDate

@Configuration(proxyBeanMethods = false)
class ContractExpiryJobConfig {
    private val log = LoggerFactory.getLogger(javaClass)

    @Bean
    fun contractRepository(): ContractRepository =
        InMemoryContractRepository().apply { SampleContracts.all().forEach(::save) }

    @Bean
    fun expireContractsStep(jobRepository: JobRepository, repository: ContractRepository): Step {
        val tasklet = Tasklet { contribution, _ ->
            val today = LocalDate.now()
            var expired = 0L
            repository.findAll().forEach { contract ->
                val updated = contract.expireIfDue(today)
                if (updated !== contract) {
                    repository.save(updated)
                    expired++
                }
            }
            contribution.incrementWriteCount(expired)
            log.info("expired {} contract(s) as of {}", expired, today)
            RepeatStatus.FINISHED
        }
        return StepBuilder("expireContracts", jobRepository).tasklet(tasklet).build()
    }

    @Bean
    fun contractExpiryJob(jobRepository: JobRepository, expireContractsStep: Step): Job =
        JobBuilder("contractExpiryJob", jobRepository).start(expireContractsStep).build()
}
```

- [x] **Step 5: 통과 확인**

```bash
./gradlew :apps:batch:test --console=plain
```
Expected: BUILD SUCCESSFUL, 2 tests

- [x] **Step 6: 실제 실행과 종료 코드 확인**

```bash
./gradlew :apps:batch:bootJar --console=plain -q
java -jar apps/batch/build/libs/app.jar 2>&1 | grep -E 'Tomcat|expired|COMPLETED' ; echo "exit=${PIPESTATUS[0]}"
```
Expected: `Tomcat` 없음, `expired 1 contract(s)`, `status=[COMPLETED]`, `exit=0`. 프로세스가 스스로 종료되어야 한다.

- [x] **Step 7: 커밋**

```bash
git add apps/batch
git commit -m "Add batch app with contract expiry job"
```

### Task 11: 전체 빌드와 Dockerfile

**Files:**
- Create: `demo-a-platform/Dockerfile`
- Create: `demo-a-platform/.dockerignore`

**Interfaces:**
- Produces: `docker build --build-arg APP=<app> .`로 네 앱 중 하나의 이미지. jar는 빌드 전에 `./gradlew :apps:<app>:bootJar`로 만들어져 있어야 한다.

- [x] **Step 1: 전체 빌드 확인**

```bash
./gradlew build --console=plain
ls apps/*/build/libs/
```
Expected: BUILD SUCCESSFUL. 각 앱 디렉터리에 `app.jar`만 존재 (plain jar 없음).

- [x] **Step 2: Dockerfile 작성**

`Dockerfile`:
```dockerfile
FROM eclipse-temurin:25-jre
ARG APP
COPY apps/${APP}/build/libs/app.jar /app.jar
ENTRYPOINT ["java", "-jar", "/app.jar"]
```

`.dockerignore`:
```text
**
!apps/*/build/libs/app.jar
```

- [x] **Step 3: 이미지 빌드와 실행 확인**

```bash
docker build --build-arg APP=api -t demo-a-platform/api:dev . -q
docker build --build-arg APP=batch -t demo-a-platform/batch:dev . -q
docker run --rm demo-a-platform/batch:dev >/dev/null 2>&1; echo "batch exit=$?"
docker run --rm -d -p 18080:8080 --name api-smoke demo-a-platform/api:dev
sleep 8
curl -s -i localhost:18080/contracts/nope | grep -E 'HTTP/|X-Correlation-Id|application/problem'
docker rm -f api-smoke
```
Expected: `batch exit=0`, `HTTP/1.1 404`, `X-Correlation-Id`, `Content-Type: application/problem+json`

- [x] **Step 4: 커밋**

```bash
git add Dockerfile .dockerignore
git commit -m "Add shared runtime Dockerfile parameterized by app"
```

### Task 12: Kustomize 매니페스트

**Files:**
- Create: `demo-a-platform/deploy/base/api/deployment.yaml`, `service.yaml`, `kustomization.yaml`
- Create: `demo-a-platform/deploy/base/admin/deployment.yaml`, `service.yaml`, `kustomization.yaml`
- Create: `demo-a-platform/deploy/base/consumer/deployment.yaml`, `kustomization.yaml`
- Create: `demo-a-platform/deploy/base/batch/cronjob.yaml`, `kustomization.yaml`
- Create: `demo-a-platform/deploy/overlays/dev/kustomization.yaml`

**Interfaces:**
- Produces: `kubectl kustomize deploy/overlays/dev`가 네 워크로드를 렌더링. 이미지 이름은 `ghcr.io/khkim6040/demo-a-platform/<app>`, 태그는 overlay의 `images:`에서만 지정. `deploy/base`는 upstream 소유, `deploy/overlays`는 프로젝트 소유.

- [x] **Step 1: api base**

`deploy/base/api/deployment.yaml`:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api
  labels:
    app: api
spec:
  replicas: 1
  selector:
    matchLabels:
      app: api
  template:
    metadata:
      labels:
        app: api
    spec:
      containers:
        - name: api
          image: ghcr.io/khkim6040/demo-a-platform/api
          ports:
            - containerPort: 8080
          resources:
            limits:
              cpu: "1"
              memory: 512Mi
```

`deploy/base/api/service.yaml`:
```yaml
apiVersion: v1
kind: Service
metadata:
  name: api
spec:
  selector:
    app: api
  ports:
    - port: 80
      targetPort: 8080
```

`deploy/base/api/kustomization.yaml`:
```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
  - deployment.yaml
  - service.yaml
```

- [x] **Step 2: admin base**

`deploy/base/admin/deployment.yaml`:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: admin
  labels:
    app: admin
spec:
  replicas: 1
  selector:
    matchLabels:
      app: admin
  template:
    metadata:
      labels:
        app: admin
    spec:
      containers:
        - name: admin
          image: ghcr.io/khkim6040/demo-a-platform/admin
          ports:
            - containerPort: 8081
          resources:
            limits:
              cpu: "1"
              memory: 512Mi
```

`deploy/base/admin/service.yaml`:
```yaml
apiVersion: v1
kind: Service
metadata:
  name: admin
spec:
  selector:
    app: admin
  ports:
    - port: 80
      targetPort: 8081
```

`deploy/base/admin/kustomization.yaml`:
```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
  - deployment.yaml
  - service.yaml
```

- [x] **Step 3: consumer base**

`deploy/base/consumer/deployment.yaml`:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: consumer
  labels:
    app: consumer
spec:
  replicas: 1
  selector:
    matchLabels:
      app: consumer
  template:
    metadata:
      labels:
        app: consumer
    spec:
      containers:
        - name: consumer
          image: ghcr.io/khkim6040/demo-a-platform/consumer
          resources:
            limits:
              cpu: "500m"
              memory: 384Mi
```

`deploy/base/consumer/kustomization.yaml`:
```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
  - deployment.yaml
```

- [x] **Step 4: batch base**

`deploy/base/batch/cronjob.yaml`:
```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: batch
spec:
  schedule: "0 1 * * *"
  concurrencyPolicy: Forbid
  jobTemplate:
    spec:
      template:
        spec:
          restartPolicy: OnFailure
          containers:
            - name: batch
              image: ghcr.io/khkim6040/demo-a-platform/batch
              resources:
                limits:
                  cpu: "500m"
                  memory: 384Mi
```

`deploy/base/batch/kustomization.yaml`:
```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
  - cronjob.yaml
```

- [x] **Step 5: dev overlay**

`deploy/overlays/dev/kustomization.yaml`:
```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
namespace: demo-a-dev
resources:
  - ../../base/api
  - ../../base/admin
  - ../../base/consumer
  - ../../base/batch
images:
  - name: ghcr.io/khkim6040/demo-a-platform/api
    newTag: 0.1.0
  - name: ghcr.io/khkim6040/demo-a-platform/admin
    newTag: 0.1.0
  - name: ghcr.io/khkim6040/demo-a-platform/consumer
    newTag: 0.1.0
  - name: ghcr.io/khkim6040/demo-a-platform/batch
    newTag: 0.1.0
```

- [x] **Step 6: 렌더링 확인**

```bash
kubectl kustomize deploy/overlays/dev | grep -E '^kind:|image:'
```
Expected: `Deployment`×3, `Service`×2, `CronJob`×1, `image:` 4줄 모두 `:0.1.0`

- [x] **Step 7: 커밋**

```bash
git add deploy
git commit -m "Add Kustomize base and dev overlay for all apps"
```

### Task 13: GitHub Actions CI와 태그 릴리스

**Files:**
- Create: `demo-a-platform/.github/workflows/ci.yml`
- Create: `demo-a-platform/.github/workflows/release.yml`
- Create: `demo-a-platform/README.md`

**Interfaces:**
- Produces: main push/PR에 `ci` 워크플로(빌드 + kustomize 검증). `<app>-v<semver>` 태그 push에 `release` 워크플로가 `ghcr.io/khkim6040/demo-a-platform/<app>:<semver>` 이미지를 푸시하고 라벨 `org.opencontainers.image.revision=<sha>`를 붙인다.

- [x] **Step 1: ci.yml**

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
      - run: ./gradlew build --console=plain
      - name: Validate manifests
        run: kubectl kustomize deploy/overlays/dev > /dev/null
```

- [x] **Step 2: release.yml**

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
  image:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v7
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
      - uses: docker/login-action@v4
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      - uses: docker/build-push-action@v7
        with:
          context: .
          push: true
          build-args: APP=${{ steps.tag.outputs.app }}
          tags: ghcr.io/${{ github.repository }}/${{ steps.tag.outputs.app }}:${{ steps.tag.outputs.version }}
          labels: org.opencontainers.image.revision=${{ github.sha }}
```

- [x] **Step 3: README**

`README.md`:
```markdown
# demo-a-platform

Insurance platform PoC, A안(Fork + Upstream Merge)의 플랫폼 레포이자 참조 모노레포.

- `apps/{api,admin,consumer,batch}`: 독립 실행·배포되는 네 앱 (api 8080, admin 8081, consumer·batch는 웹 서버 없음)
- `libs/domain`: Spring에 의존하지 않는 계약 도메인
- `platform/http-starter`: Correlation ID, ProblemDetail, 기본 프로퍼티를 제공하는 스타터
- `build-logic`: 컨벤션 플러그인 `platform.kotlin-library`, `platform.spring-boot-app`
- `deploy/`: Kustomize (`base`는 플랫폼 소유, `overlays`는 프로젝트 소유)

빌드: `./gradlew build` (JDK 25). 이미지: `./gradlew :apps:api:bootJar && docker build --build-arg APP=api .`
릴리스: `deploy/overlays/dev`의 태그를 올려 커밋한 뒤 `git tag api-v0.1.0 && git push --tags`.

A안 비즈니스 프로젝트의 수정 금지 파일: `platform/**`, `build-logic/**`, `gradle/**`, 루트 빌드 파일, `apps/*/build.gradle.kts`, `Dockerfile`, `.github/**`, `deploy/base/**`.
```

- [x] **Step 4: 커밋과 push, CI 확인**

```bash
git add .github README.md
git commit -m "Add CI and tag-based release workflows"
git push -u origin main
gh run watch --exit-status $(gh run list --workflow ci --limit 1 --json databaseId --jq '.[0].databaseId')
```
Expected: `ci` 성공. 실패하면 로그를 읽고 고친 뒤 다시 push한다. 흔한 원인은 Gradle 툴체인이 CI에서 JDK 25를 못 찾는 경우인데, `setup-java`가 설치한 JDK가 기본이므로 발생하지 않아야 한다.

- [x] **Step 5: 태그 릴리스 확인**

```bash
git tag api-v0.1.0
git push origin api-v0.1.0
sleep 20
gh run watch --exit-status $(gh run list --workflow release --limit 1 --json databaseId --jq '.[0].databaseId')
gh api /user/packages/container/demo-a-platform%2Fapi/versions --jq '.[].metadata.container.tags'
```
Expected: `release` 성공, 태그 목록에 `["0.1.0"]`

### Task 14: Phase 1 완료 기록

**Files:**
- Create: `insurance-platform-poc/experiments/phase1-reference-monorepo.md`

**Interfaces:**
- Produces: Phase 1 완료 기준의 증거 목록. Phase 2 계획의 입력.

- [x] **Step 1: 기록 작성**

`experiments/phase1-reference-monorepo.md` (각 항목의 실제 값을 채운다):
```markdown
# Phase 1: 참조 모노레포 완료 기록

- 레포: https://github.com/khkim6040/demo-a-platform
- 완료 커밋: <sha>
- 버전: Spring Boot 4.1.2, Kotlin 2.4.21, Gradle 9.7.0, JDK 25

## 완료 기준 확인

| 기준 | 증거 |
|---|---|
| `./gradlew build` 통과 | 로컬 실행 결과, 테스트 수 <N> |
| api·admin이 SERVLET | `ApiApplicationTest`, `AdminApplicationTest` |
| consumer·batch에 Servlet 없음 | `ConsumerApplicationTest`, `ContractExpiryJobTest` |
| CI 녹색 | <ci run URL> |
| 태그 push로 api 이미지 | <release run URL>, `ghcr.io/khkim6040/demo-a-platform/api:0.1.0` |

## 구현 중 설계와 달랐던 점

- (Spring Boot 4 / Spring Batch 6 패키지 이동으로 고친 import, 플러그인 접근 방식 등 실제로 바꾼 것만 적는다. 없으면 "없음")

## 움직이는 부품 수 (baseline 사전 기록)

- Gradle 모듈 <N>, 컨벤션 플러그인 2, 워크플로 2, Dockerfile 1, Kustomize 파일 <N>, Kotlin 소스 줄 수 <N> (`find . -name '*.kt' -not -path '*/build/*' | xargs wc -l`)
```

- [x] **Step 2: 커밋과 push**

```bash
cd /Users/gwanhokim/personal-projects/insurance-poc/insurance-platform-poc
git add experiments/phase1-reference-monorepo.md
git commit -m "Record Phase 1 completion evidence"
git push
```

---

## 자체 점검 결과

- **스펙 커버리지 (Phase 0·1 범위)**: 3장 레포 생성(Task 3), 4장 Gradle·스타터(Task 4·6), 5장 앱·테스트·소유권(Task 5·7~10, README), 6장 Dockerfile·CI·릴리스·Kustomize(Task 11~13), 9장 Phase 1 완료 기준(Task 13·14). Phase 2 이후는 다음 계획에서 다룬다.
- **의도적으로 뺀 것**: Spring Boot 레이어드 jar, buildInfo, 관측성·복원력 스타터(Phase 6), GHCR 패키지 공개 설정(아무도 pull하지 않음), consumer의 실제 큐.
- **알려진 위험**: Spring Boot 4·Spring Batch 6의 패키지 이동, `the<LibrariesForLibs>()` 접근자. 둘 다 Global Constraints와 Task 4 Step 4의 대안으로 복구 경로를 적어 두었다.
