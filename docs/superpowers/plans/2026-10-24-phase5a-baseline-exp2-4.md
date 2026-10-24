# Phase 5a: baseline과 실험 2·3·4 실행 계획

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Phase 4 완료 시점의 세 플랫폼 부품 수를 `00-baseline.md`에 기록하고, 실험 2(다중 앱 PR, 한 번), 3(독립 배포, A/B/C), 4(보안 패치 Jackson 3.1.8, A/B/C)를 수행해 `02-`, `03-`, `04-` 기록 파일을 근거 링크와 함께 채운다. 실험 5~8은 Phase 5b 계획에서 다룬다.

**Architecture:** 실험은 스펙 7.2의 순서(2 → 3 → 4)로 수행하고, 실험마다 변경 → 검증 → 기록을 한 Task로 묶는다. 실험 2는 플랫폼 무관이므로 `demo-a-contract`에서 한 번만 하되, 이후 A안 머지(실험 4)가 프로젝트 소유 파일의 변경과 충돌하지 않음을 보이는 부수 효과를 얻는다. 실험 3은 세 contract에 같은 api 변경을 넣고 `api-v1.1.0` 태그로 api 이미지만 만들어지는지, 매니페스트 revert로 롤백되는지 본다. 실험 4는 Boot 4.1.2가 고정한 Jackson 3.1.7을 3.1.8로 강제한다. A는 카탈로그에 `jackson-bom`을 추가하고 컨벤션 플러그인이 플랫폼으로 적용 → 플랫폼 PR → contract가 upstream 머지 PR. B/C는 카탈로그 + `platform-bom`에 `jackson-bom` import → 플랫폼 PR → `v1.1.0` 퍼블리시 → contract가 `platformVersion` 한 줄 PR. 두 BOM이 같은 모듈에 다른 버전을 제약하면 Gradle은 높은 쪽(3.1.8)을 택한다.

**Tech Stack:** Phase 1~4와 동일. 추가로 `gh pr create/checks/merge`, `tools.jackson:jackson-bom:3.1.8`(Maven Central `maven-metadata.xml`로 존재 확인함), `kubectl kustomize`.

**Spec:** `docs/superpowers/specs/2026-10-24-insurance-platform-poc-design.md` (5.4 소유권 규약, 6.2~6.3 릴리스·롤백, 7.1 기록 양식·baseline, 7.2 실험 2·3·4, 7.3 평가 기준)

## Global Constraints

- 레포 경로 `/Users/gwanhokim/personal-projects/insurance-poc/<레포>`. 기록은 `insurance-platform-poc/experiments/`에 쓴다.
- 모든 Gradle·java 명령은 `export JAVA_HOME=$(/usr/libexec/java_home -v 25)` 후 실행한다.
- 시작 상태: `demo-a-platform` `95d383a`, `demo-a-contract` `d05f63f`, `demo-b-platform` `v1.0.0`=`61f4281`, `demo-b-contract` `c5823ec`, `demo-c-platform` `v1.0.0`=`4d80703`, `demo-c-contract` `2854805`. 세 contract의 코드 패키지는 모두 `io.github.khkim6040.contract.*`라 소스 경로가 같다.
- 실험 2·4는 실제 GitHub PR로 한다(스펙 7.2). 플랫폼 변경도, 프로젝트 반영도 PR이다. 머지는 `gh pr merge --merge --delete-branch`(머지 커밋). 실험 3은 main 직접 push.
- A안 소유권 규약(스펙 5.4): contract는 `platform/**`, `build-logic/**`, `gradle/**`, 루트 빌드 파일, `apps/*/build.gradle.kts`, `Dockerfile`, `.github/**`, `deploy/base/**`를 건드리지 않는다. 실험 2·3의 변경은 모두 프로젝트 소유 파일(`apps/*/src/**`, `libs/**`, `deploy/overlays/**`)이다.
- 보안 패치 대상: Jackson `3.1.7` → `3.1.8`(`tools.jackson.core:jackson-core`, `jackson-databind`, `tools.jackson.module:jackson-module-kotlin`). `tools.jackson:jackson-bom:3.1.8`을 플랫폼으로 import해 셋을 한 번에 올린다. 플랫폼 버전은 A/B/C 모두 `v1.1.0` 태그(A는 참조용, 워크플로 트리거 없음: `v1.1.0`은 `*-v*` 패턴에 맞지 않음).
- B/C contract의 `release.yml` `@v1.0.0`은 이번에 올리지 않는다(릴리스 워크플로·Dockerfile 변경 없음). 두 숫자가 어긋난 상태를 관찰에 적는다.
- 측정은 "수동 단계 수(목록)", "손댄 파일 수", "충돌 파일 수", "함께 끌려온 변경 수"다. 시간은 측정하지 않는다. 각 Task의 마지막 Step이 기록이다.
- 커밋은 영어 제목 한 줄. 외부 쓰기(push, PR, 태그, 퍼블리시, 이미지)는 스펙 승인 범위. 삭제·force는 없다.
- `gh`는 항상 `-R khkim6040/<레포>`를 명시한다.
- macOS `sed -i`를 쓰지 않고 `perl -pi -e`를 쓴다.

---

## 파일 구조

### insurance-platform-poc

| 파일 | 내용 |
|---|---|
| `experiments/00-baseline.md` | 세 플랫폼의 움직이는 부품 수와 구조적 속성 (Task 1) |
| `experiments/02-multi-app-pr.md` | 실험 2 기록 (Task 2) |
| `experiments/03-independent-deploy.md` | 실험 3 기록 (Task 3) |
| `experiments/04-security-patch.md` | 실험 4 기록 (Task 4) |

### demo-a-contract (실험 2, 3, 4)

| 파일 | 변경 |
|---|---|
| `libs/domain/src/main/kotlin/io/github/khkim6040/contract/domain/Contract.kt` | `beneficiary` 필드 + `changeBeneficiary()` |
| `libs/domain/src/main/kotlin/io/github/khkim6040/contract/domain/ContractEvent.kt` | `BENEFICIARY_CHANGED` + `beneficiary` 필드 |
| `libs/domain/src/main/kotlin/io/github/khkim6040/contract/domain/SampleContracts.kt` | 샘플에 수익자 |
| `libs/domain/src/test/kotlin/io/github/khkim6040/contract/domain/ContractTest.kt` | 헬퍼 수정 + 테스트 2개 |
| `apps/api/src/main/kotlin/io/github/khkim6040/contract/api/ContractController.kt` | 요청 DTO에 `beneficiary`(실험 2), `QuoteResponse.rate`(실험 3) |
| `apps/api/src/test/kotlin/io/github/khkim6040/contract/api/ApiApplicationTest.kt` | 본문·단언 수정 |
| `apps/consumer/src/main/kotlin/io/github/khkim6040/contract/consumer/ContractEventHandler.kt` | 새 이벤트 처리 |
| `apps/consumer/src/test/kotlin/io/github/khkim6040/contract/consumer/ConsumerApplicationTest.kt` | 테스트 1개 추가 |
| `deploy/overlays/dev/kustomization.yaml` | api `newTag` 1.1.0 → revert (실험 3) |

### demo-b-contract, demo-c-contract (실험 3, 4)

`apps/api/.../ContractController.kt`, `apps/api/.../ApiApplicationTest.kt`, `deploy/overlays/dev/kustomization.yaml`, `gradle.properties`(`platformVersion`).

### 플랫폼 레포 (실험 4)

| 레포 | 파일 |
|---|---|
| `demo-a-platform` | `gradle/libs.versions.toml`, `build-logic/src/main/kotlin/platform.kotlin-library.gradle.kts` |
| `demo-b-platform`, `demo-c-platform` | `gradle/libs.versions.toml`, `platform-bom/build.gradle.kts` |

---

### Task 1: 00-baseline.md

**Files:**
- Create: `insurance-platform-poc/experiments/00-baseline.md`

- [x] **Step 1: 부품 수 집계**

```bash
cd /Users/gwanhokim/personal-projects/insurance-poc
export JAVA_HOME=$(/usr/libexec/java_home -v 25)
for r in demo-a-platform demo-b-platform demo-b-template demo-c-platform; do
  cd /Users/gwanhokim/personal-projects/insurance-poc/$r
  echo "== $r $(git rev-parse --short HEAD) commits=$(git rev-list --count HEAD)"
  echo "gradle_modules=$(./gradlew projects --console=plain -q 2>/dev/null | grep -c "Project ':")"
  echo "convention_plugins=$(ls build-logic/src/main/kotlin/*.gradle.kts 2>/dev/null | wc -l | tr -d ' ')"
  echo "workflows=$(ls .github/workflows | wc -l | tr -d ' ') -> $(ls .github/workflows | tr '\n' ' ')"
  echo "scripts=$(ls tools 2>/dev/null | wc -l | tr -d ' ') dockerfile=$(ls Dockerfile 2>/dev/null | wc -l | tr -d ' ')"
  echo "kustomize_files=$(find deploy -name '*.yaml' 2>/dev/null | wc -l | tr -d ' ')"
  echo "kt_platform=$(find . -name '*.kt' -not -path '*/build/*' -not -path './templates/*' | xargs wc -l | tail -1 | awk '{print $1}') files=$(find . -name '*.kt' -not -path '*/build/*' -not -path './templates/*' | wc -l | tr -d ' ')"
  [ -d templates ] && echo "kt_template=$(find templates -name '*.kt' | xargs wc -l | tail -1 | awk '{print $1}') template_files_total=$(git ls-files templates | wc -l | tr -d ' ') script_lines=$(wc -l < tools/create-project.sh | tr -d ' ')"
  echo "tracked_files=$(git ls-files | wc -l | tr -d ' ')"
done
gh api "/user/packages?package_type=maven" --jq '.[] | "\(.repository.name) \(.name) v=\(.version_count)"'
```
Expected: 네 레포의 숫자. 참고치(Phase 1 기록): A 모듈 6, 컨벤션 2, 워크플로 2, Kustomize 11, `.kt` 30파일 786줄. B 플랫폼 모듈 3, 템플릿 모듈 5. C 플랫폼 모듈 3 + 템플릿 5 + 스크립트 1.

- [x] **Step 2: 파일 작성**

`experiments/00-baseline.md`. `<n>`은 Step 1의 값으로 채운다.

```markdown
# 00. Baseline: Phase 4 완료 시점의 플랫폼 부품 수와 구조적 속성

기록 시점: 2026-10-24, `demo-a-platform` `95d383a`, `demo-b-platform` `v1.0.0`(`61f4281`) + `demo-b-template` `50e4394`, `demo-c-platform` `v1.0.0`(`4d80703`).

## 움직이는 부품 수

| 항목 | A | B | C |
|---|---|---|---|
| 플랫폼 레포 수 | 1 | 2 (platform + template) | 1 |
| 퍼블리시 아티팩트 | 0 | 3 Maven (`io.github.khkim6040.platform:*`) + reusable workflow 1 | 3 Maven (`io.github.khkim6040.cplatform:*`) + reusable workflow 1 |
| Gradle 모듈 (플랫폼 레포) | <n> | <n> (+ 템플릿 <n>) | <n> (+ 템플릿 <n>) |
| 컨벤션 플러그인 | 2 | 2 (템플릿에 복사본) | 2 (템플릿에 복사본) |
| 워크플로 | <n> (`ci`, `release`) | <n> (`ci`, `publish`, `release-app`) + 템플릿 2 | <n> + 템플릿 2 |
| 스크립트 | 0 | 0 | 1 (`create-project.sh`, <n>줄) |
| Dockerfile | 1 | 1 (플랫폼 레포, 릴리스 시 checkout) | 1 (같음) |
| Kustomize 파일 | <n> | 템플릿 <n> | 템플릿 <n> |
| Kotlin 코드 (플랫폼 레포) | <n>파일 <n>줄 (스타터 + 샘플 앱 + 도메인) | <n>파일 <n>줄 (스타터만) + 템플릿 <n>줄 | <n>파일 <n>줄 + 템플릿 <n>줄 |
| 추적 파일 수 | <n> | <n> + <n> | <n> |
| 비즈니스 레포가 올리는 플랫폼 버전 숫자 | 0 (git ref: `upstream/main` 또는 태그 머지) | 2 (`platformVersion`, `release.yml` `@v`) | 2 (같음) |

## 구조적 속성

| 속성 | A | B | C |
|---|---|---|---|
| 프로젝트의 적용 시점 선택 | 가능. 머지 시점을 프로젝트가 정함 | 가능. 숫자를 올릴 때 | 가능. 같음 |
| 프로젝트의 적용 범위 선택 | 불가에 가까움. 머지는 마지막 머지 이후 upstream 변경 전부(cherry-pick은 규약 밖) | 부분 가능. 아티팩트 세트(`platformVersion`)와 릴리스 워크플로(`@v`)를 따로 올릴 수 있음. 아티팩트 세트 안은 전부 | 같음 |
| 구조적 대기 단계 (플랫폼 변경 → 프로젝트 적용 가능까지) | 0. upstream 커밋 즉시 fetch 가능 | 1. `publish` 워크플로 완료까지(태그 → GitHub Packages) | 1. 같음 |
| 플랫폼이 프로젝트 코드에 닿는 범위 | upstream 소유 파일 전부가 머지로 들어옴. 규약 위반 시 충돌 | 아티팩트·워크플로만. 컨벤션 플러그인·deploy·앱 빌드 파일은 생성 후 프로젝트 소유 | 같음 |
| 템플릿 전달 방식 | clone (이력·태그 포함) | GitHub Template (이력 없음, 치환 수동) | 스크립트 (이력 없음, 치환 자동, 생성 원본 SHA 기록) |
| 생성 전제 (개발자당 1회) | 없음 | GitHub Packages 토큰 | 토큰 + 플랫폼 레포 clone |
| 템플릿 검증 | 플랫폼 CI가 곧 템플릿 CI | 템플릿 레포 CI | 없음 (퍼블리시 전 빌드 불가). 생성 후 첫 빌드 |
| 네임스페이스 제약 | 없음 | GitHub Packages는 계정 단위. 플랫폼 레포가 둘이면 Group ID 분리 필요 (Phase 4에서 `cplatform`으로 분리) | 같음 |

## 집계 명령

<Step 1 명령 블록 그대로>
```

- [x] **Step 3: 커밋**

```bash
cd /Users/gwanhokim/personal-projects/insurance-poc/insurance-platform-poc
git add experiments/00-baseline.md
git commit -q -m "Record baseline platform part counts"
```

---

### Task 2: 실험 2 — 다중 앱 PR (demo-a-contract, 한 번)

**Files:**
- Modify (demo-a-contract): `Contract.kt`, `ContractEvent.kt`, `SampleContracts.kt`, `ContractTest.kt`, `ContractController.kt`, `ApiApplicationTest.kt`, `ContractEventHandler.kt`, `ConsumerApplicationTest.kt` (8파일, 3모듈)
- Create: `insurance-platform-poc/experiments/02-multi-app-pr.md`

**Interfaces:**
- Produces: `Contract(id, holderName, beneficiary, insuredAmount, startDate, endDate, status)`, `Contract.changeBeneficiary(newBeneficiary: String): Contract`, `ContractEventType.BENEFICIARY_CHANGED`, `ContractEvent(eventId, contractId, type, beneficiary: String? = null)`. 실험 3의 api 변경은 이 위에서 이루어진다

- [x] **Step 1: 브랜치와 실패하는 테스트**

```bash
cd /Users/gwanhokim/personal-projects/insurance-poc/demo-a-contract
git checkout -q -b beneficiary
```

`libs/domain/src/test/kotlin/io/github/khkim6040/contract/domain/ContractTest.kt`에서 헬퍼를 바꾸고 테스트 두 개를 추가한다:

```kotlin
    private fun contract(end: LocalDate = today.plusYears(1), amount: Long = 10_000_000, beneficiary: String = "Park") =
        Contract("C-1", "Kim", beneficiary, amount, today.minusDays(30), end)

    @Test
    fun `rejects blank beneficiary`() {
        assertFailsWith<IllegalArgumentException> { contract(beneficiary = " ") }
    }

    @Test
    fun `changes beneficiary`() {
        assertEquals("Choi", contract().changeBeneficiary("Choi").beneficiary)
        assertFailsWith<IllegalArgumentException> { contract().changeBeneficiary("") }
    }
```

`apps/consumer/src/test/kotlin/io/github/khkim6040/contract/consumer/ConsumerApplicationTest.kt`에 추가:

```kotlin
    @Test
    fun `updates beneficiary from event`() {
        val event = ContractEvent("test-3", "C-1001", ContractEventType.BENEFICIARY_CHANGED, beneficiary = "Choi")
        assertThat(handler.handle(event)).isEqualTo(HandleResult.PROCESSED)
        assertThat(repository.findById("C-1001").beneficiary).isEqualTo("Choi")
    }
```

`apps/api/src/test/kotlin/io/github/khkim6040/contract/api/ApiApplicationTest.kt`: `validBody`를 바꾸고 읽기 테스트에 단언 한 줄 추가:

```kotlin
    private val validBody = """
        {"holderName":"Kim","beneficiary":"Park","insuredAmount":10000000,"startDate":"2026-01-01","endDate":"2027-01-01"}
    """.trimIndent()
```
```kotlin
        assertThat(read).bodyJson().extractingPath("$.beneficiary").isEqualTo("Park")
```

- [x] **Step 2: 실패 확인**

```bash
cd /Users/gwanhokim/personal-projects/insurance-poc/demo-a-contract
export JAVA_HOME=$(/usr/libexec/java_home -v 25)
./gradlew :libs:domain:compileTestKotlin --console=plain -q 2>&1 | grep -E 'error:|BUILD' | head -3
```
Expected: `e: ... Too many arguments` 또는 `Unresolved reference 'changeBeneficiary'` 류의 컴파일 오류, `BUILD FAILED`.

- [x] **Step 3: 구현**

`Contract.kt` 전체:

```kotlin
package io.github.khkim6040.contract.domain

import java.time.LocalDate

enum class ContractStatus { ACTIVE, SUSPENDED, EXPIRED }

data class Contract(
    val id: String,
    val holderName: String,
    val beneficiary: String,
    val insuredAmount: Long,
    val startDate: LocalDate,
    val endDate: LocalDate,
    val status: ContractStatus = ContractStatus.ACTIVE,
) {
    init {
        require(holderName.isNotBlank()) { "holderName must not be blank" }
        require(beneficiary.isNotBlank()) { "beneficiary must not be blank" }
        require(insuredAmount > 0) { "insuredAmount must be positive" }
        require(endDate.isAfter(startDate)) { "endDate must be after startDate" }
    }

    fun suspend(): Contract {
        check(status == ContractStatus.ACTIVE) { "contract $id is $status, only ACTIVE can be suspended" }
        return copy(status = ContractStatus.SUSPENDED)
    }

    fun changeBeneficiary(newBeneficiary: String): Contract = copy(beneficiary = newBeneficiary)

    fun expireIfDue(today: LocalDate): Contract =
        if (status != ContractStatus.EXPIRED && !endDate.isAfter(today)) copy(status = ContractStatus.EXPIRED) else this
}
```

`ContractEvent.kt` 전체:

```kotlin
package io.github.khkim6040.contract.domain

enum class ContractEventType { CREATED, SUSPENDED, EXPIRED, BENEFICIARY_CHANGED }

data class ContractEvent(
    val eventId: String,
    val contractId: String,
    val type: ContractEventType,
    val beneficiary: String? = null,
)
```

`SampleContracts.kt`의 두 줄:

```kotlin
            Contract("C-1001", "Kim Gwanho", "Kim Jiho", 50_000_000, today.minusMonths(6), today.plusYears(1)),
            Contract("C-1002", "Lee Minji", "Lee Seojun", 20_000_000, today.minusYears(1), today.minusDays(1)),
```

`ContractController.kt`: 요청 DTO와 생성 호출에 한 줄씩:

```kotlin
data class CreateContractRequest(
    val holderName: String,
    val beneficiary: String,
    val insuredAmount: Long,
    val startDate: LocalDate,
    val endDate: LocalDate,
)
```
```kotlin
                holderName = request.holderName,
                beneficiary = request.beneficiary,
```

`ContractEventHandler.kt`의 `process`에 분기 한 줄:

```kotlin
            ContractEventType.BENEFICIARY_CHANGED ->
                repository.save(repository.findById(event.contractId).changeBeneficiary(requireNotNull(event.beneficiary)))
```

- [x] **Step 4: 전체 빌드**

```bash
cd /Users/gwanhokim/personal-projects/insurance-poc/demo-a-contract
export JAVA_HOME=$(/usr/libexec/java_home -v 25)
./gradlew build --console=plain 2>&1 | grep -E 'BUILD|FAILED'
grep -ho 'tests="[0-9]*"' */*/build/test-results/test/*.xml | grep -o '[0-9]*' | paste -sd+ - | bc
git status --short | wc -l
```
Expected: `BUILD SUCCESSFUL`, 테스트 `28`(25 + domain 2 + consumer 1), 변경 파일 `8`.

- [x] **Step 5: PR 생성·CI·머지**

```bash
cd /Users/gwanhokim/personal-projects/insurance-poc/demo-a-contract
R=khkim6040/demo-a-contract
git add -A
git commit -q -m "Add beneficiary to Contract and propagate to api and consumer"
git push -q -u origin beneficiary
gh pr create -R $R --fill 2>&1 | tail -1
gh pr checks -R $R beneficiary --watch 2>&1 | tail -3
gh pr view -R $R beneficiary --json number,url,changedFiles,additions,deletions --jq '"pr #\(.number) \(.url) files=\(.changedFiles) +\(.additions) -\(.deletions)"'
gh pr merge -R $R beneficiary --merge --delete-branch 2>&1 | tail -1
git checkout -q main && git pull -q
git log --oneline | head -2
```
Expected: CI 체크 `pass`, `files=8`, 머지 커밋이 main에.

- [x] **Step 6: 기록**

`experiments/02-multi-app-pr.md`:

```markdown
# 실험 2: 다중 앱 PR

## 시나리오와 성공 기준

`Contract`에 `beneficiary`를 추가하고 api(요청 DTO·응답)와 consumer(`BENEFICIARY_CHANGED` 이벤트 처리)에 반영한다. PR 하나로 영향 모듈 테스트가 통과하면 성공. 다중 레포였다면 필요한 PR 수와 대조한다. 플랫폼 무관이므로 `demo-a-contract`에서 한 번만 수행했다.

## 결과

| 항목 | A (수행) | B | C |
|---|---|---|---|
| 플랫폼 측 수동 단계 수 (목록) | 0 | 동일 (플랫폼 무관) | 동일 |
| 프로젝트 측 수동 단계 수, 프로젝트 1개당 (목록) | 1 PR: 브랜치 → 8파일 수정(libs/domain 4, apps/api 2, apps/consumer 2) → push → CI → 머지. 다중 레포 환산: domain 라이브러리 PR + 퍼블리시 대기 + api PR + consumer PR = PR 3개, 대기 1회 | 동일 | 동일 |
| 머지 충돌 파일 수 | 0 | | |
| 의미적 충돌 (빌드·테스트 실패, 동작 변화) | 없음. `build` 통과, 테스트 28개(+3). 생성자 시그니처 변경이 컴파일 시점에 모든 호출처(SampleContracts, 테스트, api)를 드러냄 — 다중 레포라면 소비 측이 라이브러리 버전을 올리는 시점에야 드러남 | | |
| 함께 끌려온 무관한 변경 수 | 0 | | |
| 검증 방법과 결과 | PR CI(`./gradlew build` + kustomize) 녹색. `gh pr view`: files=8 | | |

## 근거: 커밋 SHA, PR, CI 실행 링크

- PR: <url>, 머지 커밋 `<sha>`, CI <run url>

## 관찰: 잘못하기 쉬운 지점, 자동화할 수 있는 단계

- 모노레포의 이점은 "컴파일러가 영향 범위를 즉시 보여 준다"는 것이고, 비용은 "한 PR의 리뷰 범위가 3모듈"이라는 것. 이 실험은 A/B/C 어디서 해도 같다(비즈니스 레포 내부 변경).
- 세 contract 중 A만 이 변경을 가진 상태로 실험 3·4로 넘어간다. 실험 4의 A안 upstream 머지가 프로젝트 소유 파일 변경과 충돌하지 않는지 확인하는 부수 효과가 있다.
```

```bash
cd /Users/gwanhokim/personal-projects/insurance-poc/insurance-platform-poc
git add experiments/02-multi-app-pr.md
git commit -q -m "Record experiment 2 multi-app PR"
```

---

### Task 3: 실험 3 — 독립 배포 (A/B/C)

**Files:**
- Modify (세 contract 각각): `apps/api/src/main/kotlin/io/github/khkim6040/contract/api/ContractController.kt`, `apps/api/src/test/kotlin/io/github/khkim6040/contract/api/ApiApplicationTest.kt`, `deploy/overlays/dev/kustomization.yaml`
- Create: `insurance-platform-poc/experiments/03-independent-deploy.md`

**Interfaces:**
- Consumes: 세 contract의 `QuoteResponse(contractId, monthlyPremium, quotedPremium)`
- Produces: `QuoteResponse(..., rate: Double)`; 세 contract에 태그 `api-v1.1.0`, 이미지 `ghcr.io/khkim6040/demo-<x>-contract/api:1.1.0`; overlay는 revert되어 `0.1.0`

- [x] **Step 1: api 변경 (세 레포 동일)**

각 레포에서 `ContractController.kt`의 두 줄:

```kotlin
data class QuoteResponse(val contractId: String, val monthlyPremium: Long, val quotedPremium: Long, val rate: Double)
```
```kotlin
        return QuoteResponse(contract.id, premium, (premium * rate).toLong(), rate)
```

`ApiApplicationTest.kt`의 quote 테스트 끝에 한 줄:

```kotlin
        assertThat(quote).bodyJson().extractingPath("$.rate").isEqualTo(1.5)
```

```bash
export JAVA_HOME=$(/usr/libexec/java_home -v 25)
for x in a b c; do
  cd /Users/gwanhokim/personal-projects/insurance-poc/demo-$x-contract
  perl -pi -e 's/val quotedPremium: Long\)/val quotedPremium: Long, val rate: Double)/' apps/api/src/main/kotlin/io/github/khkim6040/contract/api/ContractController.kt
  perl -pi -e 's/\(premium \* rate\)\.toLong\(\)\)/(premium * rate).toLong(), rate)/' apps/api/src/main/kotlin/io/github/khkim6040/contract/api/ContractController.kt
  perl -pi -e 's/(extractingPath\("\$\.quotedPremium"\)\.isEqualTo\(15000\))/$1\n        assertThat(quote).bodyJson().extractingPath("\$.rate").isEqualTo(1.5)/' apps/api/src/test/kotlin/io/github/khkim6040/contract/api/ApiApplicationTest.kt
  echo "== $x $(git status --short | wc -l | tr -d ' ') files"
  ./gradlew :apps:api:test --console=plain -q 2>&1 | grep -E 'FAILED|error' ; echo "api test exit=$?"
  git commit -qam "Return rate in quote response" && git push -q origin main
done
```
Expected: 각 레포 `2 files`, `api test exit=1`(실패 없음), push 성공. (`perl` 치환 뒤 `git diff`로 두 파일이 바뀌었는지 눈으로 확인한다.)

- [x] **Step 2: 매니페스트 올리고 태그 (세 레포)**

```bash
for x in a b c; do
  cd /Users/gwanhokim/personal-projects/insurance-poc/demo-$x-contract
  perl -0pi -e 's/(api\n(?:    newName: [^\n]+\n)?    newTag: )0\.1\.0/${1}1.1.0/' deploy/overlays/dev/kustomization.yaml
  kubectl kustomize deploy/overlays/dev | grep 'image:' | sort
  git commit -qam "Deploy api 1.1.0" && git push -q origin main
  git tag api-v1.1.0 && git push -q origin api-v1.1.0
done
```
Expected: 각 레포에서 `image:` 네 줄 중 api만 `:1.1.0`, 나머지 `:0.1.0`.

- [x] **Step 3: CI가 api만 빌드했는지 확인**

```bash
sleep 20
for x in a b c; do
  R=khkim6040/demo-$x-contract
  RUN=$(gh run list -R $R --workflow release --limit 1 --json databaseId --jq '.[0].databaseId')
  gh run watch -R $R --exit-status "$RUN" >/dev/null 2>&1
  gh run view -R $R "$RUN" --json status,conclusion,url --jq '"'$x' release: \(.status) \(.conclusion) \(.url)"'
  echo "  bootJar tasks: $(gh run view -R $R "$RUN" --log 2>/dev/null | grep -oE 'Task :apps:[a-z]+:bootJar' | sort -u | tr '\n' ' ')"
  for app in api admin; do docker manifest inspect ghcr.io/$R/$app:1.1.0 >/dev/null 2>&1 && echo "  $app:1.1.0 EXISTS" || echo "  $app:1.1.0 absent"; done
done
```
Expected: 세 안 모두 `completed success`, bootJar는 `:apps:api:bootJar` 하나, `api:1.1.0 EXISTS`, `admin:1.1.0 absent`. B/C는 reusable 워크플로(`demo-b-platform@v1.0.0` / `demo-c-platform@v1.0.0`) 경로, A는 레포 내 워크플로 경로.

- [x] **Step 4: 롤백 (매니페스트 revert)**

```bash
for x in a b c; do
  cd /Users/gwanhokim/personal-projects/insurance-poc/demo-$x-contract
  git revert --no-edit HEAD >/dev/null && git push -q origin main
  echo "== $x $(git log --oneline -1)"
  kubectl kustomize deploy/overlays/dev | grep 'image:' | grep -c ':0.1.0'
done
sleep 10
for x in a b c; do
  R=khkim6040/demo-$x-contract
  RUN=$(gh run list -R $R --workflow ci --limit 1 --json databaseId --jq '.[0].databaseId')
  gh run watch -R $R --exit-status "$RUN" >/dev/null 2>&1
  gh run view -R $R "$RUN" --json status,conclusion,url --jq '"'$x' ci after revert: \(.status) \(.conclusion) \(.url)"'
  echo "  release runs total: $(gh run list -R $R --workflow release --json databaseId --jq 'length')"
done
```
Expected: 각 레포 `Revert "Deploy api 1.1.0"`, `:0.1.0` 네 줄(`4`), CI 성공, release 실행 수는 그대로 `2`(revert는 이미지를 만들지 않음). 이미지 `api:1.1.0`과 태그는 남는다.

- [x] **Step 5: 기록**

`experiments/03-independent-deploy.md`:

```markdown
# 실험 3: 독립 배포

## 시나리오와 성공 기준

api만 수정(`QuoteResponse.rate`), `deploy/overlays/dev`의 api 이미지 태그를 1.1.0으로 올리고 `api-v1.1.0` 태그를 push한다. 성공 기준: CI가 api 이미지만 빌드·푸시하고(admin 등은 안 만들어짐), 매니페스트 커밋 revert만으로 롤백된다(CI는 레포에 커밋을 쓰지 않음).

## 결과

| 항목 | A | B | C |
|---|---|---|---|
| 플랫폼 측 수동 단계 수 (목록) | 0 | 0 | 0 |
| 프로젝트 측 수동 단계 수, 프로젝트 1개당 (목록) | 3: ① api 코드 커밋(2파일) ② overlay `newTag` 커밋(1파일) + 태그 push ③ 롤백 = revert 커밋 | 3: 같음 | 3: 같음 |
| 머지 충돌 파일 수 | 0 | 0 | 0 |
| 의미적 충돌 (빌드·테스트 실패, 동작 변화) | 없음 | 없음 | 없음 |
| 함께 끌려온 무관한 변경 수 | 0 | 0 | 0 |
| 검증 방법과 결과 | release 로그에 `:apps:api:bootJar`만, `api:1.1.0` 존재·`admin:1.1.0` 부재, revert 후 kustomize 렌더 전부 `0.1.0`, release 실행 수 불변 | 같음 (reusable `release-app.yml@v1.0.0` 경로) | 같음 (`demo-c-platform@v1.0.0` 경로) |

## 근거: 커밋 SHA, PR, CI 실행 링크

- A: 코드 `<sha>`, 매니페스트 `<sha>`, revert `<sha>`, release <url>, ci <url>
- B: ...
- C: ...

## 관찰: 잘못하기 쉬운 지점, 자동화할 수 있는 단계

- 세 안의 차이는 릴리스 단계가 어디 있느냐(A 레포 안, B/C 플랫폼 reusable)뿐이고, 프로젝트 측 절차와 결과는 같다. 독립 배포는 태그 규칙 `<app>-v<ver>` + `:apps:<app>:bootJar`라는 Phase 1 설계가 결정하며 플랫폼 구조와 무관하다.
- 롤백은 매니페스트 revert이고 이미지·태그는 남는다. 같은 버전을 다시 태그하면 release가 다시 돌아 이미지를 덮어쓴다(태그 재사용 금지 규칙이 필요).
- `newTag`를 올릴 때 다른 앱 항목을 잘못 건드리기 쉽다. 네 앱의 `newTag`가 한 파일에 있어 diff 리뷰로 잡는다.
- (실행 중 드러난 점을 추가한다)
```

```bash
cd /Users/gwanhokim/personal-projects/insurance-poc/insurance-platform-poc
git add experiments/03-independent-deploy.md
git commit -q -m "Record experiment 3 independent deploy"
```

---

### Task 4: 실험 4 — 보안 패치 Jackson 3.1.8 (A/B/C)

**Files:**
- Modify (demo-a-platform): `gradle/libs.versions.toml`, `build-logic/src/main/kotlin/platform.kotlin-library.gradle.kts`
- Modify (demo-b-platform, demo-c-platform): `gradle/libs.versions.toml`, `platform-bom/build.gradle.kts`
- Modify (demo-b-contract, demo-c-contract): `gradle.properties`
- Modify (demo-a-contract): upstream 머지 (파일 변경 없음, 머지 커밋)
- Create: `insurance-platform-poc/experiments/04-security-patch.md`

**Interfaces:**
- Produces: 카탈로그 별칭 `libs.jackson.bom` = `tools.jackson:jackson-bom:3.1.8`; 플랫폼 태그 `v1.1.0`(A/B/C); B/C 아티팩트 `1.1.0`

- [x] **Step 1: 현재 버전 확인 (세 contract)**

```bash
export JAVA_HOME=$(/usr/libexec/java_home -v 25)
for x in a b c; do
  cd /Users/gwanhokim/personal-projects/insurance-poc/demo-$x-contract
  echo "== $x"
  for app in api admin consumer batch; do
    echo "  $app: $(./gradlew :apps:$app:dependencies --configuration runtimeClasspath --console=plain -q | grep -oE 'jackson-(core|databind|module-kotlin):[0-9.]+( -> [0-9.]+)?' | sort -u | tr '\n' ' ')"
  done
done
```
Expected: api·admin `jackson-core:3.1.7 jackson-databind:3.1.7 jackson-module-kotlin:3.1.7`. consumer·batch는 Jackson이 없거나(빈 줄) 3.1.7. 이 결과를 기록의 "변경 전"으로 적는다.

- [x] **Step 2: A 플랫폼 PR**

`demo-a-platform/gradle/libs.versions.toml`에 추가:

```toml
# [versions]
jackson = "3.1.8"
# [libraries]
jackson-bom = { module = "tools.jackson:jackson-bom", version.ref = "jackson" }
```

`build-logic/src/main/kotlin/platform.kotlin-library.gradle.kts`의 `dependencies`에 한 줄:

```kotlin
    implementation(platform(libs.spring.boot.bom))
    implementation(platform(libs.jackson.bom)) // security patch: overrides Boot's 3.1.7
```

```bash
cd /Users/gwanhokim/personal-projects/insurance-poc/demo-a-platform
export JAVA_HOME=$(/usr/libexec/java_home -v 25)
R=khkim6040/demo-a-platform
git checkout -q -b jackson-3.1.8
perl -pi -e 's/^spring-boot = "4.1.2"$/spring-boot = "4.1.2"\njackson = "3.1.8"/' gradle/libs.versions.toml
perl -pi -e 's/^(spring-boot-bom = .*)$/$1\njackson-bom = { module = "tools.jackson:jackson-bom", version.ref = "jackson" }/' gradle/libs.versions.toml
perl -pi -e 's/^(    implementation\(platform\(libs\.spring\.boot\.bom\)\))$/$1\n    implementation(platform(libs.jackson.bom)) \/\/ security patch: overrides Boot'"'"'s 3.1.7/' build-logic/src/main/kotlin/platform.kotlin-library.gradle.kts
git diff --stat
./gradlew :apps:api:dependencies --configuration runtimeClasspath --console=plain -q | grep -oE 'jackson-(core|databind|module-kotlin):[0-9.]+( -> [0-9.]+)?' | sort -u
./gradlew build --console=plain 2>&1 | grep -E 'BUILD|FAILED'
git commit -qam "Force Jackson 3.1.8 via jackson-bom"
git push -q -u origin jackson-3.1.8
gh pr create -R $R --fill 2>&1 | tail -1
gh pr checks -R $R jackson-3.1.8 --watch 2>&1 | tail -2
gh pr merge -R $R jackson-3.1.8 --merge --delete-branch 2>&1 | tail -1
git checkout -q main && git pull -q
git tag v1.1.0 && git push -q origin v1.1.0
git log --oneline -1
```
Expected: 2파일 변경, 로컬에서 `3.1.7 -> 3.1.8` 세 줄, `BUILD SUCCESSFUL`, PR CI pass, 머지, 태그.

- [x] **Step 3: B·C 플랫폼 PR과 v1.1.0 퍼블리시**

각 플랫폼의 `gradle/libs.versions.toml`에 A와 같은 두 줄, `platform-bom/build.gradle.kts`에:

```kotlin
    api(platform(libs.spring.boot.bom))
    api(platform(libs.jackson.bom)) // security patch: overrides Boot's 3.1.7
```

```bash
export JAVA_HOME=$(/usr/libexec/java_home -v 25)
for x in b c; do
  cd /Users/gwanhokim/personal-projects/insurance-poc/demo-$x-platform
  R=khkim6040/demo-$x-platform
  git checkout -q -b jackson-3.1.8
  perl -pi -e 's/^spring-boot = "4.1.2"$/spring-boot = "4.1.2"\njackson = "3.1.8"/' gradle/libs.versions.toml
  perl -pi -e 's/^(spring-boot-bom = .*)$/$1\njackson-bom = { module = "tools.jackson:jackson-bom", version.ref = "jackson" }/' gradle/libs.versions.toml
  perl -pi -e 's/^(    api\(platform\(libs\.spring\.boot\.bom\)\))$/$1\n    api(platform(libs.jackson.bom)) \/\/ security patch: overrides Boot'"'"'s 3.1.7/' platform-bom/build.gradle.kts
  git diff --stat
  ./gradlew build publishToMavenLocal -PplatformVersion=0.0.0-LOCAL --console=plain 2>&1 | grep -E 'BUILD|FAILED'
  grep -c 'jackson-bom' ~/.m2/repository/io/github/khkim6040/*platform/platform-bom/0.0.0-LOCAL/platform-bom-0.0.0-LOCAL.pom
  git commit -qam "Force Jackson 3.1.8 via jackson-bom"
  git push -q -u origin jackson-3.1.8
  gh pr create -R $R --fill 2>&1 | tail -1
  gh pr checks -R $R jackson-3.1.8 --watch 2>&1 | tail -2
  gh pr merge -R $R jackson-3.1.8 --merge --delete-branch 2>&1 | tail -1
  git checkout -q main && git pull -q
  git tag v1.1.0 && git push -q origin v1.1.0
done
sleep 20
for x in b c; do
  R=khkim6040/demo-$x-platform
  RUN=$(gh run list -R $R --workflow publish --limit 1 --json databaseId --jq '.[0].databaseId')
  gh run watch -R $R --exit-status "$RUN" >/dev/null 2>&1
  gh run view -R $R "$RUN" --json status,conclusion,url --jq '"'$x' publish: \(.status) \(.conclusion) \(.url)"'
done
G_b=platform; G_c=cplatform
for x in b c; do eval g=\$G_$x; curl -sL -o /dev/null -w "$x bom 1.1.0: %{http_code}\n" -u "khkim6040:$(gh auth token)" "https://maven.pkg.github.com/khkim6040/demo-$x-platform/io/github/khkim6040/$g/platform-bom/1.1.0/platform-bom-1.1.0.pom"; done
```
Expected: 각 2파일, `BUILD SUCCESSFUL`, 로컬 BOM pom에 `jackson-bom` 1회 이상, PR pass·머지·태그, publish `completed success` 둘, `200` 둘. (B·C 플랫폼 레포 `~/.m2`의 그룹 디렉터리는 B `platform`, C `cplatform`이므로 glob `*platform`으로 둘을 잡는다.)

- [x] **Step 4: A contract — upstream 머지 PR**

```bash
cd /Users/gwanhokim/personal-projects/insurance-poc/demo-a-contract
export JAVA_HOME=$(/usr/libexec/java_home -v 25)
R=khkim6040/demo-a-contract
git fetch -q upstream
git log --oneline main..upstream/main
git checkout -q -b platform-jackson-3.1.8
git merge --no-edit upstream/main 2>&1 | tail -2
echo "conflicts=$(git diff --name-only --diff-filter=U | wc -l | tr -d ' ')"
git show --stat HEAD | grep -E 'files? changed'
./gradlew build --console=plain 2>&1 | grep -E 'BUILD|FAILED'
git push -q -u origin platform-jackson-3.1.8
gh pr create -R $R --title "Merge platform v1.1.0 (Jackson 3.1.8)" --body "upstream/main @ v1.1.0" 2>&1 | tail -1
gh pr checks -R $R platform-jackson-3.1.8 --watch 2>&1 | tail -2
gh pr merge -R $R platform-jackson-3.1.8 --merge --delete-branch 2>&1 | tail -1
git checkout -q main && git pull -q
```
Expected: `main..upstream/main`에 커밋 2개(jackson 커밋 + 플랫폼 PR 머지 커밋), `conflicts=0`, 머지 커밋 `2 files changed`, `BUILD SUCCESSFUL`, PR pass·머지.

- [x] **Step 5: B·C contract — platformVersion PR**

```bash
export JAVA_HOME=$(/usr/libexec/java_home -v 25)
for x in b c; do
  cd /Users/gwanhokim/personal-projects/insurance-poc/demo-$x-contract
  R=khkim6040/demo-$x-contract
  git checkout -q -b platform-1.1.0
  perl -pi -e 's/^platformVersion=1\.0\.0$/platformVersion=1.1.0/' gradle.properties
  git diff --stat
  ./gradlew build --console=plain 2>&1 | grep -E 'BUILD|FAILED'
  git commit -qam "Take platform 1.1.0 (Jackson 3.1.8)"
  git push -q -u origin platform-1.1.0
  gh pr create -R $R --fill 2>&1 | tail -1
  gh pr checks -R $R platform-1.1.0 --watch 2>&1 | tail -2
  gh pr merge -R $R platform-1.1.0 --merge --delete-branch 2>&1 | tail -1
  git checkout -q main && git pull -q
done
```
Expected: 각 1파일 1줄, `BUILD SUCCESSFUL`(새 패키지 1.1.0 다운로드), PR pass·머지.

- [x] **Step 6: 네 앱 버전 확인 (세 contract)**

```bash
export JAVA_HOME=$(/usr/libexec/java_home -v 25)
for x in a b c; do
  cd /Users/gwanhokim/personal-projects/insurance-poc/demo-$x-contract
  echo "== $x $(git log --oneline -1)"
  for app in api admin consumer batch; do
    echo "  $app: $(./gradlew :apps:$app:dependencies --configuration runtimeClasspath --console=plain -q | grep -oE 'jackson-(core|databind|module-kotlin):[0-9.]+( -> [0-9.]+)?' | sort -u | tr '\n' ' ')"
  done
  grep -n 'uses:' .github/workflows/release.yml 2>/dev/null; grep -n platformVersion gradle.properties 2>/dev/null
done
```
Expected: 세 안 모두 api·admin에 `3.1.7 -> 3.1.8` 세 줄. consumer·batch는 Step 1과 같은 모양(없으면 없음, 있으면 `-> 3.1.8`). B/C는 `platformVersion=1.1.0`인데 `release.yml`은 `@v1.0.0`(의도된 어긋남, 관찰에 적는다).

- [x] **Step 7: 기록**

`experiments/04-security-patch.md`:

```markdown
# 실험 4: 보안 패치 (전이 의존성 강제)

## 시나리오와 성공 기준

Spring Boot 4.1.2가 고정한 Jackson 3.1.7(`jackson-core`, `jackson-databind`, `jackson-module-kotlin`)을 3.1.8로 강제한다. `tools.jackson:jackson-bom:3.1.8`을 플랫폼으로 import해 세 모듈을 한 번에 올린다. 성공 기준: 세 contract의 네 앱 `runtimeClasspath`에서 Jackson이 3.1.8. 플랫폼 변경과 프로젝트 반영 모두 실제 PR.

변경 전: api·admin 3.1.7 / consumer·batch <Step 1 결과>.

## 결과

| 항목 | A | B | C |
|---|---|---|---|
| 플랫폼 측 수동 단계 수 (목록) | 3: ① `libs.versions.toml` 2줄 + 컨벤션 1줄(2파일) ② PR → CI → 머지 ③ 태그 `v1.1.0`(참조용, 트리거 없음) | 4: ① `libs.versions.toml` 2줄 + `platform-bom` 1줄(2파일) ② PR → CI → 머지 ③ 태그 `v1.1.0` ④ publish 완료 대기(구조적 대기 1) | 4: 같음 |
| 프로젝트 측 수동 단계 수, 프로젝트 1개당 (목록) | 1 PR: `fetch upstream` + `merge upstream/main` → push → CI → 머지. 손댄 파일 0(머지 커밋만) | 1 PR: `gradle.properties` 1줄 → push → CI → 머지. 손댄 파일 1 | 1 PR: 같음 |
| 머지 충돌 파일 수 | 0 (실험 2의 프로젝트 소유 변경 8파일과 upstream 소유 변경 2파일이 겹치지 않음) | 0 (머지 없음) | 0 |
| 의미적 충돌 (빌드·테스트 실패, 동작 변화) | 없음. `build` 통과 | 없음 | 없음 |
| 함께 끌려온 무관한 변경 수 | 0 (upstream 커밋 2개 = 이 패치의 커밋 + PR 머지 커밋) | 0 (`1.1.0` = 이 패치만) | 0 |
| 검증 방법과 결과 | 네 앱 `dependencies --configuration runtimeClasspath`: api·admin `3.1.7 -> 3.1.8`, consumer·batch <결과> | 같음. `platform-bom:1.1.0` pom에 `jackson-bom` import | 같음 |

## 근거: 커밋 SHA, PR, CI 실행 링크

- A 플랫폼 PR <url>, 머지 `<sha>`, 태그 `v1.1.0`=`<sha>`; contract PR <url>, 머지 `<sha>`
- B 플랫폼 PR <url>, `v1.1.0`=`<sha>`, publish <url>; contract PR <url>
- C 플랫폼 PR <url>, `v1.1.0`=`<sha>`, publish <url>; contract PR <url>

## 관찰: 잘못하기 쉬운 지점, 자동화할 수 있는 단계

- 수단은 셋 다 "BOM을 하나 더 import"이고 Gradle이 높은 버전을 택한다. 플랫폼 측 파일 수는 같다(2). 차이는 전달: A는 git 머지(대기 0, 프로젝트가 손대는 파일 0), B/C는 퍼블리시(대기 1) + 숫자 1줄.
- B/C는 `platformVersion`만 올리고 `release.yml`의 `@v`는 `v1.0.0`에 남겼다. 아티팩트와 워크플로가 다른 버전을 가리키는 상태가 정상 운영에서 생긴다. 이것이 문제가 되는지는 실험 7(워크플로 변경)에서 본다.
- A는 upstream 머지가 프로젝트 변경(실험 2·3)과 충돌하지 않았다. 소유권 규약이 지켜지는 동안 A의 전파 비용은 "머지 PR 하나"다.
- Boot가 이미 최신 패치를 고정한 라이브러리(Tomcat 11.0.27, Logback 1.5.38)는 강제할 패치가 없었다. 패치 대상을 찾는 일 자체가 플랫폼 측 작업이며, 세 안 공통.
- `dependencies` 출력의 `(c)`(constraint)와 `->`(치환) 표기를 확인하지 않으면 BOM이 적용된 줄 알고 넘어가기 쉽다.
- (실행 중 드러난 점을 추가한다)
```

```bash
cd /Users/gwanhokim/personal-projects/insurance-poc/insurance-platform-poc
git add experiments/04-security-patch.md
git commit -q -m "Record experiment 4 security patch"
```

---

### Task 5: 마무리

- [x] **Step 1: 계획 체크박스 반영, push, 작업 트리 확인**

```bash
cd /Users/gwanhokim/personal-projects/insurance-poc/insurance-platform-poc
git add docs/superpowers/plans/2026-10-24-phase5a-baseline-exp2-4.md
git commit -q -m "Mark Phase 5a plan complete"
git push -q origin main
for d in demo-a-platform demo-a-contract demo-b-platform demo-b-contract demo-c-platform demo-c-contract insurance-platform-poc; do
  echo "$d: $(git -C /Users/gwanhokim/personal-projects/insurance-poc/$d status --short | wc -l | tr -d ' ') uncommitted, branch $(git -C /Users/gwanhokim/personal-projects/insurance-poc/$d branch --show-current)"
done
```
Expected: 전부 `0 uncommitted, branch main`.

---

## 자체 점검 결과

- **스펙 커버리지**: 7.1 baseline(부품 수 + 구조적 속성, Phase 4 완료 시점) → Task 1. 7.2 실험 2(한 번, 영향 모듈 테스트, PR 수 대조, 실제 PR) → Task 2. 실험 3(api만 수정, 매니페스트, `api-v1.1.0`, api 이미지만, revert 롤백, A/B/C) → Task 3. 실험 4(전이 의존성 패치, A 카탈로그→머지, B/C BOM 퍼블리시→카탈로그 버전 한 줄, 네 앱 `dependencies` 확인, 실제 PR) → Task 4. 6.3 롤백 절차(revert, CI는 커밋 안 씀) → Task 3 Step 4. 5.4 소유권(실험 2·3은 프로젝트 소유 파일만) → Global Constraints. 실험 5~8은 Phase 5b.
- **자리표시자**: `<...>`는 실행 중 얻는 값(SHA, URL, 수치)만. 코드·명령은 전부 적혀 있다.
- **일관성**: `Contract` 생성자 인자 순서(`id, holderName, beneficiary, insuredAmount, startDate, endDate`)가 Contract.kt·SampleContracts·ContractTest 헬퍼에서 같다. `libs.jackson.bom` 별칭이 toml(`jackson-bom`)과 Gradle 접근자에서 대응한다. 브랜치 이름 `jackson-3.1.8`(플랫폼), `platform-jackson-3.1.8`(A contract), `platform-1.1.0`(B/C contract)이 생성·checks·merge 명령에서 같다.
- **알려진 위험**: ① `perl` 치환은 원문이 정확히 일치해야 한다. 각 Step의 `git diff --stat`으로 변경 파일 수를 확인하고, 0이면 손으로 고친다. ② `gh pr checks --watch`가 체크가 등록되기 전에 실행되면 즉시 끝날 수 있다. 그 경우 `sleep 10` 후 다시 실행한다. ③ B/C contract PR의 CI는 `1.1.0` 패키지가 올라간 뒤에만 통과하므로 Step 3의 publish 성공 뒤에 Step 5를 실행한다(순서 고정).
