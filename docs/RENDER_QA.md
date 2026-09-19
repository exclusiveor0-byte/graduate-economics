# 렌더·가독성 검수 기록

검수일: 2026-09-14 · Quarto 1.10.18 · Windows / Microsoft Edge (headless)

## 결과

- 전체 58페이지 렌더 성공, 내부 링크 및 anchor 검사 통과.
- 수식 3,853개, 의미 블록 363개, 접힌 증명/상세 설명 95개 보존.
- 58페이지 × 1440px / 390px / 320px = 브라우저 검사 174건 통과.
- 모든 페이지의 MathJax CHTML 출력과 수식 오류 여부 검사.
- 증명 제목을 실제 클릭한 뒤 접힌 블록을 펼쳐 수식 표시 및 화면 넘침 검사.
- 표 스크롤 영역, 문서 가로 넘침, 브라우저 JavaScript 오류 검사.
- 홈·소비자이론 Section의 데스크톱과 모바일 스크린샷 직접 확인. 모바일 메뉴의 긴 제목 줄바꿈과 화면 내 배치도 확인.
- 미시경제학 48개 qmd는 작업 전 백업과 바이트 단위 일치. microeconomics/index.qmd에만 Chapter 선택 링크 표 추가.

## 수정한 문제

- 넓은 본문을 최대 820px로 제한하고 한영 혼용 글꼴·행간·제목 간격 정리.
- 정리/정의/증명 색상과 긴 표·수식의 스크롤 처리.
- 320px에서 협업 안내의 긴 파일명 및 3페이지의 이전/다음 링크 넘침 수정. 열린 모바일 목차 폭과 Chapter 제목 줄바꿈도 수정.
- 전체 빌드와 실행 중인 preview의 생성 파일 충돌: 별도 검수 폴더에서 전체 빌드 완료.
- 원본 학술 내용과 수식·증명은 수정하지 않음.

## 검증 범위의 한계

- 렌더 검수는 경제학 명제의 새 증명 또는 내용 peer review가 아님.
- 외부 참고문헌 URL의 서버 응답 및 실제 팀원 계정으로 로그인한 GitHub 수정 링크는 미검증.
- Slutsky 검색으로 소비자수요 Section 발견, 390px/320px 모바일 목차에서 1.4 Section 이동 검증 완료.
- 이 보고서는 로컬 검수 결과입니다. 원격 Actions 실행과 공개 배포는 별도 실행 기록으로 확인합니다.
- R/MATLAB 확장은 경로·데이터·검토 규약 준비 단계이며 runtime 실행/interactive 구현은 후속.

## 페이지별 결과

| 페이지 | 수식 | 의미 블록 | 접힌 블록 | 렌더/링크 | 3개 화면 폭 |
|---|---:|---:|---:|---|---|
| `index.qmd` | 0 | 0 | 0 | 통과 | 통과 |
| `collaboration.qmd` | 0 | 1 | 0 | 통과 | 통과 |
| `microeconomics/index.qmd` | 0 | 1 | 0 | 통과 | 통과 |
| `microeconomics/ch00-foundations/index.qmd` | 0 | 2 | 0 | 통과 | 통과 |
| `microeconomics/ch00-foundations/01-model-structure.qmd` | 5 | 1 | 0 | 통과 | 통과 |
| `microeconomics/ch00-foundations/02-notation-logic.qmd` | 111 | 4 | 0 | 통과 | 통과 |
| `microeconomics/ch00-foundations/03-euclidean-space-sets.qmd` | 33 | 2 | 0 | 통과 | 통과 |
| `microeconomics/ch00-foundations/04-topology-convergence.qmd` | 109 | 11 | 1 | 통과 | 통과 |
| `microeconomics/ch00-foundations/05-functions-correspondences.qmd` | 69 | 9 | 0 | 통과 | 통과 |
| `microeconomics/ch00-foundations/06-convexity.qmd` | 96 | 8 | 0 | 통과 | 통과 |
| `microeconomics/ch00-foundations/07-matrix-calculus-optimization-kkt.qmd` | 94 | 6 | 1 | 통과 | 통과 |
| `microeconomics/ch00-foundations/08-parameterized-optimization.qmd` | 81 | 5 | 2 | 통과 | 통과 |
| `microeconomics/ch00-foundations/09-fixed-point-existence.qmd` | 19 | 4 | 1 | 통과 | 통과 |
| `microeconomics/ch00-foundations/10-separation-supporting-prices.qmd` | 18 | 4 | 0 | 통과 | 통과 |
| `microeconomics/ch00-foundations/11-math-map.qmd` | 1 | 1 | 0 | 통과 | 통과 |
| `microeconomics/ch00-foundations/exercises.qmd` | 90 | 0 | 0 | 통과 | 통과 |
| `microeconomics/ch00-foundations/references.qmd` | 0 | 0 | 0 | 통과 | 통과 |
| `microeconomics/ch01-consumer/index.qmd` | 0 | 2 | 0 | 통과 | 통과 |
| `microeconomics/ch01-consumer/01-components.qmd` | 53 | 5 | 0 | 통과 | 통과 |
| `microeconomics/ch01-consumer/02-preferences-utility.qmd` | 286 | 21 | 6 | 통과 | 통과 |
| `microeconomics/ch01-consumer/03-consumer-problem.qmd` | 178 | 18 | 5 | 통과 | 통과 |
| `microeconomics/ch01-consumer/04-indirect-utility-expenditure.qmd` | 357 | 28 | 9 | 통과 | 통과 |
| `microeconomics/ch01-consumer/05-demand-properties.qmd` | 257 | 28 | 9 | 통과 | 통과 |
| `microeconomics/ch01-consumer/supplement-standard-utility.qmd` | 65 | 2 | 1 | 통과 | 통과 |
| `microeconomics/ch01-consumer/exercises.qmd` | 48 | 0 | 0 | 통과 | 통과 |
| `microeconomics/ch01-consumer/references.qmd` | 0 | 0 | 0 | 통과 | 통과 |
| `microeconomics/ch02-producer/index.qmd` | 0 | 2 | 0 | 통과 | 통과 |
| `microeconomics/ch02-producer/01-firm-technology.qmd` | 126 | 12 | 3 | 통과 | 통과 |
| `microeconomics/ch02-producer/02-geometry-scale.qmd` | 90 | 9 | 3 | 통과 | 통과 |
| `microeconomics/ch02-producer/03-cost-minimization.qmd` | 183 | 16 | 6 | 통과 | 통과 |
| `microeconomics/ch02-producer/04-production-duality.qmd` | 114 | 12 | 5 | 통과 | 통과 |
| `microeconomics/ch02-producer/05-competitive-firm.qmd` | 163 | 22 | 8 | 통과 | 통과 |
| `microeconomics/ch02-producer/supplement-standard-technologies.qmd` | 31 | 0 | 0 | 통과 | 통과 |
| `microeconomics/ch02-producer/exercises.qmd` | 40 | 0 | 0 | 통과 | 통과 |
| `microeconomics/ch02-producer/references.qmd` | 0 | 0 | 0 | 통과 | 통과 |
| `microeconomics/ch03-partial-equilibrium/index.qmd` | 0 | 2 | 0 | 통과 | 통과 |
| `microeconomics/ch03-partial-equilibrium/01-perfect-competition.qmd` | 140 | 17 | 5 | 통과 | 통과 |
| `microeconomics/ch03-partial-equilibrium/02-market-conduct.qmd` | 257 | 33 | 10 | 통과 | 통과 |
| `microeconomics/ch03-partial-equilibrium/03-equilibrium-welfare.qmd` | 107 | 12 | 4 | 통과 | 통과 |
| `microeconomics/ch03-partial-equilibrium/04-linear-model-exercises.qmd` | 67 | 2 | 0 | 통과 | 통과 |
| `microeconomics/ch03-partial-equilibrium/references.qmd` | 0 | 0 | 0 | 통과 | 통과 |
| `microeconomics/ch04-pure-exchange/index.qmd` | 0 | 2 | 0 | 통과 | 통과 |
| `microeconomics/ch04-pure-exchange/01-primitives-feasibility.qmd` | 32 | 5 | 0 | 통과 | 통과 |
| `microeconomics/ch04-pure-exchange/02-prices-income-demand.qmd` | 49 | 5 | 1 | 통과 | 통과 |
| `microeconomics/ch04-pure-exchange/03-walrasian-equilibrium-law.qmd` | 39 | 7 | 2 | 통과 | 통과 |
| `microeconomics/ch04-pure-exchange/04-existence-truncated-economy.qmd` | 168 | 14 | 6 | 통과 | 통과 |
| `microeconomics/ch04-pure-exchange/05-pareto-contract-set.qmd` | 38 | 6 | 1 | 통과 | 통과 |
| `microeconomics/ch04-pure-exchange/06-welfare-theorems.qmd` | 111 | 11 | 3 | 통과 | 통과 |
| `microeconomics/ch04-pure-exchange/07-core-competitive-limit.qmd` | 81 | 11 | 3 | 통과 | 통과 |
| `microeconomics/ch04-pure-exchange/supplement-examples-exercises.qmd` | 47 | 0 | 0 | 통과 | 통과 |
| `microeconomics/ch04-pure-exchange/references.qmd` | 0 | 0 | 0 | 통과 | 통과 |
| `macroeconomics/index.qmd` | 0 | 0 | 0 | 통과 | 통과 |
| `econometrics/index.qmd` | 0 | 0 | 0 | 통과 | 통과 |
| `supplements/index.qmd` | 0 | 0 | 0 | 통과 | 통과 |
| `supplements/visualization-guide.qmd` | 0 | 0 | 0 | 통과 | 통과 |
| `references.qmd` | 0 | 0 | 0 | 통과 | 통과 |
