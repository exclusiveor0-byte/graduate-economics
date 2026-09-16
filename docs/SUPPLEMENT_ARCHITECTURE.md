# R / MATLAB / interactive 확장 규약

웹 배포를 검증한 뒤 첫 실제 supplement를 구현합니다.
본문은 Section별 독립 파일로 유지하고, 계산 소스와 결과를 아래 경로에 연결합니다.

```text
supplements/
  topic.qmd                  # 목적, 가정, 결과 해석, 관련 Section 링크
  r/topic.R                  # 로컬 계산 원본
  matlab/topic.m             # 로컬 계산 원본
  interactive/topic/         # 자체 완결 HTML/JS 또는 htmlwidgets
assets/
  data/topic.csv             # 브라우저가 읽는 계산 결과
  data/topic-metadata.json    # 가정, 모수, 실행환경, 생성 방법
  images/topic.png            # 정적 대체 자료
  gif/topic.gif              # 짧은 변화 과정일 때만
  video/topic.mp4            # 영상이 필요한 경우만
```

## 하나의 supplement를 추가하는 순서

1. 담당 Section을 정하고 `templates/supplement-template.qmd`로 설명 페이지를 만듭니다.
2. 계산은 R 또는 MATLAB 중 필요한 도구 하나를 선택합니다. 둘 다 구현할 필요는 없습니다.
3. 모수와 입력 경로를 파일 앞에 모으고, 난수가 있으면 seed를 고정합니다.
4. 결과 CSV/JSON과 정적 이미지, 실행환경을 함께 commit합니다.
5. HTML 위젯을 추가할 때 외부 파일 경로가 아니라 저장소 상대 경로를 사용합니다.
6. `_quarto.yml`의 chapters 등록은 maintainer가 담당합니다.
7. 한 PR 안에서 계산 소스·결과·설명을 함께 검토합니다.

## 데이터 약속

- CSV는 UTF-8, 첫 행 열 이름, 소수점은 `.`, 행 이름은 저장하지 않습니다.
- 열 이름에는 영문 소문자와 `_`를 사용하고, 단위·정의역은 metadata에 씁니다.
- 의미 있는 기준점 하나의 기대값과 수치 허용오차를 PR 설명에 적습니다.
- MATLAB의 NaN/Inf나 R의 NA를 JSON에 그대로 넣지 않습니다. 결측의 이유와 표시를 정합니다.
- 사이트에 공개할 수 있는 데이터와 산출물만 포함합니다.

## 표시와 접근성

interactive가 실패하거나 JavaScript가 꺼져도 정적 그림 또는 결과 표와 설명을 읽을 수 있게 합니다.
iframe에는 제목을 넣고, 키보드로 조작할 수 있는 입력 요소와 결과 설명을 제공합니다.
GIF/MP4는 자동 재생을 기본으로 하지 않고, 재생 제어와 대표 정적 화면을 둡니다.
시각화는 교육적 목적이 있는 경우에만 추가합니다.

## 실행 경계

현재 Actions에는 R/MATLAB runtime을 설치하지 않습니다.
재생산용 소스는 보관하고, 이미 생성한 결과만 Quarto에서 표시합니다.
Quarto 실행 셀 `{r}`나 외부 계산 엔진을 본문에 바로 추가하면 CI 요구사항이 달라집니다.
초기 버전은 일반 코드 블록으로 재현 코드를 보여주고 완성된 산출물을 링크합니다.

매 배포마다 계산해야 할 실제 요구가 생기면 R 패키지 잠금 파일 또는 MATLAB 버전·라이선스 구성을 별도로 결정합니다.
Shiny 서버가 필요한 앱과 서버 없이 실행되는 htmlwidgets/정적 JavaScript를 구분합니다.

## 첫 구현 후보: Slutsky 분해

관련 Section: `microeconomics/ch01-consumer/05-demand-properties.qmd`.
가격변화 전·후 선택과 보상된 선택을 비교하고, 먼저 보상의 정의를 명시합니다.
유한한 가격변화에서 초기 소비묶음을 살 수 있게 하는 Slutsky 보상과
초기 효용을 유지하는 Hicks 보상은 다른 실험입니다. 두 개념을 같은 이름으로 표시하지 않습니다.
본문에서 사용한 정의를 확인한 뒤 interactive + 결과 표/정적 그림부터 만들고,
애니메이션이 추가 설명에 도움이 되는 경우에만 GIF/MP4를 추가합니다.

첫 실제 구현은 supplements/interactive/slutsky-decomposition/에 있습니다. 이는 두 재화
Cobb--Douglas 소비자의 Slutsky/Hicks 분해를 비교하는 독립형 도구입니다. Quarto 페이지는
설명과 정적 대체 자료를 제공하고, iframe 안의 도구는 모수를 조작하게 합니다.

도구는 외부 네트워크 요청이나 서버 없이 동작하며 Quarto 책과 함께 배포됩니다.

## 첫 R 구현: Solow 성장모형

`supplements/r/solow-growth.R`은 외부 패키지 없이 Solow 기준경제의 모수 격자를
계산한다. 이 스크립트는 `assets/data/solow-growth-scenarios.json`, 실행 메타데이터,
그리고 정적 SVG를 함께 생성한다. 브라우저 도구는 JSON에 포함된 시나리오만 선택해
표시하므로 GitHub Pages에서 R 서버나 Shiny 서버가 필요하지 않다.

R 스크립트, 생성된 JSON·SVG, 설명 페이지, interactive HTML은 반드시 같은 PR에서
수정하고 검토한다. 모수 격자나 전이식을 바꾸면 프로젝트 루트에서 다음 명령을 실행한
뒤 생성물도 함께 commit한다.

```r
Rscript supplements/r/solow-growth.R
```

## 첫 MATLAB 구현: OLS 표본 기하와 표본 변동

`supplements/matlab/ols_geometry_monte_carlo.m`은 base MATLAB만으로 단일 설명변수
OLS의 기준 표본, 실행 메타데이터, 그리고 정적 PNG를 생성한다. 브라우저 도구는 같은
모형을 이용해 표본 수·기울기·오차 분산·Monte Carlo 반복 횟수를 조절하게 한다.

MATLAB 기준 산출물은 다음 명령으로 다시 생성한다.

```text
matlab -batch "run('supplements/matlab/ols_geometry_monte_carlo.m')"
```

난수 seed, 표본 수, Monte Carlo 반복 횟수와 $X'\hat u=0$ 검증값은 metadata에 함께
저장한다. MATLAB 실행은 현재 CI에 포함하지 않으므로, MATLAB 원본과 생성된 CSV·JSON·PNG를
같은 PR에서 검토한다.
