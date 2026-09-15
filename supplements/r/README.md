# R 계산 소스

R 원본은 이 폴더에 두고 프로젝트 루트에서 실행합니다.
CSV/JSON은 `assets/data/`, 정적 결과는 `assets/images/`에 저장합니다.
CI는 R을 실행하지 않으므로 소스와 이미 생성한 결과를 같은 PR에 포함하세요.
추가 규약: `docs/SUPPLEMENT_ARCHITECTURE.md`.

현재 구현: `solow-growth.R`은 base R만으로 Solow 모형의 36개 시나리오,
메타데이터, 정적 SVG를 생성합니다. 실행 명령은 다음과 같습니다.

```r
Rscript supplements/r/solow-growth.R
```
