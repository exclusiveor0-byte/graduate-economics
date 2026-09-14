# Writing & Formatting Guide

## 기본 구조

Section은 독립 페이지이므로 파일의 `#` 제목 또는 YAML `title`로 시작합니다.
Chapter의 `index.qmd`는 개요와 Section 링크를 담습니다. 기존 제목 번호는 그대로 유지합니다.

```markdown
# 1.4 간접효용과 지출
```

## 의미 블록

### Definition / Assumption
```markdown
::: {.callout-note title="Definition"}
내용
:::
```

### Theorem / Proposition / Lemma
```markdown
::: {.callout-important title="Proposition"}
내용
:::
```

### Proof
```markdown
::: {.callout-tip collapse="true" title="Proof"}
내용
:::
```

### Remark
```markdown
::: {.callout-note appearance="simple" title="Remark"}
내용
:::
```

### Caution / Boundary Case
```markdown
::: {.callout-caution title="Caution"}
내용
:::
```

## 수식

Display math:

```text
$$
u(x_1,x_2)=x_1^\alpha x_2^{1-\alpha}
$$
```

Inline math:

```text
$u(x)$
```

## 표기

- 한 Section 안에서 notation을 임의로 바꾸지 않습니다.
- 기존 Chapter의 notation을 먼저 확인합니다.
- 다른 Chapter와 충돌하는 표기가 필요하면 PR 설명에 적습니다.
