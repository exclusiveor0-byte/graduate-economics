# Migration Note: v1 → v1.1

v1은 한 Chapter 페이지 안에 여러 Section 파일을 `include`하는 구조였습니다.

v1.1에서는 다음과 같이 변경했습니다.

```text
Chapter = Part landing page
Section = standalone qmd page
```

이 변경은 읽기 편의, Section별 URL, Pull Request 리뷰, conflict 감소를 위한 것입니다.

기존 Section 파일 이름과 디렉터리는 유지했기 때문에,
향후 실제 미시경제학 노트 내용을 각 파일에 그대로 이식할 수 있습니다.
