# 실험 8: 버전 유지·롤백 (`claims` 생성 재측정, contract 올렸다 되돌림)

## 시나리오와 성공 기준

플랫폼 `v1.5.0`(`server.shutdown: graceful` 기본값 + 스타터 테스트 단언 1줄)을 낸 뒤 ① 각 안의 절차로 두 번째 프로젝트 `claims`를 최신 플랫폼 기준으로 만들어 실험 1을 재측정하고(성공 기준: `clean build`, CI, `api:0.1.0` 이미지), ② 구버전에 있는 contract(A는 `v1.4.0` 머지 상태, B/C는 `platformVersion=1.3.0`)를 `v1.5.0`으로 올렸다가 되돌린다(A: 태그 머지 → 머지 커밋 `revert -m 1`, B/C: `platformVersion` 변경 → `revert`). 성공 기준: 올린 뒤 graceful 포함, 되돌린 뒤 미포함, 빌드·CI 통과. 두 프로젝트(claims 최신, contract 구버전)가 서로 다른 플랫폼 버전에 머무를 수 있음을 보인다.

B/C 템플릿의 버전 핀(`platformVersion=1.0.0`, `release-app.yml@v1.0.0`)은 실험 4~7 동안 갱신하지 않았으므로, claims를 최신으로 만들려면 먼저 핀을 1.5.0으로 올려야 했다. 이 비용을 플랫폼 측에 계상한다.

## 결과

| 항목 | A | B | C |
|---|---|---|---|
| 플랫폼 측 수동 단계 수 (목록) | 3: ① yml 1줄 + 테스트 1줄(2파일) ② PR → CI → 머지 ③ 태그 `v1.5.0`. 템플릿 갱신 없음(clone이 곧 최신) | 5: ①~③ 같음 ④ publish 대기 ⑤ **템플릿 레포 핀 갱신** 2파일(`gradle.properties`, `release.yml`) → push → CI. 별도 레포이며 publish가 끝난 뒤에만 CI가 통과한다(순서 의존) | 4: ① yml·테스트 2파일 + **템플릿 핀 2파일**(같은 PR, 총 4파일) ② PR → CI → 머지 ③ 태그 ④ publish 대기 |
| 프로젝트 측 수동 단계 수, 프로젝트 1개당 (목록) | **생성 5단계**(실험 1과 동일: 리모트 재구성·태그 삭제, 패키지 치환 23파일, overlay, README, push+태그), 손댄 파일 25. 지울 upstream 태그 **6**(실험 1 때 1). **올림 1**: `fetch upstream tag v1.5.0` + `merge v1.5.0` → push → CI(손댄 파일 0, 들어온 파일 2). **되돌림 1**: `revert -m 1` → push → CI | **생성 4단계**(실험 1과 동일), 손댄 파일 30. 올림 1: `gradle.properties` 1줄 → push → CI. 되돌림 1: `revert` → push → CI | **생성 2단계**(`create-project.sh` 한 명령 + remote add·push·태그), 손댄 파일 **0**. 올림·되돌림 B와 같음 |
| 머지 충돌 파일 수 | 0 (v1.5.0의 yml 변경이 파일 머리, 실험 6 위반 줄은 파일 끝이라 떨어져 있음) | 0 | 0 |
| 의미적 충돌 (빌드·테스트 실패, 동작 변화) | 없음. 단 revert 후 `git merge upstream/main`이 `Already up to date.`를 내며 graceful은 돌아오지 않는다(되돌린 머지는 이력상 이미 들어온 것으로 취급). 재적용은 revert 커밋을 다시 revert해야 한다 | 없음. 되돌린 뒤 다시 올리는 데 함정 없음(숫자를 다시 쓰면 됨) | 없음 |
| 함께 끌려온 무관한 변경 수 | 0 | 0 | 0 |
| 검증 방법과 결과 | claims: `clean build` 테스트 25, `platform-defaults.yml`에 graceful 1(최신 기준), CI·release ok, `api:0.1.0` Alpine. contract: 머지 후 graceful 1·`read-timeout: 3s` 유지 → revert 후 graceful 0·3s 유지, 빌드·CI 2회 ok | claims: 테스트 20, `platformVersion=1.5.0`·`@v1.5.0`, CI·release ok, Alpine. contract: 1.5.0 jar의 yml에 graceful 1 → revert 후 `platformVersion=1.3.0`, `runtimeClasspath`에 `platform-http-starter:1.3.0` | claims: 테스트 20, `1.5.0`/`@v1.5.0`, 생성 커밋 메시지 `templates/multi-service@f608e95`(= `v1.5.0`), CI·release ok, Alpine. contract: B와 같음(`cplatform:…:1.3.0`) |
| 에이전트 개입 (사람 결정·행동이 필요했던 지점) | 0 | 0 (레포가 미리 없어 실험 1의 삭제 승인이 필요 없었음) | 0 |

## 근거: 커밋 SHA, PR, CI 실행 링크

- 플랫폼 v1.5.0: A PR https://github.com/khkim6040/demo-a-platform/pull/5 (머지 `2cc5429`, PR CI https://github.com/khkim6040/demo-a-platform/actions/runs/40151829527); B PR https://github.com/khkim6040/demo-b-platform/pull/5 (머지 `dd5bd8e`), publish https://github.com/khkim6040/demo-b-platform/actions/runs/40151965925; C PR https://github.com/khkim6040/demo-c-platform/pull/5 (머지 `f608e95`), publish https://github.com/khkim6040/demo-c-platform/actions/runs/40152037492. B 템플릿 핀 커밋 `367078b` CI https://github.com/khkim6040/demo-b-template/actions/runs/40152120227
- claims A https://github.com/khkim6040/demo-a-claims — 패키지 치환 `2987560`, overlay·README `f0bc128`, ci https://github.com/khkim6040/demo-a-claims/actions/runs/40152236884, release https://github.com/khkim6040/demo-a-claims/actions/runs/40152405586
- claims B https://github.com/khkim6040/demo-b-claims — 템플릿 초기 커밋 `0aa2127`, 치환 `ef9a128`, `1f74a6a`, ci https://github.com/khkim6040/demo-b-claims/actions/runs/40152513596, release https://github.com/khkim6040/demo-b-claims/actions/runs/40152696788
- claims C https://github.com/khkim6040/demo-c-claims — 생성 커밋 `94cff57`, ci https://github.com/khkim6040/demo-c-claims/actions/runs/40152803367, release https://github.com/khkim6040/demo-c-claims/actions/runs/40152986616
- contract A: 머지 `81d95b0` CI https://github.com/khkim6040/demo-a-contract/actions/runs/40153080210, revert `0e25686` CI https://github.com/khkim6040/demo-a-contract/actions/runs/40153153791
- contract B: bump `d7dd3ab` CI https://github.com/khkim6040/demo-b-contract/actions/runs/40153212099, revert `66f4433` CI https://github.com/khkim6040/demo-b-contract/actions/runs/40153303372
- contract C: bump `541214d` CI https://github.com/khkim6040/demo-c-contract/actions/runs/40153358752, revert `81fc5d2` CI https://github.com/khkim6040/demo-c-contract/actions/runs/40153432239

## 관찰: 잘못하기 쉬운 지점, 자동화할 수 있는 단계

- **B/C 템플릿의 버전 핀은 플랫폼 릴리스마다 갱신해야 하는 숨은 비용**이다. 실험 4~7에서 네 번 릴리스하면서 한 번도 올리지 않았고, 그 사이 템플릿으로 프로젝트를 만들었다면 1.0.0(Ubuntu Dockerfile, 헤더 없는 Filter)으로 시작했을 것이다. C는 템플릿이 플랫폼 레포 안에 있어 같은 PR에서 고치면 되고 태그에 함께 묶이지만, B는 별도 레포라 publish 완료 후 따로 커밋해야 하며 순서를 어기면 템플릿 CI가 실패한다. A는 이 비용이 구조적으로 없다(clone = 최신).
- 실험 1 재측정 결과는 실험 1과 같다(A 5단계/25파일, B 4/30, C 2/0). 단 A의 지울 태그가 1 → 6으로 늘었다. 플랫폼 릴리스가 쌓일수록 A의 생성 절차에서 "태그 정리" 단계의 크기가 커진다(`git tag -d $(git tag)` 한 줄이라 단계 수는 같다).
- A의 되돌림 함정: 머지 커밋을 revert하면 이력상 v1.5.0은 "이미 머지됨"이므로 다음 `merge upstream/main`이 그 내용을 다시 가져오지 않는다. 플랫폼이 v1.6.0을 내면 A contract는 v1.6.0 diff만 받고 v1.5.0 내용(graceful)은 영원히 빠진 채 빌드가 통과한다. 재적용하려면 revert 커밋을 revert해야 하며, 이 사실을 아는 사람이 팀에 있어야 한다. B/C는 숫자라서 어느 방향으로든 다시 쓰면 끝이다.
- 두 프로젝트가 다른 버전에 머무는 방식: A는 "이력에서 어디까지 머지했나"이고 레포 밖에서 읽을 수 없다(태그도 없음). B/C는 `gradle.properties` 한 줄이라 `grep`으로 전 프로젝트의 버전 분포를 알 수 있다. 프로젝트가 많아질수록 이 가독성 차이가 운영 비용이 된다.
- N=2일 때 전파 비용 = 플랫폼 측 + 프로젝트 측 × 2. 이번 실험에서 프로젝트 측은 세 안 모두 1단계(머지 또는 1줄)로 같았으므로 N에 비례하는 항은 같고, 차이는 플랫폼 측 상수항(A 3, B 5, C 4)이다.
- A contract에는 이제 `v1.5.0` 태그가 로컬에 있다(push 안 함). 태그로 fetch한 머지는 "어느 버전을 받았는지"를 머지 커밋 메시지(`Merge tag 'v1.5.0'`)에 남겨 `merge upstream/main`보다 추적성이 낫다. A의 운영 규칙으로 "태그만 머지"를 두는 것이 가능하다.
- Phase 6 시작 상태: A contract는 v1.5.0 머지가 revert된 상태, B/C contract는 `platformVersion=1.3.0`·`@v1.4.0`, claims 셋은 v1.5.0 기준. 실험 10에서 A가 최신으로 가려면 revert의 revert가 먼저 필요하며 이를 A의 업그레이드 비용으로 센다.
