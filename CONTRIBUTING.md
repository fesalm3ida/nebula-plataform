---
tipo: Contribuicao
id: CONTRIBUTING
projeto: Nebula Platform
relacionados:
- '[[CHANGELOG]]'
- '[[PROJECT_STATUS-v2]]'
- '[[PROJECT_STATUS]]'
- '[[README]]'
- '[[RELEASES]]'
tags:
- contribuicao
aliases:
- CONTRIBUTING
---

# Contribuição

## Convenção de commits

- **Assunto e corpo em português.**
- **Prefixo em inglês**, no padrão Conventional Commits, com o escopo da frente
  de trabalho entre parênteses:

  ```
  fix(webos): alcançar o campo de busca com a seta para cima na grade
  feat(webos): ...
  perf(webos): ...
  docs(webos): ...
  ```

  Escopos usados: `webos` (app da LG, `frontend/nebula-tv`), `core` (backend),
  `admin`, `player`.

- **O corpo explica a causa raiz**, não apenas o que mudou. Os commits deste
  projeto registram o sintoma observado (a tela, o log, o que o usuário fez), o
  motivo técnico e o efeito da correção — é o que permite reavaliar a decisão
  meses depois, quando o contexto já não está na cabeça de ninguém.
- **Ao alterar o app da TV**, suba a versão em `frontend/nebula-tv/appinfo.json`
  (o webOS reaproveita o pacote instalado quando a versão não muda) e feche a
  mensagem com a nota de instalação, como nos commits anteriores:
  `Versão elevada para 0.3.8 e instalada na TV.`

## Antes de commitar

```bash
cd frontend/nebula-tv && npm test
```

O app da TV **não** depende de `git push` para funcionar: o pacote é instalado
direto da pasta local pela CLI do webOS (`npm run deploy`). O push serve para
versionar o código no repositório.

