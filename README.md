# Graduate Economics Knowledge Base

Quarto Book + GitHub + GitHub Actions + GitHub Pages를 이용한 공동 경제학 정리노트 저장소입니다.

## 팀원이 알아야 할 것

터미널 Git 사용을 전제로 하지 않습니다.

기본 협업 도구:
1. GitHub Desktop
2. VS Code
3. Quarto

기본 작업 순서:
1. `main → Fetch origin → Pull origin` (Pull이 나타날 때)
2. `New Branch`
3. `.qmd` 수정
4. `Commit`
5. `Push`
6. `Create Pull Request`
7. GitHub Actions의 초록 체크 확인
8. Maintainer가 검토 후 merge

자세한 설명은 [`docs/FIRST_DAY.md`](docs/FIRST_DAY.md)를 참고하세요.

관리자 설정은 [`docs/MAINTAINER_SETUP.md`](docs/MAINTAINER_SETUP.md),
후속 계산 자료 구조는 [`docs/SUPPLEMENT_ARCHITECTURE.md`](docs/SUPPLEMENT_ARCHITECTURE.md)를 참고하세요.

## 로컬 미리보기

VS Code의 Quarto Preview 기능을 권장합니다.

터미널을 사용할 수 있다면:

```bash
quarto preview
```

전체 렌더 확인:

```bash
quarto render
```

## Repository 원칙

- `main` = 현재 공식본
- `main`에 직접 대규모 수정하지 않음
- **Section 하나 = 독립 `.qmd` 페이지**를 원칙으로 함
- Chapter `index.qmd`는 landing page이며, 구조 변경은 Maintainer가 담당
- 내용 수정은 Pull Request를 통해 검토
- Interactive가 필수는 아님
- Interactive 자료에는 가능하면 GIF/MP4/static fallback을 함께 제공

## 공개 저장소와 웹사이트

- 원본: [exclusiveor0-byte/graduate-economics](https://github.com/exclusiveor0-byte/graduate-economics)
- 읽기 사이트: [대학원 경제학 정리노트](https://exclusiveor0-byte.github.io/graduate-economics/)

원문과 읽기 사이트 모두 공개합니다. PR의 초록 체크와 내용 리뷰를 거쳐 main에 반영하면
GitHub Actions가 전체 렌더와 링크/블록 검사를 수행한 뒤 Pages에 배포합니다.
설정은 [`docs/MAINTAINER_SETUP.md`](docs/MAINTAINER_SETUP.md),
검수 기록은 [`docs/RENDER_QA.md`](docs/RENDER_QA.md)를 참고하세요.

## Migration status

- Microeconomics Chapter 0–4: migrated from the integrated HTML study notes
- Each Section/Supplement/Exercise/Reference: standalone `.qmd` page
- Math: converted to Quarto/Pandoc `$...$` and `$$...$$` syntax
- Definition/Theorem/Proposition/Proof/Remark/Caution: converted to Quarto callouts
- R supplement: Solow 성장모형 전이경로를 base R로 계산하고 정적 Pages 도구에 연결
- MATLAB supplements: structure prepared; content to be added separately
