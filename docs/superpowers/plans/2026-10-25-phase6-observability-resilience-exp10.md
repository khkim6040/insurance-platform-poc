# Phase 6: 관측성·복원력 스타터 + 실험 10 실행 계획

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 세 플랫폼에 `observability-starter`·`resilience-starter`를 추가해 `v1.6.0`으로 내고, contract·claims 여섯 프로젝트에 전파해 `experiments/10-new-common-feature.md`를 근거 링크와 에이전트 개입 행까지 채운다. Phase 6 완료.

**Architecture:** 스타터는 각각 "의존성 묶음 + 최저 우선순위 기본 프로퍼티(`EnvironmentPostProcessor`) + 스타터 테스트"로, 기존 `http-starter`와 같은 모양이다. 관측성 = Actuator + Micrometer Prometheus + Boot 4.1 `spring-boot-starter-opentelemetry`(Micrometer Tracing OTel 브리지 포함). 기본값은 `health,info,metrics,prometheus,circuitbreakers,retries` 노출, `application` 태그, 샘플링 1.0, OTLP 메트릭 내보내기 끔. 복원력 = `resilience4j-spring-boot4` 2.4.0 + `aspectjweaver`, 기본값은 CB(창 10, 최소 5콜, 실패율 50%, open 10s, 헬스 등록)와 Retry(3회, 200ms). A는 `platform/` 모듈 2개와 api·admin 빌드 파일에 줄을 더해 머지로 전파하고, B/C는 아티팩트 2개 + BOM 제약 + 카탈로그 별칭을 퍼블리시하고 프로젝트가 앱마다 한 줄을 적는다. 실험 10의 "충돌 예상" 지점(스펙 5.4: 프로젝트의 의존성 추가 vs 플랫폼의 스타터 추가)을 실제로 만들기 위해, 세 contract가 **먼저** `apps/api/build.gradle.kts`에 자기 의존성 한 줄(`commons-lang3`)을 더한다. A에서는 소유권 규약 위반이지만 스펙이 명시한 측정 지점이므로 계획된 위반이다. claims는 손대지 않은 프로젝트의 경로를 보여 준다.

**Tech Stack:** Phase 1~5와 동일. 추가: Boot 4.1.2 모듈 `spring-boot-starter-actuator`, `spring-boot-starter-micrometer-metrics`, `spring-boot-starter-opentelemetry`, `io.micrometer:micrometer-registry-prometheus`(micrometer-bom 관리), `io.github.resilience4j:resilience4j-spring-boot4:2.4.0`(Maven Central에 2.4.0만 존재, Boot 4.0.0 기준 컴파일), `org.aspectj:aspectjweaver`(Boot BOM 관리). 대체안: Spring Framework 7 `org.springframework.resilience.annotation.@EnableResilientMethods`/`@Retryable`.

**Spec:** `docs/superpowers/specs/2026-10-24-insurance-platform-poc-design.md` (4.3 스타터 모양, 4.4 BOM·카탈로그, 5.4 소유권 규약과 실험 10 충돌 지점, 7.1 기록 양식·에이전트 개입 행, 7.2 실험 10, 8 심화 스타터, 9 Phase 6 완료 기준)

## Global Constraints

- 레포 경로 `/Users/gwanhokim/personal-projects/insurance-poc/<레포>`. 기록은 `insurance-platform-poc/experiments/`. 임시 파일은 `/private/tmp/claude-501/-Users-gwanhokim-personal-projects/4cd73c96-55d2-443e-ad6b-891bfc33231f/scratchpad`(아래 `$S`).
- 모든 Gradle·java 명령은 `source $S/poc.sh` 뒤에 실행한다(JAVA_HOME 25, `api_up`/`api_down`/`pr_merge`/`run_wait`/`tests_total`, Task 0에서 `actuator_probe`·`deps_has` 추가).
- 시작 상태(모두 `main`, clean): `demo-a-platform` `2cc5429`=`v1.5.0`, `demo-a-contract` `0e25686`(v1.5.0 머지가 revert된 상태, 위반 줄 `read-timeout: 3s` 유지), `demo-a-claims` `f0bc128`(v1.5.0 기준), `demo-b-platform` `dd5bd8e`=`v1.5.0`, `demo-b-template` `367078b`(핀 `1.5.0`/`@v1.5.0`), `demo-b-contract` `66f4433`(`platformVersion=1.3.0`, `@v1.4.0`), `demo-b-claims` `1f74a6a`(`1.5.0`/`@v1.5.0`), `demo-c-platform` `f608e95`=`v1.5.0`(템플릿 핀 `1.5.0`/`@v1.5.0`), `demo-c-contract` `81fc5d2`(`1.3.0`/`@v1.4.0`), `demo-c-claims` `94cff57`(`1.5.0`/`@v1.5.0`).
- 새 플랫폼 버전은 세 안 공통 `v1.6.0`. Group ID: B `io.github.khkim6040.platform`, C `io.github.khkim6040.cplatform`.
- 모듈 경로: A `platform/observability-starter/`, `platform/resilience-starter/`; B/C `platform-observability-starter/`, `platform-resilience-starter/`. 모듈 안 상대 경로는 같다. 패키지 `io.github.khkim6040.platform.observability`, `io.github.khkim6040.platform.resilience`.
- 플랫폼 변경은 PR → CI → 머지 → 태그(B/C는 publish 대기 포함). 프로젝트 반영은 main 직접 push + CI. 단계 수를 셀 때 "PR → CI → 머지"와 "commit → push → CI"는 각각 1단계.
- A 충돌 해소 정책(미리 정함, 개입으로 세지 않음): `apps/api/build.gradle.kts` 충돌은 **양쪽 모두 유지**(프로젝트의 `commons-lang3` 줄 + 플랫폼의 스타터 2줄). `--ours`로 풀면 스타터가 빠져 실험이 무의미해진다.
- B/C 숫자 올리기 원칙: 변경이 필요로 하는 숫자만. 실험 10은 `platformVersion`만(`release-app.yml`은 1.6.0에서 바뀌지 않으므로 `@v`는 그대로 둔다).
- 측정: 수동 단계 수(목록), 손댄 파일 수, 충돌 파일 수, 함께 끌려온 변경 수, 에이전트 개입. 시간은 재지 않는다. 기록 표의 값은 **실측**으로 적고 아래 "기대"와의 차이는 관찰에 남긴다.
- 커밋은 영어 제목 한 줄. `gh`는 항상 `-R khkim6040/<레포>`. `sed -i` 대신 `perl -pi -e`. 토큰·`gpr.key`는 출력하지 않는다. 삭제·force push 없음.
- 포트: api 8080, 스텁 9090. 각 검증 뒤 `api_down`으로 반드시 내린다.
- 실패 시 멈춤: Task 2의 Step 9(스타터 테스트)에서 `resilience4j-spring-boot4`가 Boot 4.1에서 컨텍스트를 못 올리면 Step 9b의 대체안으로 간다. 그 외 설계와 다른 사실이 드러나면 멈추고 보고한다.

---

## 파일 구조

### insurance-platform-poc

| 파일 | 내용 |
|---|---|
| `experiments/10-new-common-feature.md` | 실험 10 기록 (Task 7) |

### 플랫폼 레포 — 새 모듈 (A `platform/<name>-starter`, B/C `platform-<name>-starter`)

| 파일 | 역할 |
|---|---|
| `observability-starter/build.gradle.kts` | actuator·micrometer-metrics·prometheus·opentelemetry `api` 의존성. B/C는 `maven-publish` 추가 |
| `observability-starter/src/main/kotlin/io/github/khkim6040/platform/observability/PlatformObservabilityEnvironmentPostProcessor.kt` | `platform-observability-defaults.yml`을 최저 우선순위로 등록 |
| `observability-starter/src/main/resources/platform-observability-defaults.yml` | 엔드포인트 노출, `application` 태그, 샘플링 1.0, OTLP 메트릭 끔 |
| `observability-starter/src/main/resources/META-INF/spring.factories` | 위 프로세서 등록 |
| `observability-starter/src/test/kotlin/io/github/khkim6040/platform/observability/{ObservabilityTestApplication,PlatformObservabilityStarterTest}.kt` | `/actuator/health`·`/actuator/prometheus`, 태그, `Tracer` 빈 |
| `resilience-starter/build.gradle.kts` | `resilience4j-spring-boot4`·`aspectjweaver` `api` 의존성 |
| `resilience-starter/src/main/kotlin/io/github/khkim6040/platform/resilience/PlatformResilienceEnvironmentPostProcessor.kt` | `platform-resilience-defaults.yml` 등록 |
| `resilience-starter/src/main/resources/platform-resilience-defaults.yml` | CB·Retry 기본 설정 |
| `resilience-starter/src/main/resources/META-INF/spring.factories` | 프로세서 등록 |
| `resilience-starter/src/test/kotlin/io/github/khkim6040/platform/resilience/{ResilienceTestApplication,PlatformResilienceStarterTest}.kt` | Retry 3회, CB open, 기본값 |

### 플랫폼 레포 — 기존 파일 수정

| 파일 | A | B | C |
|---|---|---|---|
| `gradle/libs.versions.toml` | `resilience4j` 버전·별칭 | 같음 | 같음 |
| `settings.gradle.kts` | `platform:observability-starter`, `platform:resilience-starter` include | `platform-observability-starter`, `platform-resilience-starter` include | 같음(B) |
| `platform-bom/build.gradle.kts` | — | 제약 2줄 | 제약 2줄(cplatform) |
| `platform-catalog/build.gradle.kts` | — | 별칭 2줄 | 별칭 2줄(cplatform) |
| `apps/api/build.gradle.kts`, `apps/admin/build.gradle.kts` | api +2줄, admin +1줄 | — (`demo-b-template` 별도 레포에서 같은 변경) | `templates/multi-service/apps/{api,admin}/build.gradle.kts` 같은 변경 |
| 템플릿 핀 | — | `demo-b-template` `gradle.properties` `1.6.0`, `release.yml` `@v1.6.0` | `templates/multi-service/gradle.properties`, `.../release.yml` |
| `README.md` | 스타터 목록 2줄 | — | — |

### 프로젝트 레포

| 레포 | 변경 |
|---|---|
| `demo-{a,b,c}-contract` | (사전) `apps/api/build.gradle.kts` `commons-lang3` 1줄. (전파) A: revert-of-revert 커밋 + `v1.6.0` 머지 커밋(충돌 1 해소). B/C: `gradle.properties` + `apps/api/build.gradle.kts` 2줄 + `apps/admin/build.gradle.kts` 1줄 |
| `demo-{a,b,c}-claims` | A: `v1.6.0` 머지 커밋(충돌 0). B/C: 위와 같은 3파일 |

---

## Task 0: 시작 상태 확인과 헬퍼 보강

**Files:**
- Modify: `$S/poc.sh` (`actuator_probe`, `deps_has` 추가)

- [x] **Step 1: 열 개 레포가 모두 Global Constraints의 시작 상태인지 확인**

```bash
cd /Users/gwanhokim/personal-projects/insurance-poc
for r in demo-a-platform demo-a-contract demo-a-claims demo-b-platform demo-b-template demo-b-contract demo-b-claims demo-c-platform demo-c-contract demo-c-claims; do
  printf '%-16s %s dirty=%s branch=%s\n' $r "$(git -C $r rev-parse --short HEAD)" "$(git -C $r status --porcelain | wc -l | tr -d ' ')" "$(git -C $r branch --show-current)"
done
```
Expected: SHA가 Global Constraints와 같고 `dirty=0 branch=main`.

- [x] **Step 2: `poc.sh`에 두 함수 추가**

`$S/poc.sh` 끝에 덧붙인다:

```bash
# 실험 10 검증. api가 8080에 떠 있고 $S/api.log가 있는 상태에서 호출.
# 출력: health <code> / prom-app-tag <n> / cb <code> / traced-log-lines <n> / export-errors <n>
actuator_probe() {
  curl -s -o /dev/null localhost:8080/contracts/nope
  printf 'health %s\n' "$(curl -s -o /dev/null -w '%{http_code}' localhost:8080/actuator/health)"
  printf 'prom-app-tag %s\n' "$(curl -s localhost:8080/actuator/prometheus | grep http_server_requests_seconds_count | grep -c 'application="api"')"
  printf 'cb %s\n' "$(curl -s -o /dev/null -w '%{http_code}' localhost:8080/actuator/circuitbreakers)"
  printf 'traced-log-lines %s\n' "$(grep -cE '\[[0-9a-f]{32}-[0-9a-f]{16}\]' $S/api.log)"
  printf 'export-errors %s\n' "$(grep -ci 'failed to export\|connection refused' $S/api.log)"
}
# api runtimeClasspath에 두 스타터가 들어왔는지. 출력: observability <n> / resilience <n>
deps_has() {
  local out; out=$(cd "$1" && ./gradlew :apps:api:dependencies --configuration runtimeClasspath -q --console=plain 2>/dev/null)
  printf 'observability %s\n' "$(printf '%s' "$out" | grep -c 'observability-starter')"
  printf 'resilience %s\n' "$(printf '%s' "$out" | grep -c 'resilience4j-spring-boot4')"
}
```

`traced-log-lines`는 요청 범위 로그가 있어야 1 이상이므로, 검증 시 `api_up` 전에 `export LOGGING_LEVEL_WEB=DEBUG`를 하고 끝난 뒤 `unset` 한다(Boot는 Micrometer Tracing이 classpath에 있으면 콘솔 패턴에 `[traceId-spanId]` 49자 필드를 넣는다. 로거 이름은 환경변수로 넘기면 소문자로 바인딩되므로 로그 그룹 `web`을 쓴다).

- [x] **Step 3: 함수 로드 확인**

```bash
source $S/poc.sh && type actuator_probe deps_has | head -2
```
Expected: 두 함수가 `shell function`으로 나온다.

- [x] **Step 4: 계획 파일 커밋**

```bash
cd /Users/gwanhokim/personal-projects/insurance-poc/insurance-platform-poc
git add docs/superpowers/plans/2026-10-25-phase6-observability-resilience-exp10.md
git commit -m "Add Phase 6 plan: observability and resilience starters, experiment 10"
git push -q origin main
```

---

## Task 1: 실험 10 사전 단계 — 세 contract가 api에 자기 의존성 추가

**Files:**
- Modify: `demo-{a,b,c}-contract/apps/api/build.gradle.kts` (http-starter 줄 바로 아래 1줄)

**Interfaces:**
- Produces: A contract의 `apps/api/build.gradle.kts`가 upstream과 달라져 Task 5의 머지 충돌 조건이 된다. B/C는 프로젝트 소유 파일이라 충돌이 구조적으로 불가능하다.

- [x] **Step 1: 세 contract에 `commons-lang3` 줄 추가**

삽입 위치는 세 레포 모두 "http-starter 의존성 줄 바로 아래"(플랫폼이 Task 2~4에서 스타터를 넣는 자리와 같다). 버전은 Boot BOM(A는 convention, B/C는 platform-bom 경유)이 관리한다.

```bash
cd /Users/gwanhokim/personal-projects/insurance-poc
perl -pi -e 's|^(    implementation\(project\(":platform:http-starter"\)\))$|$1\n    implementation("org.apache.commons:commons-lang3")|' demo-a-contract/apps/api/build.gradle.kts
for r in demo-b-contract demo-c-contract; do
  perl -pi -e 's|^(    implementation\(libs\.platform\.http\.starter\))$|$1\n    implementation("org.apache.commons:commons-lang3")|' $r/apps/api/build.gradle.kts
done
grep -n 'commons-lang3' demo-{a,b,c}-contract/apps/api/build.gradle.kts
```
Expected: 세 파일에 각 1줄, http-starter 줄 다음 행.

- [x] **Step 2: 세 contract 빌드(api만) 확인**

```bash
source $S/poc.sh
for r in demo-a-contract demo-b-contract demo-c-contract; do (cd $ROOT/$r && ./gradlew :apps:api:build --console=plain -q 2>&1 | grep -E 'FAIL|error:' || echo "$r ok"); done
```
Expected: 세 줄 `ok`.

- [x] **Step 3: 커밋·push·CI**

```bash
for r in demo-a-contract demo-b-contract demo-c-contract; do
  (cd $ROOT/$r && git add apps/api/build.gradle.kts && git commit -q -m "Add commons-lang3 to api" && git push -q origin main && echo "$r $(git rev-parse --short HEAD)")
done
for r in demo-a-contract demo-b-contract demo-c-contract; do run_wait $r ci; done
```
Expected: 세 SHA, 세 `ok`. SHA는 기록용으로 메모(기록의 "프로젝트 측 사전 변경").

---

## Task 2: A 플랫폼 — 두 스타터 추가, `v1.6.0`

**Files:**
- Create: `demo-a-platform/platform/observability-starter/**`, `demo-a-platform/platform/resilience-starter/**` (파일 구조 표 참조)
- Modify: `demo-a-platform/gradle/libs.versions.toml`, `settings.gradle.kts`, `apps/api/build.gradle.kts`, `apps/admin/build.gradle.kts`, `README.md`

**Interfaces:**
- Produces: `v1.6.0` 태그. 스타터 소스는 Task 3·4가 그대로 복사한다(B/C는 `build.gradle.kts`에 `maven-publish`만 더한다).

- [x] **Step 1: 브랜치와 카탈로그 버전**

```bash
cd $ROOT/demo-a-platform && git checkout -q -b observability-resilience-starters
perl -0pi -e 's|jackson = "3.1.8"\n|jackson = "3.1.8"\nresilience4j = "2.4.0"\n|; s|(kotlin-test-junit5 = \{[^\n]*\n)|$1resilience4j-spring-boot4 = \{ module = "io.github.resilience4j:resilience4j-spring-boot4", version.ref = "resilience4j" \}\n|' gradle/libs.versions.toml
grep -n resilience4j gradle/libs.versions.toml
```
Expected: `[versions]`에 1줄, `[libraries]`에 1줄.

- [x] **Step 2: observability-starter 빌드 파일**

`platform/observability-starter/build.gradle.kts`:

```kotlin
plugins {
    id("platform.kotlin-library")
}

dependencies {
    api("org.springframework.boot:spring-boot-starter-actuator")
    api("org.springframework.boot:spring-boot-starter-micrometer-metrics")
    api("io.micrometer:micrometer-registry-prometheus")
    api("org.springframework.boot:spring-boot-starter-opentelemetry")

    testImplementation("org.springframework.boot:spring-boot-starter-webmvc")
    testImplementation("org.springframework.boot:spring-boot-starter-test")
    testImplementation("org.springframework.boot:spring-boot-starter-webmvc-test")
}
```

- [x] **Step 3: observability-starter 기본값과 프로세서**

`platform/observability-starter/src/main/resources/platform-observability-defaults.yml`:

```yaml
# Platform observability defaults. Lowest precedence: any app property overrides these.
management:
  endpoints:
    web:
      exposure:
        include: health,info,metrics,prometheus,circuitbreakers,retries
  observations:
    key-values:
      application: ${spring.application.name:unknown}
  tracing:
    sampling:
      probability: 1.0
  otlp:
    metrics:
      export:
        enabled: false
```

`platform/observability-starter/src/main/resources/META-INF/spring.factories`:

```properties
org.springframework.boot.EnvironmentPostProcessor=\
io.github.khkim6040.platform.observability.PlatformObservabilityEnvironmentPostProcessor
```

`platform/observability-starter/src/main/kotlin/io/github/khkim6040/platform/observability/PlatformObservabilityEnvironmentPostProcessor.kt`:

```kotlin
package io.github.khkim6040.platform.observability

import org.springframework.boot.EnvironmentPostProcessor
import org.springframework.boot.SpringApplication
import org.springframework.boot.env.YamlPropertySourceLoader
import org.springframework.core.env.ConfigurableEnvironment
import org.springframework.core.io.ClassPathResource

/** Registers platform-observability-defaults.yml with the lowest precedence so every app property wins. */
class PlatformObservabilityEnvironmentPostProcessor : EnvironmentPostProcessor {
    override fun postProcessEnvironment(environment: ConfigurableEnvironment, application: SpringApplication) {
        YamlPropertySourceLoader()
            .load("platform-observability-defaults", ClassPathResource("platform-observability-defaults.yml"))
            .forEach { environment.propertySources.addLast(it) }
    }
}
```

- [x] **Step 4: observability-starter 테스트**

`platform/observability-starter/src/test/kotlin/io/github/khkim6040/platform/observability/ObservabilityTestApplication.kt`:

```kotlin
package io.github.khkim6040.platform.observability

import org.springframework.boot.autoconfigure.SpringBootApplication

@SpringBootApplication
class ObservabilityTestApplication
```

`platform/observability-starter/src/test/kotlin/io/github/khkim6040/platform/observability/PlatformObservabilityStarterTest.kt`:

```kotlin
package io.github.khkim6040.platform.observability

import io.micrometer.tracing.Tracer
import org.assertj.core.api.Assertions.assertThat
import org.junit.jupiter.api.Test
import org.springframework.beans.factory.annotation.Autowired
import org.springframework.boot.test.context.SpringBootTest
import org.springframework.boot.webmvc.test.autoconfigure.AutoConfigureMockMvc
import org.springframework.core.env.Environment
import org.springframework.test.web.servlet.assertj.MockMvcTester

@SpringBootTest(properties = ["spring.application.name=probe"])
@AutoConfigureMockMvc
class PlatformObservabilityStarterTest {
    @Autowired lateinit var mvc: MockMvcTester
    @Autowired lateinit var env: Environment
    @Autowired lateinit var tracer: Tracer

    @Test
    fun `exposes health and prometheus endpoints by default`() {
        val health = mvc.get().uri("/actuator/health").exchange()
        assertThat(health).hasStatusOk()
        assertThat(health).bodyJson().extractingPath("$.status").isEqualTo("UP")

        val prometheus = mvc.get().uri("/actuator/prometheus").exchange()
        assertThat(prometheus).hasStatusOk()
        assertThat(prometheus.response.contentAsString).contains("jvm_memory_used_bytes")
    }

    @Test
    fun `tags observations with the application name and traces every request`() {
        assertThat(env.getProperty("management.observations.key-values.application")).isEqualTo("probe")
        assertThat(env.getProperty("management.tracing.sampling.probability")).isEqualTo("1.0")
        assertThat(env.getProperty("management.otlp.metrics.export.enabled")).isEqualTo("false")
        assertThat(tracer).isNotNull()
    }
}
```

- [x] **Step 5: resilience-starter 빌드 파일**

`platform/resilience-starter/build.gradle.kts`:

```kotlin
plugins {
    id("platform.kotlin-library")
}

dependencies {
    api(libs.resilience4j.spring.boot4)
    api("org.aspectj:aspectjweaver")

    testImplementation("org.springframework.boot:spring-boot-starter-test")
}
```

- [x] **Step 6: resilience-starter 기본값과 프로세서**

`platform/resilience-starter/src/main/resources/platform-resilience-defaults.yml`:

```yaml
# Platform resilience defaults. Lowest precedence: any app property overrides these.
resilience4j:
  circuitbreaker:
    configs:
      default:
        sliding-window-size: 10
        minimum-number-of-calls: 5
        failure-rate-threshold: 50
        wait-duration-in-open-state: 10s
        register-health-indicator: true
  retry:
    configs:
      default:
        max-attempts: 3
        wait-duration: 200ms
```

`platform/resilience-starter/src/main/resources/META-INF/spring.factories`:

```properties
org.springframework.boot.EnvironmentPostProcessor=\
io.github.khkim6040.platform.resilience.PlatformResilienceEnvironmentPostProcessor
```

`platform/resilience-starter/src/main/kotlin/io/github/khkim6040/platform/resilience/PlatformResilienceEnvironmentPostProcessor.kt`:

```kotlin
package io.github.khkim6040.platform.resilience

import org.springframework.boot.EnvironmentPostProcessor
import org.springframework.boot.SpringApplication
import org.springframework.boot.env.YamlPropertySourceLoader
import org.springframework.core.env.ConfigurableEnvironment
import org.springframework.core.io.ClassPathResource

/** Registers platform-resilience-defaults.yml with the lowest precedence so every app property wins. */
class PlatformResilienceEnvironmentPostProcessor : EnvironmentPostProcessor {
    override fun postProcessEnvironment(environment: ConfigurableEnvironment, application: SpringApplication) {
        YamlPropertySourceLoader()
            .load("platform-resilience-defaults", ClassPathResource("platform-resilience-defaults.yml"))
            .forEach { environment.propertySources.addLast(it) }
    }
}
```

- [x] **Step 7: resilience-starter 테스트**

`platform/resilience-starter/src/test/kotlin/io/github/khkim6040/platform/resilience/ResilienceTestApplication.kt`:

```kotlin
package io.github.khkim6040.platform.resilience

import io.github.resilience4j.circuitbreaker.annotation.CircuitBreaker
import io.github.resilience4j.retry.annotation.Retry
import org.springframework.boot.autoconfigure.SpringBootApplication
import org.springframework.stereotype.Component

@SpringBootApplication
class ResilienceTestApplication

@Component
class FlakyService {
    var calls = 0

    @Retry(name = "probe-retry")
    fun call(): String {
        calls++
        if (calls < 3) throw IllegalStateException("flaky")
        return "ok"
    }
}

@Component
class BrokenService {
    @CircuitBreaker(name = "probe-cb")
    fun call(): String = throw IllegalStateException("always broken")
}
```

`platform/resilience-starter/src/test/kotlin/io/github/khkim6040/platform/resilience/PlatformResilienceStarterTest.kt`:

```kotlin
package io.github.khkim6040.platform.resilience

import io.github.resilience4j.circuitbreaker.CallNotPermittedException
import io.github.resilience4j.circuitbreaker.CircuitBreaker
import io.github.resilience4j.circuitbreaker.CircuitBreakerRegistry
import org.assertj.core.api.Assertions.assertThat
import org.assertj.core.api.Assertions.assertThatThrownBy
import org.junit.jupiter.api.Test
import org.springframework.beans.factory.annotation.Autowired
import org.springframework.boot.test.context.SpringBootTest
import org.springframework.core.env.Environment

@SpringBootTest
class PlatformResilienceStarterTest {
    @Autowired lateinit var flaky: FlakyService
    @Autowired lateinit var broken: BrokenService
    @Autowired lateinit var registry: CircuitBreakerRegistry
    @Autowired lateinit var env: Environment

    @Test
    fun `retries three times by default`() {
        assertThat(flaky.call()).isEqualTo("ok")
        assertThat(flaky.calls).isEqualTo(3)
    }

    @Test
    fun `opens the circuit after five failing calls by default`() {
        repeat(5) { assertThatThrownBy { broken.call() }.isInstanceOf(IllegalStateException::class.java) }
        assertThat(registry.circuitBreaker("probe-cb").state).isEqualTo(CircuitBreaker.State.OPEN)
        assertThatThrownBy { broken.call() }.isInstanceOf(CallNotPermittedException::class.java)
    }

    @Test
    fun `platform defaults apply with lowest precedence`() {
        assertThat(env.getProperty("resilience4j.retry.configs.default.max-attempts")).isEqualTo("3")
        assertThat(env.getProperty("resilience4j.circuitbreaker.configs.default.minimum-number-of-calls")).isEqualTo("5")
    }
}
```

- [x] **Step 8: settings·앱 빌드 파일·README 배선**

```bash
cd $ROOT/demo-a-platform
perl -pi -e 's|^(    "platform:http-starter",)$|$1\n    "platform:observability-starter",\n    "platform:resilience-starter",|' settings.gradle.kts
perl -pi -e 's|^(    implementation\(project\(":platform:http-starter"\)\))$|$1\n    implementation(project(":platform:observability-starter"))\n    implementation(project(":platform:resilience-starter"))|' apps/api/build.gradle.kts
perl -pi -e 's|^(    implementation\(project\(":platform:http-starter"\)\))$|$1\n    implementation(project(":platform:observability-starter"))|' apps/admin/build.gradle.kts
perl -pi -e 's|^(- `platform/http-starter`.*)$|$1\n- `platform/observability-starter`: Actuator, Prometheus, OpenTelemetry tracing 기본값\n- `platform/resilience-starter`: Resilience4j Circuit Breaker·Retry 기본값|' README.md
git diff --stat
```
Expected: 5파일 변경(toml, settings, api, admin, README).

- [x] **Step 9: 스타터 테스트 실행**

```bash
cd $ROOT/demo-a-platform && ./gradlew :platform:observability-starter:test :platform:resilience-starter:test --console=plain -q 2>&1 | tail -20
```
Expected: 출력 없음(테스트 5개 통과). 실패하면 원인을 본다.
- `Tracer` 빈 없음 → `spring-boot-starter-opentelemetry`가 브리지를 안 가져온 것. `api("io.micrometer:micrometer-tracing-bridge-otel")`을 observability 빌드 파일에 추가하고 재실행.
- resilience 컨텍스트 기동 실패(`NoClassDefFoundError`, `BeanCreationException` 등 Boot 4.1 비호환) → **Step 9b**.

- [x] **Step 9b (resilience4j가 Boot 4.1에서 안 뜰 때만): Spring Framework 7 `@Retryable` 대체안**

스펙 8장의 대체안: Retry만 제공, Circuit Breaker 제외. 아래로 바꾸고 Step 9를 다시 돈다. 기록(Task 7)의 복원력 내용을 "Retry만"으로 적는다.

`platform/resilience-starter/build.gradle.kts`:

```kotlin
plugins {
    id("platform.kotlin-library")
}

dependencies {
    api("org.springframework.boot:spring-boot-starter")

    testImplementation("org.springframework.boot:spring-boot-starter-test")
}
```

`platform-resilience-defaults.yml`, `spring.factories`, `PlatformResilienceEnvironmentPostProcessor.kt`는 삭제한다(`@Retryable`은 애너테이션 속성으로 설정하므로 프로퍼티 기본값이 없다). 대신:

`platform/resilience-starter/src/main/kotlin/io/github/khkim6040/platform/resilience/PlatformResilienceAutoConfiguration.kt`:

```kotlin
package io.github.khkim6040.platform.resilience

import org.springframework.boot.autoconfigure.AutoConfiguration
import org.springframework.resilience.annotation.EnableResilientMethods

/** Turns on Spring Framework 7 @Retryable / @ConcurrencyLimit for every app that depends on this starter. */
@AutoConfiguration
@EnableResilientMethods
class PlatformResilienceAutoConfiguration
```

`platform/resilience-starter/src/main/resources/META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports`:

```text
io.github.khkim6040.platform.resilience.PlatformResilienceAutoConfiguration
```

`ResilienceTestApplication.kt`:

```kotlin
package io.github.khkim6040.platform.resilience

import org.springframework.boot.autoconfigure.SpringBootApplication
import org.springframework.resilience.annotation.Retryable
import org.springframework.stereotype.Component

@SpringBootApplication
class ResilienceTestApplication

@Component
class FlakyService {
    var calls = 0

    @Retryable(maxAttempts = 3, delay = 200)
    fun call(): String {
        calls++
        if (calls < 3) throw IllegalStateException("flaky")
        return "ok"
    }
}
```

`PlatformResilienceStarterTest.kt`:

```kotlin
package io.github.khkim6040.platform.resilience

import org.assertj.core.api.Assertions.assertThat
import org.junit.jupiter.api.Test
import org.springframework.beans.factory.annotation.Autowired
import org.springframework.boot.test.context.SpringBootTest

@SpringBootTest
class PlatformResilienceStarterTest {
    @Autowired lateinit var flaky: FlakyService

    @Test
    fun `retries three times`() {
        assertThat(flaky.call()).isEqualTo("ok")
        assertThat(flaky.calls).isEqualTo(3)
    }
}
```

`gradle/libs.versions.toml`의 `resilience4j` 두 줄은 지운다. `actuator_probe`의 `cb` 행은 404가 정상이 된다(기록에 그대로 적는다).

- [x] **Step 10: 전체 빌드와 로컬 기동 검증**

```bash
cd $ROOT/demo-a-platform && ./gradlew build --console=plain -q 2>&1 | grep -E 'FAIL|error:' || echo "build ok"; tests_total .
export LOGGING_LEVEL_WEB=DEBUG
api_up $ROOT/demo-a-platform && actuator_probe; api_down
unset LOGGING_LEVEL_WEB
```
Expected: 빌드 통과, 테스트 총수(이전 25 + 5 = 30 근처, 실측 기록). `health 200`, `prom-app-tag` ≥ 1, `cb 200`(9b면 404), `traced-log-lines` ≥ 1, `export-errors 0`. `prom-app-tag`가 0이면 `management.observations.key-values`가 http.server.requests에 안 붙은 것이므로 멈추고 보고한다.

- [x] **Step 11: 커밋 분리 → PR → 머지 → 태그**

```bash
cd $ROOT/demo-a-platform
git add gradle/libs.versions.toml platform/observability-starter platform/resilience-starter settings.gradle.kts
git commit -q -m "Add observability and resilience platform starters"
git add apps/api/build.gradle.kts apps/admin/build.gradle.kts README.md
git commit -q -m "Wire observability and resilience starters into api and admin"
pr_merge demo-a-platform observability-resilience-starters
git tag v1.6.0 && git push -q origin v1.6.0 && git log --oneline -1
run_wait demo-a-platform ci
```
Expected: PR 번호(#6 예상), 머지 SHA = `v1.6.0`, main CI `ok`. 플랫폼 측 단계: ① 코드(파일 수는 `git diff --stat v1.5.0 v1.6.0 | tail -1`로 실측) ② PR → CI → 머지 ③ 태그 = **3단계**.

---

## Task 3: B 플랫폼 — 두 스타터 퍼블리시, 템플릿 핀

**Files:**
- Create: `demo-b-platform/platform-observability-starter/**`, `demo-b-platform/platform-resilience-starter/**`
- Modify: `demo-b-platform/gradle/libs.versions.toml`, `settings.gradle.kts`, `platform-bom/build.gradle.kts`, `platform-catalog/build.gradle.kts`
- Modify: `demo-b-template/gradle.properties`, `.github/workflows/release.yml`, `apps/api/build.gradle.kts`, `apps/admin/build.gradle.kts`

- [x] **Step 1: 브랜치, 카탈로그 버전, 스타터 소스 복사**

A에서 통과한 소스를 그대로 가져온다(Step 9b를 탔다면 그 결과물이 복사된다).

```bash
cd $ROOT/demo-b-platform && git checkout -q -b observability-resilience-starters
perl -0pi -e 's|jackson = "3.1.8"\n|jackson = "3.1.8"\nresilience4j = "2.4.0"\n|; s|(kotlin-test-junit5 = \{[^\n]*\n)|$1resilience4j-spring-boot4 = \{ module = "io.github.resilience4j:resilience4j-spring-boot4", version.ref = "resilience4j" \}\n|' gradle/libs.versions.toml
for s in observability resilience; do
  mkdir -p platform-$s-starter && cp -R $ROOT/demo-a-platform/platform/$s-starter/src platform-$s-starter/
  cp $ROOT/demo-a-platform/platform/$s-starter/build.gradle.kts platform-$s-starter/build.gradle.kts
  perl -0pi -e 's|    id\("platform.kotlin-library"\)\n\}|    id("platform.kotlin-library")\n    `maven-publish`\n}|' platform-$s-starter/build.gradle.kts
  cat >> platform-$s-starter/build.gradle.kts <<'EOF'

publishing {
    publications {
        create<MavenPublication>("starter") {
            from(components["java"])
        }
    }
}
EOF
done
perl -pi -e 's|^(    "platform-http-starter",)$|$1\n    "platform-observability-starter",\n    "platform-resilience-starter",|' settings.gradle.kts
perl -pi -e 's|^(        api\("io.github.khkim6040.platform:platform-http-starter:\$\{project.version\}"\))$|$1\n        api("io.github.khkim6040.platform:platform-observability-starter:\${project.version}")\n        api("io.github.khkim6040.platform:platform-resilience-starter:\${project.version}")|' platform-bom/build.gradle.kts
perl -pi -e 's|^(        library\("platform-http-starter", "io.github.khkim6040.platform", "platform-http-starter"\).versionRef\("platform"\))$|$1\n        library("platform-observability-starter", "io.github.khkim6040.platform", "platform-observability-starter").versionRef("platform")\n        library("platform-resilience-starter", "io.github.khkim6040.platform", "platform-resilience-starter").versionRef("platform")|' platform-catalog/build.gradle.kts
git status --short | wc -l; grep -c 'starter' platform-bom/build.gradle.kts platform-catalog/build.gradle.kts settings.gradle.kts
```
Expected: bom 3, catalog 3, settings 3 (`http`+2). 9b를 탔다면 toml의 resilience4j 두 줄은 넣지 않는다.

- [x] **Step 2: 빌드·publishToMavenLocal 검증**

```bash
cd $ROOT/demo-b-platform && ./gradlew build publishToMavenLocal -PplatformVersion=0.0.0-LOCAL --console=plain -q 2>&1 | grep -E 'FAIL|error:' || echo "build ok"
ls ~/.m2/repository/io/github/khkim6040/platform/ | tr '\n' ' '
```
Expected: exit 0, 디렉터리에 `platform-observability-starter platform-resilience-starter` 포함.

- [x] **Step 3: 커밋 → PR → 태그 → publish 대기**

```bash
cd $ROOT/demo-b-platform
git add -A && git commit -q -m "Add observability and resilience platform starters"
pr_merge demo-b-platform observability-resilience-starters
git tag v1.6.0 && git push -q origin v1.6.0 && git log --oneline -1
run_wait demo-b-platform publish
```
Expected: PR(#6 예상), publish `ok`. 아티팩트 존재는 Step 4의 템플릿 빌드(1.6.0 해석)로 확인한다.

- [x] **Step 4: 템플릿 핀 + 템플릿 앱 배선 (publish 뒤, 별도 레포)**

```bash
cd $ROOT/demo-b-template
perl -pi -e 's|^platformVersion=1\.5\.0$|platformVersion=1.6.0|' gradle.properties
perl -pi -e 's|release-app\.yml\@v1\.5\.0|release-app.yml\@v1.6.0|' .github/workflows/release.yml
perl -pi -e 's|^(    implementation\(libs\.platform\.http\.starter\))$|$1\n    implementation(libs.platform.observability.starter)\n    implementation(libs.platform.resilience.starter)|' apps/api/build.gradle.kts
perl -pi -e 's|^(    implementation\(libs\.platform\.http\.starter\))$|$1\n    implementation(libs.platform.observability.starter)|' apps/admin/build.gradle.kts
./gradlew :apps:api:build :apps:admin:build --console=plain -q 2>&1 | grep -E 'FAIL|error:' || echo "build ok"
git add -A && git commit -q -m "Pin template to platform 1.6.0 and wire new starters" && git push -q origin main && git log --oneline -1
run_wait demo-b-template ci
```
Expected: 4파일 변경, 빌드 통과(1.6.0 아티팩트 해석), CI `ok`. 플랫폼 측 단계: ① 코드 ② PR → CI → 머지 ③ 태그 ④ publish 대기 ⑤ 템플릿 레포 4파일 → push → CI = **5단계**.

---

## Task 4: C 플랫폼 — 두 스타터 퍼블리시, 템플릿 배선 (같은 PR)

**Files:**
- Create: `demo-c-platform/platform-observability-starter/**`, `demo-c-platform/platform-resilience-starter/**`
- Modify: `demo-c-platform/gradle/libs.versions.toml`, `settings.gradle.kts`, `platform-bom/build.gradle.kts`, `platform-catalog/build.gradle.kts`, `templates/multi-service/gradle.properties`, `templates/multi-service/.github/workflows/release.yml`, `templates/multi-service/apps/{api,admin}/build.gradle.kts`

- [x] **Step 1: 브랜치, 카탈로그 버전, 스타터 소스 복사, BOM·카탈로그(`cplatform`)**

```bash
cd $ROOT/demo-c-platform && git checkout -q -b observability-resilience-starters
perl -0pi -e 's|jackson = "3.1.8"\n|jackson = "3.1.8"\nresilience4j = "2.4.0"\n|; s|(kotlin-test-junit5 = \{[^\n]*\n)|$1resilience4j-spring-boot4 = \{ module = "io.github.resilience4j:resilience4j-spring-boot4", version.ref = "resilience4j" \}\n|' gradle/libs.versions.toml
for s in observability resilience; do
  mkdir -p platform-$s-starter && cp -R $ROOT/demo-b-platform/platform-$s-starter/src platform-$s-starter/
  cp $ROOT/demo-b-platform/platform-$s-starter/build.gradle.kts platform-$s-starter/build.gradle.kts
done
perl -pi -e 's|^(    "platform-http-starter",)$|$1\n    "platform-observability-starter",\n    "platform-resilience-starter",|' settings.gradle.kts
perl -pi -e 's|^(        api\("io.github.khkim6040.cplatform:platform-http-starter:\$\{project.version\}"\))$|$1\n        api("io.github.khkim6040.cplatform:platform-observability-starter:\${project.version}")\n        api("io.github.khkim6040.cplatform:platform-resilience-starter:\${project.version}")|' platform-bom/build.gradle.kts
perl -pi -e 's|^(        library\("platform-http-starter", "io.github.khkim6040.cplatform", "platform-http-starter"\).versionRef\("platform"\))$|$1\n        library("platform-observability-starter", "io.github.khkim6040.cplatform", "platform-observability-starter").versionRef("platform")\n        library("platform-resilience-starter", "io.github.khkim6040.cplatform", "platform-resilience-starter").versionRef("platform")|' platform-catalog/build.gradle.kts
grep -c 'starter' platform-bom/build.gradle.kts platform-catalog/build.gradle.kts settings.gradle.kts
```
Expected: bom 3, catalog 3, settings 3. Task 2에서 Step 9b를 탔다면 toml의 resilience4j 두 줄은 넣지 않는다.

- [x] **Step 2: 템플릿 핀과 템플릿 앱 배선 (같은 PR)**

```bash
cd $ROOT/demo-c-platform/templates/multi-service
perl -pi -e 's|^platformVersion=1\.5\.0$|platformVersion=1.6.0|' gradle.properties
perl -pi -e 's|release-app\.yml\@v1\.5\.0|release-app.yml\@v1.6.0|' .github/workflows/release.yml
perl -pi -e 's|^(    implementation\(libs\.platform\.http\.starter\))$|$1\n    implementation(libs.platform.observability.starter)\n    implementation(libs.platform.resilience.starter)|' apps/api/build.gradle.kts
perl -pi -e 's|^(    implementation\(libs\.platform\.http\.starter\))$|$1\n    implementation(libs.platform.observability.starter)|' apps/admin/build.gradle.kts
cd $ROOT/demo-c-platform && git status --short | wc -l
```
Expected: 변경 파일 수 = 기존 4(toml, settings, bom, catalog) + 템플릿 4 + 새 모듈 파일들.

- [x] **Step 3: 빌드·publishToMavenLocal 검증**

```bash
cd $ROOT/demo-c-platform && ./gradlew build publishToMavenLocal -PplatformVersion=0.0.0-LOCAL --console=plain -q 2>&1 | grep -E 'FAIL|error:' || echo "build ok"
ls ~/.m2/repository/io/github/khkim6040/cplatform/ | tr '\n' ' '
```
Expected: exit 0, 두 새 스타터 디렉터리.

- [x] **Step 4: 커밋 → PR → 태그 → publish 대기**

```bash
cd $ROOT/demo-c-platform
git add -A && git commit -q -m "Add observability and resilience platform starters"
pr_merge demo-c-platform observability-resilience-starters
git tag v1.6.0 && git push -q origin v1.6.0 && git log --oneline -1
run_wait demo-c-platform publish
```
Expected: PR(#6 예상), publish `ok`. 아티팩트 존재는 Task 5 Step 6의 contract 빌드로 확인한다. 플랫폼 측 단계: ① 코드(템플릿 포함) ② PR → CI → 머지 ③ 태그 ④ publish 대기 = **4단계**. 템플릿 핀이 같은 PR에 들어가므로 B의 ⑤가 없다.

---

## Task 5: 실험 10 — contract 전파 (A 충돌 1 예상)

**Files:**
- Modify: `demo-a-contract` (revert-of-revert 커밋, `v1.6.0` 머지 커밋, 충돌 해소 `apps/api/build.gradle.kts`)
- Modify: `demo-{b,c}-contract/gradle.properties`, `apps/api/build.gradle.kts`, `apps/admin/build.gradle.kts`

**Interfaces:**
- Consumes: Task 1의 `commons-lang3` 줄, Task 2~4의 `v1.6.0`.

- [x] **Step 1: A contract — v1.5.0 되돌림을 다시 되돌림(재올림 비용)**

실험 8의 함정: revert된 머지 위에 `v1.6.0`을 머지하면 v1.5.0 내용(graceful)은 돌아오지 않는다. 먼저 revert 커밋을 revert한다.

```bash
cd $ROOT/demo-a-contract && git revert --no-edit 0e25686 && git log --oneline -1
grep -c 'graceful' platform/http-starter/src/main/resources/platform-defaults.yml
```
Expected: 커밋 `Revert "Revert "Merge tag 'v1.5.0'""`, graceful 1.

- [x] **Step 2: A contract — `v1.6.0` 머지, 충돌 확인**

```bash
cd $ROOT/demo-a-contract && git fetch -q upstream tag v1.6.0 --no-tags
git merge v1.6.0 2>&1 | tail -5
git diff --name-only --diff-filter=U
```
Expected: `CONFLICT (content): Merge conflict in apps/api/build.gradle.kts`, 충돌 파일 목록 정확히 1개. (admin은 프로젝트가 안 건드렸으므로 깨끗히 들어온다.) 충돌이 0이면 그대로 기록하고 관찰에 이유를 적는다.

- [x] **Step 3: A contract — 양쪽 유지로 해소**

마커를 지우고 세 줄을 모두 남긴다. 결과 `dependencies` 블록:

```kotlin
dependencies {
    implementation(project(":libs:domain"))
    implementation(project(":platform:http-starter"))
    implementation("org.apache.commons:commons-lang3")
    implementation(project(":platform:observability-starter"))
    implementation(project(":platform:resilience-starter"))

    testImplementation("org.springframework.boot:spring-boot-starter-webmvc-test")
}
```

```bash
cd $ROOT/demo-a-contract
perl -0pi -e 's|<<<<<<< HEAD\n||; s|=======\n||; s|>>>>>>> v1\.6\.0\n||' apps/api/build.gradle.kts
grep -c '<<<<<<<\|>>>>>>>\|=======' apps/api/build.gradle.kts; grep -c 'implementation(' apps/api/build.gradle.kts
git add apps/api/build.gradle.kts && git commit -q --no-edit && git log --oneline -1
git diff --stat HEAD~1 HEAD | tail -1
```
Expected: 마커 0, `implementation(` 5. 머지 커밋 `Merge tag 'v1.6.0'`. 마지막 줄의 파일 수가 "들어온 파일 수"(새 모듈 + toml + settings + api/admin + README).

- [x] **Step 4: A contract — 빌드·기동 검증·push·CI**

```bash
cd $ROOT/demo-a-contract && ./gradlew clean build --console=plain -q 2>&1 | grep -E 'FAIL|error:' || echo "build ok"; tests_total .
grep -n 'read-timeout\|shutdown' platform/http-starter/src/main/resources/platform-defaults.yml
deps_has .
export LOGGING_LEVEL_WEB=DEBUG
api_up . && actuator_probe; api_down
unset LOGGING_LEVEL_WEB
git push -q origin main && run_wait demo-a-contract ci
```
Expected: 빌드 통과, 테스트 수 실측(스타터 테스트 5개 추가). `read-timeout: 3s`(위반 유지) + `shutdown: graceful`(재올림). `observability` ≥ 1, `resilience` ≥ 1. `health 200`, `prom-app-tag` ≥ 1, `cb 200`, `traced-log-lines` ≥ 1, `export-errors 0`. CI `ok`. 프로젝트 측 단계: ① revert-of-revert ② 태그 머지 + 충돌 1파일 해소 ③ push → CI = **3단계**, 손댄 파일 1.

- [x] **Step 5: B contract — 숫자 1줄 + 앱 의존성 3줄**

```bash
cd $ROOT/demo-b-contract
perl -pi -e 's|^platformVersion=1\.3\.0$|platformVersion=1.6.0|' gradle.properties
perl -pi -e 's|^(    implementation\("org.apache.commons:commons-lang3"\))$|$1\n    implementation(libs.platform.observability.starter)\n    implementation(libs.platform.resilience.starter)|' apps/api/build.gradle.kts
perl -pi -e 's|^(    implementation\(libs\.platform\.http\.starter\))$|$1\n    implementation(libs.platform.observability.starter)|' apps/admin/build.gradle.kts
git status --short
./gradlew clean build --console=plain -q 2>&1 | grep -E 'FAIL|error:' || echo "build ok"; tests_total .
deps_has .
export LOGGING_LEVEL_WEB=DEBUG
api_up . && actuator_probe; api_down
unset LOGGING_LEVEL_WEB
git add -A && git commit -q -m "Take platform 1.6.0 and add observability and resilience starters" && git push -q origin main && git log --oneline -1
run_wait demo-b-contract ci
```
Expected: 3파일 변경, 빌드 통과(테스트 수 실측, 스타터 테스트는 아티팩트라 포함 안 됨), `observability 1`·`resilience` ≥ 1, probe 전 항목 통과, CI `ok`. 프로젝트 측: **1단계**, 손댄 파일 3, 충돌 0. 함께 끌려온 변경: 1.4.0(Dockerfile, Maven 아티팩트엔 영향 없음)·1.5.0(graceful 기본값) — 실험 8에서 되돌렸던 graceful이 이번 올림으로 다시 들어온다(1).

- [x] **Step 6: C contract — B와 동일**

```bash
cd $ROOT/demo-c-contract
perl -pi -e 's|^platformVersion=1\.3\.0$|platformVersion=1.6.0|' gradle.properties
perl -pi -e 's|^(    implementation\("org.apache.commons:commons-lang3"\))$|$1\n    implementation(libs.platform.observability.starter)\n    implementation(libs.platform.resilience.starter)|' apps/api/build.gradle.kts
perl -pi -e 's|^(    implementation\(libs\.platform\.http\.starter\))$|$1\n    implementation(libs.platform.observability.starter)|' apps/admin/build.gradle.kts
git status --short
./gradlew clean build --console=plain -q 2>&1 | grep -E 'FAIL|error:' || echo "build ok"; tests_total .
deps_has .
export LOGGING_LEVEL_WEB=DEBUG
api_up . && actuator_probe; api_down
unset LOGGING_LEVEL_WEB
git add -A && git commit -q -m "Take platform 1.6.0 and add observability and resilience starters" && git push -q origin main && git log --oneline -1
run_wait demo-c-contract ci
```
Expected: B와 같다(`cplatform` 아티팩트).

---

## Task 6: 실험 10 — claims 전파 (손대지 않은 프로젝트의 경로)

**Files:**
- Modify: `demo-a-claims` (`v1.6.0` 머지 커밋), `demo-{b,c}-claims/gradle.properties`, `apps/api/build.gradle.kts`, `apps/admin/build.gradle.kts`

- [x] **Step 1: A claims — 태그 머지(충돌 0 예상)·검증·push**

```bash
cd $ROOT/demo-a-claims && git fetch -q upstream tag v1.6.0 --no-tags && git merge --no-edit v1.6.0 2>&1 | tail -2
git diff --name-only --diff-filter=U | wc -l; git diff --stat HEAD~1 HEAD | tail -1
./gradlew clean build --console=plain -q 2>&1 | grep -E 'FAIL|error:' || echo "build ok"; tests_total .
deps_has .
api_up . && actuator_probe; api_down
git push -q origin main && run_wait demo-a-claims ci
```
Expected: 충돌 0(claims는 빌드 파일을 안 건드렸으므로 api·admin 배선이 그대로 들어온다), 들어온 파일 수 실측. `observability` ≥ 1, `resilience` ≥ 1, `health 200`, `cb 200`(traced-log-lines는 DEBUG를 안 켰으므로 0이어도 됨), `export-errors 0`. CI `ok`. 프로젝트 측: **1단계**, 손댄 파일 0.

- [x] **Step 2: B claims — 3파일**

```bash
cd $ROOT/demo-b-claims
perl -pi -e 's|^platformVersion=1\.5\.0$|platformVersion=1.6.0|' gradle.properties
perl -pi -e 's|^(    implementation\(libs\.platform\.http\.starter\))$|$1\n    implementation(libs.platform.observability.starter)\n    implementation(libs.platform.resilience.starter)|' apps/api/build.gradle.kts
perl -pi -e 's|^(    implementation\(libs\.platform\.http\.starter\))$|$1\n    implementation(libs.platform.observability.starter)|' apps/admin/build.gradle.kts
git status --short
./gradlew clean build --console=plain -q 2>&1 | grep -E 'FAIL|error:' || echo "build ok"; tests_total .
deps_has .
api_up . && actuator_probe; api_down
git add -A && git commit -q -m "Take platform 1.6.0 and add observability and resilience starters" && git push -q origin main && git log --oneline -1
run_wait demo-b-claims ci
```
Expected: 3파일, 빌드 통과, deps 둘 다 ≥ 1, `health 200`·`cb 200`·`export-errors 0`, CI `ok`. 프로젝트 측 **1단계**, 손댄 파일 3. A와 달리 손댄 파일 0이 아니다: B/C에서 "새 스타터 채택"은 프로젝트가 앱마다 한 줄을 적는 opt-in이고, A에서는 플랫폼의 앱 빌드 파일이 머지로 들어오는 자동 적용이다(관찰에 적는다).

- [x] **Step 3: C claims — B와 동일**

```bash
cd $ROOT/demo-c-claims
perl -pi -e 's|^platformVersion=1\.5\.0$|platformVersion=1.6.0|' gradle.properties
perl -pi -e 's|^(    implementation\(libs\.platform\.http\.starter\))$|$1\n    implementation(libs.platform.observability.starter)\n    implementation(libs.platform.resilience.starter)|' apps/api/build.gradle.kts
perl -pi -e 's|^(    implementation\(libs\.platform\.http\.starter\))$|$1\n    implementation(libs.platform.observability.starter)|' apps/admin/build.gradle.kts
git status --short
./gradlew clean build --console=plain -q 2>&1 | grep -E 'FAIL|error:' || echo "build ok"; tests_total .
deps_has .
api_up . && actuator_probe; api_down
git add -A && git commit -q -m "Take platform 1.6.0 and add observability and resilience starters" && git push -q origin main && git log --oneline -1
run_wait demo-c-claims ci
```
Expected: B와 같다.

- [x] **Step 4: 최종 상태 점검**

```bash
cd $ROOT
for r in demo-a-platform demo-a-contract demo-a-claims demo-b-platform demo-b-template demo-b-contract demo-b-claims demo-c-platform demo-c-contract demo-c-claims; do
  printf '%-16s %s dirty=%s ahead=%s\n' $r "$(git -C $r rev-parse --short HEAD)" "$(git -C $r status --porcelain | wc -l | tr -d ' ')" "$(git -C $r rev-list --count @{u}..HEAD)"
done
grep -H platformVersion= demo-{b,c}-{contract,claims}/gradle.properties demo-b-template/gradle.properties demo-c-platform/templates/multi-service/gradle.properties
```
Expected: 모두 `dirty=0 ahead=0`, B/C 프로젝트·템플릿 모두 `1.6.0`.

---

## Task 7: 실험 10 기록과 계획 마감

**Files:**
- Create: `insurance-platform-poc/experiments/10-new-common-feature.md`
- Modify: `insurance-platform-poc/docs/superpowers/plans/2026-10-25-phase6-observability-resilience-exp10.md` (체크박스)

- [x] **Step 1: 기록 작성**

`experiments/10-new-common-feature.md`. 아래 표의 꺾쇠(`<…>`)는 Task 1~6에서 실측한 값으로 바꿔 쓴다. 꺾쇠가 남아 있으면 커밋하지 않는다.

```markdown
# 실험 10: 신규 공통 기능 (관측성·복원력 스타터 → contract·claims 전파)

## 시나리오와 성공 기준

플랫폼이 `observability-starter`(Actuator, Micrometer Prometheus, OpenTelemetry tracing, 기본 프로퍼티)와 `resilience-starter`(Resilience4j CB·Retry 기본 설정)를 추가해 `v1.6.0`으로 내고, contract·claims 여섯 프로젝트가 받는다. 스펙 5.4가 예상한 충돌 지점(프로젝트의 의존성 추가 vs 플랫폼의 스타터 추가)을 실제로 만들기 위해 세 contract는 먼저 `apps/api/build.gradle.kts`에 `commons-lang3` 한 줄을 넣었다(A에서는 소유권 규약 위반, 스펙이 명시한 측정 지점). claims는 손대지 않은 프로젝트의 경로다. 측정은 관측성으로 한다: `/actuator/health` 200, `/actuator/prometheus`의 `http_server_requests`에 `application="api"` 태그, `/actuator/circuitbreakers` 200, 요청 범위 로그 줄에 `[traceId-spanId]`.

## 결과

| 항목 | A | B | C |
|---|---|---|---|
| 플랫폼 측 수동 단계 수 (목록) | 3: ① 스타터 2모듈 + toml·settings·api·admin·README(<n>파일) ② PR → CI → 머지 ③ 태그 `v1.6.0` | 5: ① 스타터 2모듈 + toml·settings·BOM·카탈로그(<n>파일) ② PR → CI → 머지 ③ 태그 ④ publish 대기 ⑤ 템플릿 레포 4파일(핀 2 + api·admin 배선) → push → CI | 4: ① 스타터 2모듈 + toml·settings·BOM·카탈로그 + 템플릿 4파일(<n>파일) ② PR → CI → 머지 ③ 태그 ④ publish 대기 |
| 프로젝트 측 수동 단계 수, 프로젝트 1개당 (목록) | contract **3**: ① v1.5.0 revert의 revert ② `fetch tag` + `merge v1.6.0` + 충돌 1파일 해소 ③ push → CI. 손댄 파일 1, 들어온 파일 <n>. claims **1**: 머지 → push → CI, 손댄 파일 0 | contract **1**: `gradle.properties` 1줄 + api 2줄 + admin 1줄 → push → CI. 손댄 파일 3. claims 1, 손댄 파일 3 | B와 같음 |
| 머지 충돌 파일 수 | contract **<1>** (`apps/api/build.gradle.kts`, 같은 자리에 프로젝트 1줄 vs 플랫폼 2줄. 양쪽 유지로 해소). claims 0 | 0 (앱 빌드 파일은 프로젝트 소유, 플랫폼은 건드리지 않음) | 0 |
| 의미적 충돌 (빌드·테스트 실패, 동작 변화) | <없음/내용>. graceful 기본값이 재올림으로 돌아옴(의도) | <없음/내용>. 1.3.0 → 1.6.0 점프로 graceful 기본값이 들어옴(실험 8에서 되돌린 것) | B와 같음 |
| 함께 끌려온 무관한 변경 수 | contract: v1.5.0 재적용 1(graceful). claims 0 | 1 (graceful) | 1 |
| 검증 방법과 결과 | contract: `clean build` 테스트 <n>, `runtimeClasspath`에 두 스타터, probe `health 200 / prom-app-tag <n> / cb <200> / traced-log-lines <n> / export-errors 0`, `read-timeout: 3s` 유지, CI ok. claims: 테스트 <n>, deps 둘 다, `health 200 / cb <200>`, CI ok | contract: 테스트 <n>, deps(`platform-observability-starter:1.6.0`, `resilience4j-spring-boot4:2.4.0`), probe 같음, CI ok. claims: 테스트 <n>, probe, CI ok | B와 같음(`cplatform`) |
| 에이전트 개입 (사람 결정·행동이 필요했던 지점) | <0 또는 내용> | <0 또는 내용> | <0 또는 내용> |

## 근거: 커밋 SHA, PR, CI 실행 링크

- 사전(Task 1): `demo-a-contract` `<sha>`, `demo-b-contract` `<sha>`, `demo-c-contract` `<sha>` ("Add commons-lang3 to api")
- 플랫폼: `demo-a-platform` PR #<n> → `<sha>` = `v1.6.0`; `demo-b-platform` PR #<n> → `<sha>` = `v1.6.0`, publish <url>, `demo-b-template` `<sha>`; `demo-c-platform` PR #<n> → `<sha>` = `v1.6.0`, publish <url>
- contract: A `<revert-of-revert sha>`, `<merge sha>` (CI <url>); B `<sha>` (CI <url>); C `<sha>` (CI <url>)
- claims: A `<merge sha>` (CI <url>); B `<sha>`; C `<sha>`
- 스타터 검증(A 플랫폼 로컬): probe 출력 `<붙여넣기>`

## 관찰: 잘못하기 쉬운 지점, 자동화할 수 있는 단계

- A: 충돌은 예상대로 `apps/api/build.gradle.kts` 1파일. 해소 정책을 미리 정해 두지 않으면 `--ours`로 스타터가 빠지거나 `--theirs`로 프로젝트 의존성이 빠지며, 둘 다 빌드는 통과하므로(의미적 충돌) 알아차리기 어렵다.
- A: 되돌린 머지 위에 다음 버전을 머지하면 되돌린 내용은 돌아오지 않는다(실험 8 함정). 재올림에 revert-of-revert 1단계가 추가로 든다.
- A는 플랫폼이 앱 빌드 파일을 소유하므로 새 스타터가 머지로 **자동 적용**된다(claims 손댄 파일 0). B/C는 **opt-in**이라 프로젝트가 앱마다 한 줄을 적어야 한다(손댄 파일 3). 전파 비용은 B/C가 더 들지만, 적용 범위(어느 앱에 넣을지)를 프로젝트가 고른다.
- B/C: 템플릿 배선은 새 프로젝트에만 영향을 준다. 기존 프로젝트(contract·claims)에는 아무 효과가 없다. B는 publish 뒤 별도 레포에서 핀을 올려야 하는 순서 의존이 이번에도 있었다.
- 관측성 기본값은 http-starter와 독립된 yml·프로세서로 두어 세 기본값 파일이 키를 공유하지 않는다. 공유하면 `addLast` 순서(= spring.factories 로드 순서)가 승자를 정해 추적이 어렵다.
- <실행 중 드러난 추가 관찰>
```

- [x] **Step 2: 꺾쇠 잔존 확인과 커밋**

```bash
cd $ROOT/insurance-platform-poc
grep -c '<[^>]*>' experiments/10-new-common-feature.md
git add experiments/10-new-common-feature.md && git commit -q -m "Record experiment 10: new common feature propagation" && git push -q origin main && git log --oneline -1
```
Expected: 꺾쇠 0.

- [x] **Step 3: 계획 체크박스 모두 채우고 커밋**

```bash
cd $ROOT/insurance-platform-poc
perl -pi -e 's/^- \[ \]/- [x]/' docs/superpowers/plans/2026-10-25-phase6-observability-resilience-exp10.md
printf 'unticked=%s ticked=%s\n' "$(grep -c '^- \[ \]' docs/superpowers/plans/2026-10-25-phase6-observability-resilience-exp10.md)" "$(grep -c '^- \[x\]' docs/superpowers/plans/2026-10-25-phase6-observability-resilience-exp10.md)"
git add docs/superpowers/plans/2026-10-25-phase6-observability-resilience-exp10.md && git commit -q -m "Mark Phase 6 plan complete" && git push -q origin main && git status --porcelain | wc -l
```
Expected: `unticked=0`, 작업 트리 0.
