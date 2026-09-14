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

이 문서는 확장 구조이며, 아직 실행 검증된 R/MATLAB 계산 예제를 뜻하지 않습니다.
