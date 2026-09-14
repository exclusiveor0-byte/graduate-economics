# Maintainer: 저장소와 GitHub Pages

## 확정된 공개 구성

- 저장소: https://github.com/exclusiveor0-byte/graduate-economics
- 읽기 주소: https://exclusiveor0-byte.github.io/graduate-economics/
- 원문과 읽기 사이트를 모두 공개하는 구성입니다.
- 수정은 Section별 PR로 검토합니다. 일반 기여자는 터미널 Git을 사용하지 않아도 됩니다.

## Actions

- **Quarto Render Check**: PR → Quarto 1.10.18 전체 렌더 → 페이지·링크·callout 검사 → book-preview 저장.
- **Publish Quarto Book**: main 반영 → 같은 렌더/검사 → GitHub Pages 배포.
- PR workflow는 저장소 읽기 권한만 사용합니다. Pages 배포 권한은 deploy job에만 있습니다.
- R/MATLAB runtime은 CI에 설치하지 않습니다. 완성된 산출물을 commit하는 구조를 유지합니다.

## 처음 한 번 하는 설정

1. Settings → Pages → Source를 **GitHub Actions**로 선택합니다.
2. main에 프로젝트를 올린 뒤 Publish Quarto Book의 build와 deploy를 확인합니다.
3. Pages 화면의 실제 주소에서 홈·깊은 Section 링크·검색·모바일 메뉴를 확인합니다.
4. 작은 문서 변경 PR로 Quarto Render Check를 한 번 실행합니다.
5. main 보호 규칙의 필수 검사로 **Quarto Render Check**를 선택합니다.

처음 push가 Pages 설정 전에 실행되어 실패했다면 설정 후 workflow를 다시 실행합니다.

## main 보호

- Pull Request 필수
- Quarto Render Check 필수
- 검토 의견 해결 필수
- force push와 main 삭제 금지
- 다른 리뷰어가 실제로 참여한 이후 approval 1개 필수

담당자 혼자일 때 approval을 강제하면 본인 PR을 승인할 수 없어 막힐 수 있습니다.
선형 이력·rebase·merge queue는 요구하지 않습니다. 충돌은 maintainer가 함께 처리합니다.

## 팀원 첫 PR

`docs/FIRST_DAY.md`를 전달합니다. 오탈자 하나로 다음 흐름을 한 번 경험하게 합니다.

main → Fetch/Pull → 새 branch → 수정 → commit → push → PR → 초록 체크 → review/merge → Pages 반영.

작은 수정은 GitHub 웹에서도 branch와 PR을 만들어 제출할 수 있습니다.
Actions 실행 화면의 **Artifacts → book-preview**는 리뷰용 ZIP이며 임시 사이트 주소는 아닙니다.

## 로컬 검수

같은 폴더에서 preview와 render를 동시에 실행하면 생성 파일 이동이 충돌할 수 있습니다.
미리보기를 중지한 뒤 전체 렌더를 실행하거나 별도 복사본에서 검수합니다.

```bash
quarto render
python scripts/check_render.py
```

브라우저 자동 검수는 maintainer 선택사항입니다. Node와 Playwright를 준비하고
렌더한 _book을 로컬 HTTP 서버로 제공한 뒤 실행합니다.

```bash
node scripts/browser_qa.cjs http://127.0.0.1:8765
```

일반 기여자에게 Python·Node 설치를 요구하지 않습니다.

## 공식 문서

- [Quarto GitHub Pages 배포](https://quarto.org/docs/publishing/github-pages.html)
- [GitHub Pages Actions 구성](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages)
- [GitHub branch 보호](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches)
