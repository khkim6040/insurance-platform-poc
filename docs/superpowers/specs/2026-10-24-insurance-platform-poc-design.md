# Insurance Platform PoC 설계 스펙

- 작성일: 2026-10-24
- 상태: 승인 대기
- 기반 문서: "Insurance Platform — Monorepo 기반 백엔드 플랫폼 아키텍처 PoC" 청사진
- 실험 계정: GitHub `khkim6040` (전부 공개 레포)

## 1. 목적

비즈니스 프로젝트당 하나의 Monorepo(API/Admin/Consumer/Batch + 공통 도메인)를 쓰면서, 각 앱을 독립적으로 빌드·배포하고, 공통 라이브러리와 기술 설정을 중앙에서 관리하는 플랫폼 구조를 세 가지 안(A/B/C)으로 구현해 실측 비교한다.

이 PoC가 답하는 질문은 하나다. **A/B/C 중 어느 플랫폼 배포 구조가 팀의 유지보수 비용과 운영 위험을 가장 잘 줄이는가.**

## 2. 청사진 대비 변경된 결정

| 항목 | 청사진 | 결정 | 이유 |
|---|---|---|---|
| HTTP 프레임워크 | MVC/WebFlux 선택 가능, 비교 실험 | **Spring MVC 고정**. WebFlux 비교(5장, Phase 2·7, 실험 9) 삭제 | 리더 결정. WebFlux가 나중에 필요해지면 고칠 범위만 줄이는 방향으로 설계 |
| 버전 기준선 | 미정 | **Spring Boot 4.1.2, JDK 25, Kotlin, Gradle** | 신규 플랫폼의 레퍼런스 역할. 4.1은 2026-06 GA, OSS 지원 2027-06까지 |
| HTTP Client | RestClient/WebClient | **RestClient만** | MVC 고정에 따름 |
| Virtual Threads | 별도 비교 실험 | **플랫폼 기본값으로 활성화**, 비교 없음 | JDK 25에서는 pinning 문제가 없음 |
| 플랫폼 HTTP 모듈 | http-core / http-mvc / http-webflux | **`platform-http-starter` 하나**, 패키지로 중립/Servlet 분리 | 모듈 분리는 WebFlux가 생길 때 패키지를 승격하면 충분 |
| 관측성·복원력 스타터 | 구조도에만 존재 | **Phase 6(심화)에서 추가**, 실험 10의 전파 대상 | 처음부터 있으면 전파 비용을 측정할 수 없음 |
| Kafka·MongoDB | 초기 PoC 제외 가능 | **PoC 범위 밖**. Consumer는 인메모리 소스, Batch는 H2 | 구조 선택이 끝난 뒤 채택된 안에서 한 번만 만들면 됨 |
| 배포 | Docker/K8s | **이미지 빌드 + Kustomize 매니페스트 렌더링 검증까지**. 클러스터 적용 없음 | 롤백은 Kubernetes 기본 동작이라 PoC로 증명할 가치가 낮음 |
| 이미지 빌드 | 미정 | **Dockerfile** (Jib·Buildpacks 미사용) | 팀 컨벤션. CI 실행 횟수가 적어 속도 이득이 무의미 |
| 이미지 태그 | 미정 | **앱별 시맨틱 버전 git 태그 `<app>-v<semver>`** | 팀의 내부 배포 플랫폼이 커밋에 이미지 태그를 지정하는 방식 |
| GitHub Fork | Fork와 clone 차이 검증 | **`git clone` + `remote add upstream`으로 고정** | Fork 네트워크는 실험 본질과 무관하고 실무에서 해로움 |
| A안 커스터마이징 | 미정 | **플랫폼 파일 불가침 규약** + 실험 6에서 의도적 위반 1회 | 규약을 지켰을 때와 어겼을 때의 비용을 모두 측정 |
| Maven 저장소 | 미정 | **GitHub Packages** | 공개 패키지라도 토큰이 필요해 사내 Nexus와 조건이 같음 |
| 기록 위치 | 미정 | **보고서 전용 레포 `insurance-platform-poc`** | 실험 기록이 git 이력에 남아야 재현 가능 |
| 시간 측정 | 미정 | **측정하지 않음** | 에이전트 작업 시간은 노이즈이며 사람 시간으로 환산 불가 |

## 3. 레포 구성

| 레포 | 역할 | 생성 방식 |
|---|---|---|
| `insurance-platform-poc` | 스펙, 실험 기록, 최종 보고서, 부트스트랩 스크립트, 외부 API 스텁 서버 | 직접 생성 |
| `demo-a-platform` | A안 플랫폼 = 스타터를 로컬 모듈로 포함한 **완성된 모노레포**. Phase 1의 참조 구현 | 직접 생성 |
| `demo-a-contract` | A안 비즈니스 프로젝트 | `git clone` + `remote add upstream` |
| `demo-b-platform` | B안 플랫폼. BOM, 버전 카탈로그, 스타터, reusable workflow를 퍼블리시 | 직접 생성 |
| `demo-b-template` | B안 템플릿. 스타터 모듈 없이 아티팩트를 소비하는 모노레포. GitHub Template 레포 | 직접 생성 |
| `demo-b-contract` | B안 비즈니스 프로젝트 | `gh repo create --template` |
| `demo-c-platform` | C안 플랫폼 = B안 플랫폼 코드 + `templates/multi-service/` + `tools/create-project.sh` | 직접 생성 |
| `demo-c-contract` | C안 비즈니스 프로젝트 | `create-project.sh` 결과를 push |
| `demo-{a,b,c}-claims` | 실험 8용 두 번째 프로젝트 | 각 안의 생성 절차 재수행 |

- 로컬 배치: `/Users/gwanhokim/personal-projects/insurance-poc/<레포>`. 상위 폴더는 git 레포가 아니다.
- 생성 순서: `insurance-platform-poc` → `demo-a-platform`(Phase 1) → `demo-a-contract` → `demo-b-*` → `demo-c-*`.
- **한 번만 작성 원칙**: 플랫폼 라이브러리 코드와 앱 스켈레톤은 `demo-a-platform`에서 한 번 작성하고 B/C가 복사한다. 단, Phase 5 이후의 플랫폼 변경(실험 4·5·7·10)은 세 플랫폼 레포에 각각 손으로 적용한다. 이 반복은 측정 대상이므로 자동화하지 않는다.
- B와 C의 플랫폼 레포는 라이브러리 코드가 같지만 별도로 유지한다. 두 안을 독립적으로 팀에 보여 주기 위해서다.
- `tools/bootstrap-repos.sh`: `gh repo create`로 공개 레포를 만들고 clone한다. 이미 있으면 건너뛴다.

## 4. Gradle과 플랫폼 모듈

### 4.1 버전과 빌드 설정의 단일 출처

- 라이브러리·플러그인 버전은 `gradle/libs.versions.toml` 한 파일에서 나온다.
- 빌드 설정은 `build-logic` 포함 빌드의 컨벤션 플러그인 **두 개**가 담당한다.

| 플러그인 | 대상 | 역할 |
|---|---|---|
| `platform.kotlin-library` | `libs/*`, `platform/*` | Kotlin JVM, JDK 25 툴체인, 테스트 기본 의존성 |
| `platform.spring-boot-app` | `apps/*` | Spring Boot 플러그인, `kotlin-spring`, 실행 가능 jar(`app.jar`), 이미지 메타데이터(앱 이름, git sha) |

스타터 전용 설정(auto-configuration 처리기, Boot 의존성 관리)은 스타터의 빌드 파일에 직접 둔다.

### 4.2 참조 모노레포(= A안 플랫폼) 트리

```text
demo-a-platform/
├── settings.gradle.kts            # includeBuild("build-logic") + 모듈 include
├── gradle/libs.versions.toml
├── build-logic/
├── platform/
│   └── http-starter/              # Phase 1. Phase 6에서 observability-starter, resilience-starter 추가
├── libs/
│   └── domain/                    # Spring 의존 없음
├── apps/
│   ├── api/  ├── admin/  ├── consumer/  └── batch/
├── deploy/
├── Dockerfile
└── .github/workflows/
```

### 4.3 `platform-http-starter`

모듈은 하나, 패키지는 둘이다.

- `io.github.khkim6040.platform.http` (프레임워크 중립)
  - Correlation ID 헤더 이름 상수 (`X-Correlation-Id`)
  - HTTP 클라이언트 타임아웃 프로퍼티 `platform.http.client.connect-timeout`(기본 2s), `read-timeout`(기본 5s)
  - 공통 에러 응답 규약: RFC 9457 ProblemDetail에 `correlationId` 필드 추가
- `io.github.khkim6040.platform.http.servlet` (Servlet 전용)
  - Correlation ID를 요청 헤더에서 읽거나 생성해 MDC와 응답 헤더에 넣는 Filter
  - `@RestControllerAdvice` 예외 핸들러 (`IllegalArgumentException` → 400, 그 외 → 500)
  - 타임아웃 프로퍼티를 적용하는 `RestClientCustomizer`
- 등록: `META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports`. Servlet 설정 클래스에 `@ConditionalOnWebApplication(type = SERVLET)`.
- 기본 프로퍼티: `EnvironmentPostProcessor`가 스타터 안의 `platform-defaults.yml`(`spring.threads.virtual.enabled=true`, ProblemDetail 활성화)을 **최저 우선순위**로 올린다. 앱의 `application.yml`이 항상 이긴다.
- 스타터가 Boot의 MVC 스타터를 `api` 의존성으로 가져간다. 앱은 `platform-http-starter` 한 줄만 선언한다. Consumer와 Batch는 이 스타터에 의존하지 않는다.
- 실험 대상 지정: 타임아웃 프로퍼티 기본값 클래스는 실험 6의 의도적 위반 대상, Correlation Filter는 실험 5의 변경 대상.

### 4.4 B/C안 퍼블리시 아티팩트

```text
demo-b-platform/   (demo-c-platform은 여기에 templates/ + tools/ 추가)
├── platform-bom/            # java-platform. spring-boot-dependencies import + 플랫폼 스타터·추가 라이브러리 버전 고정
├── platform-catalog/        # version-catalog. libs.versions.toml을 아티팩트로 퍼블리시. 플러그인 버전과 BOM 버전 포함
├── platform-http-starter/
├── build-logic/
└── .github/workflows/
    ├── publish.yml          # v* 태그 → GitHub Packages 퍼블리시
    └── release-app.yml      # workflow_call. 비즈니스 레포가 호출하는 앱 릴리스 워크플로
```

- **BOM**은 전이 의존성까지 버전을 강제하므로 보안 패치(실험 4)의 수단이다. **카탈로그**는 Kotlin·Spring Boot 플러그인 버전을 중앙에서 정하는 유일한 수단이다. 카탈로그 안에 BOM 버전 별칭을 두어, 비즈니스 레포가 올리는 숫자는 `settings.gradle.kts`의 카탈로그 버전 **하나**가 되게 한다.
- Group ID: `io.github.khkim6040.platform`. 플랫폼 버전은 `v1.0.0` 형식의 git 태그이며 아티팩트 버전과 같다.
- 컨벤션 플러그인은 B/C안에서 템플릿에 **복사**된다. 즉 빌드 설정은 중앙 업데이트되지 않는다. Gradle 플러그인으로 퍼블리시하는 대안은 실험 7 결과를 본 뒤 판단하며 처음부터 만들지 않는다.

## 5. 비즈니스 모노레포

### 5.1 구조

A안은 플랫폼 레포 그대로, B/C안은 `platform/` 디렉터리가 빠지고 아티팩트 의존성으로 대체된 형태다.

### 5.2 앱별 책임 (Phase 1)

| 모듈 | 역할 | 실행 모델 | 검증 |
|---|---|---|---|
| `libs/domain` | `Contract`, `ContractStatus`, 보험료 계산 규칙, 만기 판정 규칙 | Spring 없음 | 단위 테스트. 네 앱이 모두 참조 |
| `api` (8080) | `POST /contracts`(도메인 규칙 검증), `GET /contracts/{id}`, `GET /contracts/{id}/quote`(외부 스텁을 RestClient로 호출) | Servlet, Virtual Threads | `X-Correlation-Id` 응답 헤더, 에러 시 ProblemDetail, 타임아웃 적용 |
| `admin` (8081) | `GET /admin/contracts`, `POST /admin/contracts/{id}/suspend` | Servlet | API와 독립 실행, 같은 도메인 참조 |
| `consumer` | `ContractEvent` 처리. 처리한 ID를 기억해 중복 제거, 실패는 N회 재시도 후 로그로 격리 | `web-application-type=none`. `@Scheduled` 가짜 소스가 이벤트를 주기 생성해 프로세스 유지 | 웹 서버 없음. 핸들러 직접 호출 테스트 |
| `batch` | `contract-expiry-job`: 계약 목록에 만기 규칙 적용, 상태 변경 기록 | Spring Batch, H2 인메모리 JobRepository, 완료 후 종료 | 종료 코드 0, `COMPLETED`, 웹 서버 없음 |

저장소는 전부 인메모리(`ConcurrentHashMap`)다.

### 5.3 테스트

- 앱마다 `@SpringBootTest` 컨텍스트 테스트 하나: api·admin은 `WebApplicationType.SERVLET`, consumer·batch는 `NONE`을 단언한다.
- 앱마다 동작 테스트 하나(api 헤더·에러 응답, consumer 중복·재시도, batch Job 결과).
- 스타터: Filter, 예외 핸들러, RestClient 타임아웃 테스트.
- `./gradlew build` 전체 실행과 `./gradlew :apps:api:test` 앱 단위 실행이 모두 된다.

### 5.4 A안 파일 소유권 규약

- **upstream 소유 (프로젝트 수정 금지)**: `platform/**`, `build-logic/**`, `gradle/**`, 루트 빌드 파일, `apps/*/build.gradle.kts`, `Dockerfile`, `.github/**`, `deploy/base/**`
- **프로젝트 소유 (생성 후 upstream이 다시 건드리지 않음)**: `apps/*/src/**`, `libs/**`, `deploy/overlays/**`, README
- 설정은 플랫폼 기본값(`platform-defaults.yml`)과 앱 `application.yml`로 분리되어 충돌하지 않는다.
- 예상되는 주된 충돌 지점은 `apps/*/build.gradle.kts`(프로젝트의 의존성 추가 vs 플랫폼의 스타터 추가)이며 실험 10에서 확인한다.
- 대가: 플랫폼이 샘플 코드를 개선해도 기존 프로젝트에 전파되지 않는다. B/C 템플릿과 같은 한계다.

### 5.5 패키지 이름

- 플랫폼: `io.github.khkim6040.platform.*`
- 샘플 앱·도메인(플랫폼 레포): `io.github.khkim6040.sample.*`
- 비즈니스 프로젝트: `io.github.khkim6040.contract.*` / `...claims.*`. B/C는 생성 시 치환, A는 clone 후 직접 변경하며 이것도 실험 1의 생성 비용에 포함한다.

## 6. CI와 배포

### 6.1 Dockerfile (루트에 하나)

```dockerfile
FROM eclipse-temurin:25-jre
ARG APP
COPY apps/${APP}/build/libs/app.jar /app.jar
ENTRYPOINT ["java", "-jar", "/app.jar"]
```

jar는 CI에서 Gradle이 먼저 만든다. 레이어 최적화는 하지 않는다.

### 6.2 비즈니스 레포 워크플로

| 워크플로 | 트리거 | 역할 |
|---|---|---|
| `ci.yml` | main push, PR | `./gradlew build`, `kubectl kustomize deploy/overlays/dev` 렌더링 검증 |
| `release.yml` | `*-v*` 태그 push | 태그에서 앱·버전 추출 → `:apps:<app>:bootJar` → `docker build --build-arg APP` → `ghcr.io/khkim6040/<repo>/<app>:<version>` 푸시, 이미지 라벨에 git sha |

- A안: `release.yml`이 레포 안에 전체 단계를 가진다. 변경은 머지로 전파된다.
- B/C안: `release.yml`은 `uses: khkim6040/demo-{b,c}-platform/.github/workflows/release-app.yml@v1.0.0` 호출 한 줄이다. 빌드 단계와 Dockerfile은 플랫폼 레포에서 checkout해 쓴다. 변경은 플랫폼 태그 + `@v` 한 줄 수정으로 전파된다.

### 6.3 릴리스와 롤백 절차

1. `deploy/overlays/dev/kustomization.yaml`의 해당 앱 이미지 태그를 올려 커밋한다.
2. `git tag api-v1.2.0 && git push --tags` → CI가 api 이미지만 만든다.
3. 롤백은 1번 커밋을 revert한다. CI는 레포에 커밋을 쓰지 않는다.

### 6.4 `deploy/`

```text
deploy/
├── base/{api,admin}/     # Deployment + Service
├── base/consumer/        # Deployment
├── base/batch/           # CronJob
└── overlays/dev/kustomization.yaml   # 네 앱의 이미지 태그
```

### 6.5 플랫폼 레포 CI

- `publish.yml`: `v*` 태그 → `./gradlew publish` → GitHub Packages. 인증은 `GITHUB_TOKEN`.
- 비즈니스 레포의 `settings.gradle.kts`에 GitHub Packages 저장소와 자격 증명(로컬 `~/.gradle/gradle.properties`, CI `GITHUB_TOKEN`)을 선언한다. 이 설정은 실험 1의 생성 비용에 포함된다.

## 7. 실험 프로토콜

### 7.1 기록 양식

`experiments/NN-<이름>.md`, 실험당 파일 하나.

```markdown
# 실험 N: 제목
## 시나리오와 성공 기준
## 결과
| 항목 | A | B | C |
|---|---|---|---|
| 플랫폼 측 수동 단계 수 (목록) | | | |
| 프로젝트 측 수동 단계 수, 프로젝트 1개당 (목록) | | | |
| 머지 충돌 파일 수 | | | |
| 의미적 충돌 (빌드·테스트 실패, 동작 변화) | | | |
| 함께 끌려온 무관한 변경 수 | | | |
| 검증 방법과 결과 | | | |
## 근거: 커밋 SHA, PR, CI 실행 링크
## 관찰: 잘못하기 쉬운 지점, 자동화할 수 있는 단계
```

- 시간은 측정하지 않는다.
- `00-baseline.md`: Phase 4 완료 시점에 세 플랫폼 레포의 움직이는 부품 수(아티팩트, 워크플로, 스크립트, 코드 줄 수)와 구조적 속성(프로젝트의 적용 시점·범위 선택 가능 여부, 구조적 대기 단계)을 한 번 기록한다.
- 프로젝트 N개일 때 비용은 최종 보고서에서 `플랫폼 측 + 프로젝트 측 × N`으로 계산한다.

### 7.2 실험 목록

| 실험 | 시나리오 | 성공 기준·측정 포인트 | 수행 |
|---|---|---|---|
| 1 생성 | 각 안의 절차로 `contract` 생성. 빌드 통과까지 손댄 파일 | `./gradlew build` 통과, 네 앱 기동. 생성 직후 수동 수정 단계 수 | A/B/C |
| 2 다중 앱 PR | `Contract`에 `beneficiary` 추가 → api·consumer 반영. PR 하나 | 영향 모듈 테스트 통과. 다중 레포 대비 PR 수 대조 | **한 번만** (플랫폼 무관) |
| 3 독립 배포 | api만 수정, 매니페스트 올림, `api-v1.1.0` 태그 | CI가 api 이미지만 빌드. 매니페스트 revert로 롤백 | A/B/C (CI 경로가 다름) |
| 4 보안 패치 | 전이 의존성 하나를 패치 버전으로 강제. A는 카탈로그 → 머지, B/C는 BOM 퍼블리시 → 카탈로그 버전 한 줄 | `dependencies --configuration runtimeClasspath`로 네 앱 모두 확인 | A/B/C |
| 5 공통 HTTP 변경 | Correlation Filter에 응답 헤더 하나 추가 | curl로 확인 | A/B/C |
| 6 커스터마이징 | contract가 read-timeout 기본값 변경. A는 스타터 파일 직접 수정(의도적 위반), B/C는 `application.yml`만 가능. 이후 플랫폼이 같은 기본값 변경 | A의 충돌 파일 수. 지연 스텁으로 실제 타임아웃 확인 | A/B/C |
| 7 CI/Docker 변경 | Dockerfile 베이스 이미지 태그 변경 | A는 머지, B/C는 플랫폼 태그 + `@v` 수정. CI 통과 | A/B/C |
| 8 버전 유지·롤백 | `claims` 생성(실험 1 재측정). claims는 최신, contract는 구버전. contract 올렸다 되돌림 | A는 태그 머지와 머지 커밋 revert, B/C는 숫자 변경 | A/B/C |
| 10 신규 공통 기능 | 관측성·복원력 스타터를 플랫폼에 추가 → contract·claims 전파. 측정은 관측성으로 | A는 `platform/` 모듈 + 앱 빌드 파일 머지(충돌 예상), B/C는 아티팩트 + 앱마다 의존성 한 줄 | A/B/C |

- 실험 9(MVC/WebFlux 혼용)는 삭제. 실험 10은 신규.
- 순서: 1 → 2 → 3 → 4 → 5 → 6 → 7 → 8 → 10. 실험 6이 만든 A안의 충돌 상태는 되돌리지 않고 이후 실험에 이어 간다.
- 실험 2·4는 실제 GitHub PR로 수행한다.

### 7.3 평가 기준과 실험의 대응

| 평가 기준 | 실험 |
|---|---|
| 신규 프로젝트 생성 편의성 | 1, 8 |
| 모노레포 개발 생산성 | 2 |
| 공통 의존성 버전 관리 효율 | 4 |
| 긴급 보안 패치 대응 | 4 |
| 서비스별 빌드·배포 독립성 | 3 |
| 공통 코드 변경 전파 비용 | 5, 7, 10 |
| Merge Conflict 및 Semantic Conflict | 6, 10, 모든 실험의 충돌 행 |
| 플랫폼 자체 유지보수 비용 | baseline, 모든 실험의 플랫폼 측 행 |
| 프로젝트 수 증가에 따른 복잡성 | 8, 보고서의 N개 비용 계산 |

## 8. 심화 단계 스타터 (Phase 6)

| 스타터 | 내용 | 비고 |
|---|---|---|
| `platform-observability-starter` | Actuator, Micrometer Prometheus, OpenTelemetry tracing 의존성 묶음. 기본 프로퍼티(엔드포인트 노출, 앱 이름 태그, 로그에 traceId) | 실험 10의 측정 대상 |
| `platform-resilience-starter` | Resilience4j Circuit Breaker + Retry 기본 설정 | `resilience4j-spring-boot4` 2.4.0(Boot 4.0 기준)을 Boot 4.1에서 검증. 실패 시 Spring Framework 7 내장 `@Retryable`로 Retry만 제공하고 Circuit Breaker는 제외 |

Kafka·MongoDB 스타터는 PoC 범위 밖이다. 구조 선택 후 채택된 안에서 만든다.

## 9. Phase

| Phase | 내용 | 완료 기준 |
|---|---|---|
| 0 준비 | JDK 25 설치, `insurance-platform-poc` 레포 push, 부트스트랩 스크립트, 지연 파라미터를 받는 외부 API 스텁 서버 | 8개 공개 레포 존재·clone. 스텁 기동 |
| 1 참조 모노레포 | `demo-a-platform` 전체 구현 (4·5·6장) | `./gradlew build` 통과. 네 앱 기동과 WebApplicationType 단언. CI 녹색. 태그 push로 api 이미지가 GHCR에 올라감 |
| 2 A안 | `demo-a-contract` clone + upstream, 패키지 치환. 실험 1(A) | contract 빌드·기동 |
| 3 B안 | `demo-b-platform` 퍼블리시, `demo-b-template`, `demo-b-contract`. 실험 1(B) | GitHub Packages 아티팩트로 contract 빌드·기동 |
| 4 C안 | `demo-c-platform` + 제너레이터, `demo-c-contract`. 실험 1(C) | 스크립트 한 번으로 생성된 프로젝트 빌드·기동 |
| 5 본 실험 | `00-baseline.md`, 실험 2~8. 실험 8에서 `claims` 3개 생성 | 실험 파일이 근거 링크와 함께 채워짐 |
| 6 심화 | 관측성·복원력 스타터를 세 플랫폼에 추가. 실험 10 | contract·claims 전파 완료 |
| 7 보고서 | 기준×실험 매트릭스, N개 비용 계산, 구조 추천. HTTP 프레임워크 항목은 "MVC 고정, WebFlux 추가 시 변경 범위"로만 정리 | `report/final.md` |

작업 방식:

- 커밋은 논리 단위로 쪼개고 제목 한 줄만 쓴다.
- 각 Phase가 끝나면 결과를 보고하고 다음으로 넘어간다. 실험 도중 설계와 다른 사실이 드러나면 멈추고 보고한다.
- Phase 7의 결론은 청사진 10장의 세 목표 각각에 대해 "증명됨 / 조건부 / 증명 안 됨"을 실험 번호와 함께 적고, A/B/C 중 하나를 추천하되 추천하지 않은 안을 택해야 하는 조건도 함께 적는다.

## 10. 범위 밖

- WebFlux, WebClient, Reactor, 코루틴
- Virtual Threads 성능 비교
- Kafka, MongoDB, `libs/persistence`
- 클러스터 실제 배포, Helm, ArgoCD
- 컨벤션 플러그인의 Gradle 플러그인 퍼블리시 (실험 7 결과 후 판단)
- 작업 시간 측정

## 11. 알려진 한계

- 에이전트가 수행하므로 "수동 단계 수"는 사람의 체감 난이도와 다를 수 있다. 관찰 항목에 잘못하기 쉬운 지점을 남겨 보완한다.
- A안의 "플랫폼 파일 불가침 규약"은 팀원이 지킬 것이라는 가정 위에 있다. 실험 6이 어겼을 때의 비용을 보여 준다.
- B와 C의 차이는 템플릿 전달 방식뿐이므로, 실험 4·5·7·10에서는 B와 C가 같은 결과를 낼 것으로 예상한다. 둘의 차이는 실험 1·8(생성)과 baseline(플랫폼 부품 수)에서 드러난다.
