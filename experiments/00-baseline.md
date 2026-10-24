# 00. Baseline: Phase 4 완료 시점의 플랫폼 부품 수와 구조적 속성

기록 시점: 2026-10-24, `demo-a-platform` `95d383a`(커밋 11), `demo-b-platform` `v1.0.0`(`61f4281`, 커밋 4) + `demo-b-template` `50e4394`(커밋 1), `demo-c-platform` `v1.0.0`(`4d80703`, 커밋 5).

## 움직이는 부품 수

| 항목 | A | B | C |
|---|---|---|---|
| 플랫폼 레포 수 | 1 | 2 (platform + template) | 1 |
| 퍼블리시 아티팩트 | 0 | 3 Maven (`io.github.khkim6040.platform:*` 1.0.0) + reusable workflow 1 | 3 Maven (`io.github.khkim6040.cplatform:*` 1.0.0) + reusable workflow 1 |
| Gradle 리프 모듈 (플랫폼 레포) | 6 (`libs:domain`, `platform:http-starter`, `apps:{api,admin,consumer,batch}`) | 3 (`platform-bom`, `platform-catalog`, `platform-http-starter`) + 템플릿 5 | 3 + 템플릿 5 |
| 컨벤션 플러그인 | 2 | 2 (템플릿에 복사본 2) | 2 (템플릿에 복사본 2) |
| 워크플로 | 2 (`ci`, `release`) | 3 (`ci`, `publish`, `release-app`) + 템플릿 2 (`ci`, `release`) | 3 + 템플릿 2 |
| 스크립트 | 0 | 0 | 1 (`create-project.sh`, 41줄) |
| Dockerfile | 1 | 1 (플랫폼 레포, 릴리스 시 checkout) | 1 (같음) |
| Kustomize 파일 | 11 | 템플릿 11 | 템플릿 11 |
| Kotlin 코드 (플랫폼 레포) | 30파일 786줄 (스타터 162 + 샘플 앱·도메인 624) | 7파일 162줄 (스타터만) + 템플릿 23파일 624줄 | 7파일 162줄 + 템플릿 23파일 624줄 |
| 추적 파일 수 | 71 | 32 + 템플릿 레포 57 | 90 (템플릿 57 포함) |
| 비즈니스 레포가 올리는 플랫폼 버전 숫자 | 0 (git ref: `upstream/main` 또는 태그 머지) | 2 (`platformVersion`, `release.yml` `@v`) | 2 (같음) |

세 안의 Kotlin 코드 총량은 786줄로 같다. A는 한 레포, B는 두 레포, C는 한 레포 안의 두 영역(플랫폼 + `templates/`)으로 나뉜다.

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

```bash
for r in demo-a-platform demo-b-platform demo-b-template demo-c-platform; do
  cd /Users/gwanhokim/personal-projects/insurance-poc/$r
  echo "== $r $(git rev-parse --short HEAD) commits=$(git rev-list --count HEAD)"
  echo "gradle_modules=$(./gradlew projects --console=plain -q | grep -c "Project ':")"   # 컨테이너 프로젝트(apps, libs, platform) 포함
  echo "convention_plugins=$(ls build-logic/src/main/kotlin/*.gradle.kts | wc -l)"
  echo "workflows=$(ls .github/workflows | wc -l)"
  echo "scripts=$(ls tools 2>/dev/null | wc -l) dockerfile=$(ls Dockerfile 2>/dev/null | wc -l)"
  echo "kustomize_files=$(find deploy -name '*.yaml' 2>/dev/null | wc -l)"
  echo "kt_platform=$(find . -name '*.kt' -not -path '*/build/*' -not -path './templates/*' | xargs wc -l | tail -1)"
  [ -d templates ] && echo "kt_template=$(find templates -name '*.kt' | xargs wc -l | tail -1) template_files=$(git ls-files templates | wc -l)"
  echo "tracked_files=$(git ls-files | wc -l)"
done
gh api "/user/packages?package_type=maven" --jq '.[] | "\(.repository.name) \(.name) v=\(.version_count)"'
```
