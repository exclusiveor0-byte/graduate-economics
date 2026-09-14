# v1.1 Architecture

## 핵심 결정

**Chapter는 Part landing page, Section은 독립 페이지**로 구성합니다.

```text
Book
├─ Microeconomics overview
├─ Chapter 0 (Part / landing page)
│  ├─ 0.1 independent page
│  ├─ 0.2 independent page
│  └─ ...
├─ Chapter 1 (Part / landing page)
│  ├─ 1.1 independent page
│  └─ ...
```

## 왜 Section을 독립 페이지로 두는가

- Section별 URL을 가질 수 있음
- 특정 Section을 직접 공유하기 쉬움
- Section별 Pull Request가 가능함
- 여러 사람이 한 Chapter를 동시에 수정할 때 conflict가 줄어듦
- 긴 Chapter 전체를 다시 렌더링하며 탐색할 필요가 없음

## 번호 체계

Quarto 자동 chapter numbering은 사용하지 않습니다.

기존 정리노트의 `0.1`, `1.4`, `4.6` 같은 번호를 **페이지 제목 자체에 보존**합니다.
이는 기존 노트의 논리적 구조와 인용 습관을 유지하기 위한 선택입니다.

## 역할

### Maintainer
- repository 구조 관리
- `_quarto.yml` 관리
- GitHub Actions 관리
- 최종 merge
- conflict 처리

### Contributors
- Section 작성/수정
- Supplement 작성
- Pull Request 제출
- 리뷰 참여
