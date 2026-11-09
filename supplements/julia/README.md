# Julia 계산 소스 (Computational Supplements in Julia)

이 디렉터리는 대학원 경제학 아카이브의 핵심 수치 계산, 몬테카를로 시뮬레이션, 미분방정식 동학 알고리즘을 담고 있는 **Julia 소스 코드** 저장소입니다.

기존에 분산되어 있던 MATLAB 및 R 스크립트를 과학 계산과 계량 이론 연구에 최적화된 고성능 언어인 **Julia**로 전면 통일하여 포팅하였습니다.

---

## 1. 실행 원칙 및 환경

- **실행 위치**: 저장소 루트 디렉터리(`c:\work\graduate-economics-v1.2-migrated`)에서 실행합니다.
- **의존성 제로 (Zero-Dependency)**: 외부 서드파티 패키지 설치 없이 Julia 표준 라이브러리(`LinearAlgebra`, `Statistics`, `Random`, `Printf`, `DelimitedFiles`)만으로 구동되도록 설계되어, vanilla Julia 환경에서 즉시 실행됩니다.
- **결과 산출물**: 모든 계산 결과(CSV, JSON, 정적 SVG 등)는 `assets/data/` 및 `assets/images/`에 결정론적(deterministic seed)으로 자동 생성됩니다.

### 실행 방법

```bash
# 개별 스크립트 실행 (프로젝트 루트 기준)
julia supplements/julia/solow_growth.jl
julia supplements/julia/islm_fiscal_shock.jl
julia supplements/julia/iv_weak_instruments.jl
julia supplements/julia/ols_geometry.jl
julia supplements/julia/ols_projection.jl
julia supplements/julia/ramsey_saddle_path.jl
julia supplements/julia/did_parallel_trends.jl

# 전체 7개 스크립트 일괄 실행 및 검증
julia supplements/julia/run_all.jl
```

---

## 2. 파일 목록 및 담당 주제

| 파일명 | 담당 주제 및 핵심 수치 알고리즘 | 생성 산출물 | 비고 |
|---|---|---|---|
| `solow_growth.jl` | **Solow–Swan 성장모형**<br>이산시간 전이경로 격자(36개 시나리오) 및 정상상태 수렴 계산 | `assets/data/solow-growth-scenarios.json`<br>`assets/data/solow-growth-metadata.json`<br>`assets/images/solow-growth-static.svg` | R 스크립트 포팅 |
| `islm_fiscal_shock.jl` | **IS–LM 재정충격 동학**<br>단기 균형 수치해, 승수효과 및 부분구축 궤적 | `assets/data/islm-fiscal-path.csv`<br>`assets/data/islm-fiscal-metadata.json`<br>`assets/images/islm-fiscal-static.svg` | MATLAB 포팅 |
| `iv_weak_instruments.jl` | **도구변수와 약한 도구**<br>DGP 몬테카를로(2,000회), OLS 편향, 2SLS 일치성, 1단계 F-통계량 | `assets/data/iv-weak-instruments-baseline.csv`<br>`assets/data/iv-weak-instruments-metadata.json` | MATLAB 포팅 |
| `ols_geometry.jl` | **OLS 표본 기하와 표본 변동**<br>잔차 직교성($X'e = 0$), Fixed-$X$ 몬테카를로(1,500회) 계수 표본분포 | `assets/data/ols-geometry-baseline.csv`<br>`assets/data/ols-geometry-metadata.json` | MATLAB 포팅 |
| `ols_projection.jl` | **OLS 직교사영과 정상방정식**<br>사영행렬($P_X, M_X$), FWL 정리, 변수추가 $R^2$ 분해, 다중공선성 조건수 진단 | `assets/data/ols-projection-metadata.json` | MATLAB 포팅 |
| `ramsey_saddle_path.jl` | **Ramsey–Cass–Koopmans 모형**<br>선형화 야코비안 고유치 분해, 역시간 적분(Reverse-time integration) 안장경로, 슈팅 알고리즘(이분법) | `assets/data/ramsey-saddle-path-metadata.json` | MATLAB 포팅 |
| `did_parallel_trends.jl` | **이중차분법(DiD)과 평행추세**<br>패널 DGP, TWFE 고속 추정, 이벤트 스터디 사전추세 $\chi^2$ 검정, 1,000회 몬테카를로 편향 분석 | `assets/data/did-event-study-baseline.csv`<br>`assets/data/did-parallel-trends-metadata.json`<br>`assets/images/did-parallel-trends-static.svg` | 신규 생성 |
