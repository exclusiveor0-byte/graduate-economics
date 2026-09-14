# Contribution Guide

이 프로젝트는 Git 초보자도 참여할 수 있도록 단순한 workflow를 사용합니다.

## 가장 중요한 규칙

**`main`은 공식본입니다. 작업은 별도 branch에서 하고 Pull Request로 합칩니다.**

## 일반 팀원 workflow

### 1. 최신 상태 받기
GitHub Desktop에서 **Current Branch → main → Fetch origin**을 누릅니다.
**Pull origin**이 나타나면 눌러 실제 변경사항을 받습니다. Fetch만으로 작업 파일이 갱신되지는 않습니다.

### 2. 새 branch 만들기
예:
- `kim/preferences-fix`
- `lee/cournot-example`
- `oh/slutsky-proof`

가능하면 한 branch에는 하나의 명확한 작업만 담습니다.

### 3. VS Code에서 `.qmd` 수정
구조 파일(`_quarto.yml`, workflow, theme)은 특별한 이유가 없으면 수정하지 않습니다.

### 4. Commit
짧고 구체적으로 씁니다.

좋은 예:
- `Fix expenditure function notation`
- `Add Cournot linear example`
- `Clarify Kakutani assumptions`

### 5. Push origin

### 6. Create Pull Request
PR 템플릿의 체크리스트를 작성합니다.

작은 오탈자는 GitHub 웹의 해당 `.qmd` 파일 → 연필 버튼 → **Commit changes** →
**Create a new branch for this commit and start a pull request**로 제안해도 됩니다.
큰 수식·증명 수정은 로컬 미리보기를 권장합니다.

### 7. 초록 체크 확인
GitHub Actions의 **Quarto Render Check**가 통과하는지 확인합니다.

### 8. 검토 후 merge
Maintainer가 내용과 렌더 상태를 확인하고 merge합니다.

merge 후 GitHub Desktop에서 **main → Fetch origin → Pull origin**으로 공식본을 받습니다.
이전 branch를 계속 사용하지 않고 다음 작업에는 새 branch를 만듭니다.

---

## 파일 충돌을 줄이는 규칙

- 같은 Section 파일을 여러 명이 동시에 크게 수정하지 않습니다.
- 작업 시작 전 GitHub Issue 또는 팀 채널에서 담당 Section을 알립니다.
- 한 PR에서 unrelated Section을 대량으로 고치지 않습니다.
- 파일 이동/이름 변경은 Maintainer와 상의합니다.

## 문서 문법

Section 작성 시 [`templates/section-template.qmd`](templates/section-template.qmd)를 복사해 시작하는 것을 권장합니다.

Supplement는 [`templates/supplement-template.qmd`](templates/supplement-template.qmd)를 사용합니다.
