# Phase 1: 참조 모노레포 완료 기록

- 레포: https://github.com/khkim6040/demo-a-platform
- 완료 커밋: `95d383a`
- 버전: Spring Boot 4.1.2, Kotlin 2.4.21, Gradle 9.7.0, JDK 25 (Temurin 25.0.5+8)

## 완료 기준 확인

| 기준 | 증거 |
|---|---|
| `./gradlew build` 통과 | 로컬 실행 결과, 테스트 25개 (domain 7, http-starter 5, api 5, admin 3, consumer 3, batch 2) |
| api·admin이 SERVLET | `ApiApplicationTest`, `AdminApplicationTest` (`WebApplicationContext` 단언) |
| consumer·batch에 Servlet 없음 | `ConsumerApplicationTest`, `ContractExpiryJobTest` (`jakarta.servlet.Servlet` 부재 + `AnnotationConfigApplicationContext` 단언), 실행 로그에 Tomcat 없음 |
| 네 앱 실제 기동 | api: 스텁 연동 `quotedPremium=12000`, admin: 테스트, consumer: 12초 실행 로그에 PROCESSED/DUPLICATE/DEAD_LETTERED, batch: `expired 1 contract(s)` 후 exit 0 |
| Docker 이미지 | `docker build --build-arg APP=api .` 404 응답에 `X-Correlation-Id` + `application/problem+json`, batch 컨테이너 exit 0 |
| Kustomize 렌더링 | `kubectl kustomize deploy/overlays/dev`: Deployment 3, Service 2, CronJob 1, 이미지 4개 모두 `:0.1.0` |
| CI 녹색 | https://github.com/khkim6040/demo-a-platform/actions/runs/40095699138 |
| 태그 push로 api 이미지 | https://github.com/khkim6040/demo-a-platform/actions/runs/40095904705, `ghcr.io/khkim6040/demo-a-platform/api:0.1.0` (manifest digest `sha256:df98a346…`, 라벨 `org.opencontainers.image.revision=95d383a…`) |

## 구현 중 설계와 달랐던 점

- `org.jetbrains.kotlin.plugin.spring`을 모듈 빌드 파일에서 버전 없이 적용할 수 없었다(포함 빌드는 플러그인 클래스패스에만 올려 주고 id 해석은 해 주지 않음). `platform.kotlin-library` 컨벤션 안으로 옮겼다. 컨벤션 플러그인 수는 여전히 2개.
- `platform.spring-boot-app`의 `spring-boot-starter-test`만으로는 `AutoConfigureMockMvc`·`MockMvcTester`가 없다. consumer·batch의 테스트 클래스패스에 Servlet이 들어가면 안 되므로 컨벤션이 아니라 `apps/api`·`apps/admin`의 `build.gradle.kts`에 `spring-boot-starter-webmvc-test`를 직접 추가했다.
- Spring Batch 6.0.6에서 `RepeatStatus`가 `org.springframework.batch.repeat` → `org.springframework.batch.infrastructure.repeat`로 이동했다. import 한 줄 수정. 계획에 적힌 `job`/`step` 하위 패키지 import(`Job`, `JobParameters`, `Step`, `StepBuilder`, `JobBuilder`)는 그대로 맞았다.
- consumer 테스트에서 `FakeEventSource`가 기동 즉시 `evt-1`을 처리해 테스트의 `evt-1`이 DUPLICATE가 되었다. 테스트 이벤트 ID를 `test-*`로 바꿨다(구현 변경 없음).
- JDK 25는 `brew install --cask temurin@25`가 sudo를 요구해 실패했고, Temurin tar.gz를 `~/Library/Java/JavaVirtualMachines/temurin-25.jdk`에 풀어 설치했다. `java_home -v 25`로 동일하게 인식된다.
- gh 토큰에 `read:packages` 스코프가 없어 GHCR 패키지 API 대신 `docker manifest inspect`와 워크플로 로그로 이미지를 확인했다.

## 움직이는 부품 수 (baseline 사전 기록)

- Gradle 모듈 6 (`libs:domain`, `platform:http-starter`, `apps:{api,admin,consumer,batch}`), 컨벤션 플러그인 2, 워크플로 2, Dockerfile 1, Kustomize 파일 11, Kotlin 소스 30파일 786줄 (`find . -name '*.kt' -not -path '*/build/*' | xargs wc -l`)
