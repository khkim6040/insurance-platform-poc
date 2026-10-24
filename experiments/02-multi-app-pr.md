# 실험 2: 다중 앱 PR

## 시나리오와 성공 기준

`Contract`에 `beneficiary`를 추가하고 api(요청 DTO·응답)와 consumer(`BENEFICIARY_CHANGED` 이벤트 처리)에 반영한다. PR 하나로 영향 모듈 테스트가 통과하면 성공. 다중 레포였다면 필요한 PR 수와 대조한다. 플랫폼 무관이므로 `demo-a-contract`에서 한 번만 수행했다.

## 결과

| 항목 | A (수행) | B | C |
|---|---|---|---|
| 플랫폼 측 수동 단계 수 (목록) | 0 | 동일 (플랫폼 무관) | 동일 |
| 프로젝트 측 수동 단계 수, 프로젝트 1개당 (목록) | 1 PR: 브랜치 → 8파일 수정(libs/domain 4, apps/api 2, apps/consumer 2, +34 −6) → push → CI → 머지. 다중 레포 환산: domain 라이브러리 PR + 퍼블리시 대기 + api PR + consumer PR = PR 3개, 대기 1회 | 동일 | 동일 |
| 머지 충돌 파일 수 | 0 | | |
| 의미적 충돌 (빌드·테스트 실패, 동작 변화) | 없음. `build` 통과, 테스트 28개(+3). 생성자 시그니처 변경이 컴파일 시점에 모든 호출처(SampleContracts, 테스트, api)를 드러냄 — 다중 레포라면 소비 측이 라이브러리 버전을 올리는 시점에야 드러남 | | |
| 함께 끌려온 무관한 변경 수 | 0 | | |
| 검증 방법과 결과 | PR CI(`./gradlew build` + kustomize) 녹색. `gh pr view`: files=8 | | |

## 근거: 커밋 SHA, PR, CI 실행 링크

- PR: https://github.com/khkim6040/demo-a-contract/pull/1, 변경 커밋 `77bcefe`, 머지 커밋 `2eb25c5`, CI https://github.com/khkim6040/demo-a-contract/actions/runs/40104755698

## 관찰: 잘못하기 쉬운 지점, 자동화할 수 있는 단계

- 모노레포의 이점은 "컴파일러가 영향 범위를 즉시 보여 준다"는 것이고, 비용은 "한 PR의 리뷰 범위가 3모듈"이라는 것. 이 실험은 A/B/C 어디서 해도 같다(비즈니스 레포 내부 변경).
- 테스트를 먼저 바꾸자 `ContractTest` 한 줄에서 인자 자리 밀림 오류 3개가 나왔다. 필수 생성자 인자를 중간에 끼워 넣으면 위치 인자 호출처가 전부 깨지므로, 모노레포에서는 그것이 곧 영향 범위 목록이 된다.
- 세 contract 중 A만 이 변경을 가진 상태로 실험 3·4로 넘어간다. 실험 4의 A안 upstream 머지가 프로젝트 소유 파일 변경과 충돌하지 않는지 확인하는 부수 효과가 있다.
