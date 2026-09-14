# 첫날 협업 가이드

Git을 깊게 배울 필요는 없습니다. 아래 여섯 동작만 익히면 됩니다.

1. **main → Fetch origin → Pull origin** (Pull 버튼이 나타날 때)
2. **New Branch**
3. **Edit**
4. **Commit**
5. **Push**
6. **Create Pull Request**

## 설치

- GitHub Desktop
- VS Code
- Quarto

## 첫 연습

처음에는 오탈자 하나를 수정하는 연습을 권장합니다.

1. GitHub Desktop으로 repository clone
2. main에서 **Fetch origin**, 필요하면 **Pull origin** 후 `practice/이름` branch 생성
3. 작은 문장 하나 수정
4. commit
5. push
6. Pull Request 생성
7. Actions 초록 체크 확인

## 터미널은 선택사항

이 프로젝트의 일반적인 문서 수정에는 터미널 명령을 요구하지 않습니다.

설치 없이 오탈자 하나를 고치려면 GitHub 웹에서 `.qmd` 파일의 연필 버튼을 누릅니다.
**Commit changes → Create a new branch for this commit and start a pull request**를 선택한 뒤 제안 내용을 적습니다.
본문이 길거나 수식을 수정할 때는 GitHub Desktop과 VS Code 미리보기를 사용하세요.

## 초록 체크 다음에 할 일

- PR의 **Files changed**에서 의도한 Section만 바뀌었는지 확인합니다.
- 초록 체크는 페이지·링크·블록 구조를 검사합니다. 경제학 내용은 리뷰어가 별도로 확인합니다.
- 렌더 결과는 Actions 실행 화면의 **Artifacts → book-preview**에서 받을 수 있습니다.
- merge 후 **main → Fetch origin → Pull origin**으로 돌아옵니다.
- 공개 웹사이트 반영은 **Publish Quarto Book**의 build와 deploy가 모두 성공하면 완료됩니다.

## 문제가 생기면

직접 Git history를 복구하려고 하기보다:
- 수정 내용을 먼저 보존하고, 버려도 되는 변경만 취소
- 이미 push했다면 Maintainer에게 PR 링크 전달
- merge conflict가 보이면 임의로 해결하지 말고 Maintainer와 함께 처리
