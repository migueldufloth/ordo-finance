# Commit e Push

Analise as mudanças no repositório, gere uma mensagem de commit no padrão Conventional Commits em português e envie ao GitHub.

## Padrão de mensagem

```
<tipo>(<escopo>): <descrição imperativa curta>

[corpo opcional]
```

**Tipos:**
| Tipo | Quando usar |
|---|---|
| `feat` | Nova funcionalidade visível ao usuário |
| `fix` | Correção de bug |
| `refactor` | Refatoração sem mudança de comportamento |
| `test` | Adição ou correção de testes |
| `ci` | Pipelines, workflows, configurações de CI/CD |
| `docs` | Documentação |
| `chore` | Dependências, configurações, builds, migrações |
| `perf` | Melhoria de performance |
| `style` | Formatação pura, sem impacto em lógica |

**Regras obrigatórias:**
- Mensagem em **português com acentuação correta** — Git usa UTF-8 e GitHub exibe corretamente
- Descrição no **imperativo presente**, minúscula, sem ponto final
  - ✅ `corrige cálculo de mês no dashboard`
  - ❌ `Corrigiu cálculo` / `Corrigir cálculo.`
- Primeira linha: **máximo 72 caracteres**
- Corpo: apenas quando o **motivo** não é óbvio pelo diff — nunca descreva o que o código faz, só o porquê
- **Sem** `Co-Authored-By`, sem referências a ferramentas ou IA
- Escopo em minúscula, singular (ex: `model`, `view`, `auth`, `api`, `docker`, `ci`)

**Exemplos:**
```
feat(transacao): adiciona exportação de relatório em PDF
fix(dashboard): corrige cálculo do mês com timezone de São Paulo
refactor(view): extrai base view para cartões e categorias
chore(deps): remove fastapi do requirements do Django
ci: adiciona workflow de lint e testes no GitHub Actions
test(model): adiciona testes unitários para validators de Transacao
```

## Passos de execução

1. `git status` — identifique arquivos modificados, novos e deletados
2. `git diff HEAD` — leia o diff completo para entender as mudanças reais
3. `git log --oneline -5` — verifique o histórico para consistência de estilo
4. Selecione os arquivos a commitar (exclua `.env`, binários, arquivos gerados como `staticfiles/`)
5. `git add <arquivos específicos>` — nunca use `git add .` ou `git add -A`
6. Monte a mensagem seguindo o padrão acima
7. `git commit -m "..."` com a mensagem gerada
8. `git push` para enviar ao GitHub
9. Confirme com `git log --oneline -1`

$ARGUMENTS
