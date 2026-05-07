# SPEC — AutoOpen (GLPI Automation)

> **Versão:** 1.0.0 | **Status:** Ativo | **Última revisão:** 2026-05-06
> Documento vivo — atualize junto com o código. Decisões de implementação **devem** ser validadas aqui primeiro.

---

## TL;DR

**O que:** Automação Python+Playwright que lê uma planilha de logins e cria chamados em lote no GLPI, herdando dados de um chamado-raiz.
**Por quê:** Um técnico precisa abrir dezenas de tickets idênticos para diferentes usuários manualmente. Isso elimina esse trabalho repetitivo.
**Quem:** Técnico de TI abre o `main.py`, preenche o nº do chamado-raiz + seleciona planilha → clica em Iniciar → recebe planilha de resultados.

---

## 1. COMMANDS *(leia antes de qualquer coisa)*

```bash
# --- Setup ---
pip install -r requirements.txt          # instala dependências fixadas
playwright install chromium              # instala navegador headless

# --- Executar ---
python main.py                           # abre interface gráfica

# --- Lint (Ruff) ---
ruff check .                             # verifica erros e violações de estilo
ruff check . --fix                       # corrige automaticamente o que for seguro
ruff format .                            # formata código (substitui black)
ruff format . --check                    # verifica formatação sem alterar

# --- Git ---
git init                                 # apenas na primeira vez
git add .
git commit -m "feat: <descrição>"        # ver Seção 6 para convenção de commits
git log --oneline                        # histórico compacto

# --- Testes (quando implementados) ---
pytest                                   # roda todos os testes
pytest tests/unit/ -v                    # apenas testes unitários
pytest --asyncio-mode=auto               # para testes async (automation.py)
```

**Critério de saída:** Antes de qualquer commit, `ruff check .` deve retornar zero erros.

---

## 2. ESTRUTURA DO PROJETO

```
AutoOpen/
├── main.py             # Interface gráfica (CustomTkinter) — ponto de entrada
├── automation.py       # Núcleo da automação (Playwright + pandas) — sem estado global
├── requirements.txt    # Dependências com versões fixas (incluindo ruff)
├── pyproject.toml      # Configuração do Ruff e ferramentas de dev
├── .env                # Credenciais locais — NUNCA versionado
├── .env.example        # Modelo de configuração — versionado
├── .gitignore          # .env, __pycache__, *.pyc, .playwright/
├── spec.md             # Esta especificação — fonte da verdade
└── readme.md           # Documentação de uso para o técnico
```

**Regra de estrutura:** Projeto flat (sem subpastas de código-fonte). Qualquer crescimento futuro exige discussão — nunca antes de ser necessário.

---

## 3. TECH STACK

| Camada        | Tecnologia              | Versão    | Por quê                                           |
|---------------|-------------------------|-----------|---------------------------------------------------|
| Linguagem     | Python                  | 3.10+     | Compatibilidade ampla, tipagem moderna            |
| Automação Web | Playwright (async)      | 1.51.0    | Controle headless/headed, seletores CSS robustos  |
| Interface     | CustomTkinter           | 5.2.2     | GUI nativa moderna, sem dependência web           |
| Dados         | pandas + openpyxl       | 3.0.1 / 3.1.5 | Leitura/escrita `.xlsx` e `.csv`              |
| Configuração  | python-dotenv           | 1.1.0     | Credenciais fora do código-fonte                  |
| Lint/Format   | ruff                    | 0.9.0+    | Substitui flake8 + isort + black — zero config    |
| Navegador     | Chromium (Playwright)   | —         | Instalado via `playwright install chromium`       |

---

## 4. ESTILO DE CÓDIGO

**Regra:** `ruff check .` com zero erros é condição de merge. Sem exceções.

### Configuração (pyproject.toml)

```toml
[tool.ruff]
line-length = 100
target-version = "py310"

[tool.ruff.lint]
select = ["E", "F", "W", "I", "UP", "B", "C4"]
ignore = ["E501"]  # linha longa: ruff format cuida disso

[tool.ruff.lint.isort]
known-first-party = ["automation"]

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
```

### Convenções de nomenclatura

| Contexto | Estilo | Exemplo |
|---|---|---|
| Funções utilitárias genéricas | inglês, snake_case | `_wait_and_fill`, `_read_selected_option` |
| Funções de domínio | português, snake_case | `_ler_chamado_raiz`, `_criar_chamado_filho` |
| Variáveis de negócio | português | `requerente`, `localizacao`, `categoria` |
| Seletores CSS longos | constante UPPER_SNAKE | `SEL_REQUERENTE`, `SEL_OBSERVADOR` |
| Funções internas ao módulo | prefixo `_` | `_login`, `_fill_autocomplete` |
| API pública de automation.py | sem prefixo | `executar_automacao` |

### Exemplo canônico (tom de referência)

```python
SEL_REQUERENTE = "input[name='_users_id_requester']"

async def _fill_autocomplete(page: Page, selector: str, value: str) -> None:
    """Preenche um campo de autocomplete do GLPI: fill → Enter."""
    await page.fill(selector, value)
    await page.keyboard.press("Enter")
    await page.wait_for_timeout(500)
```

---

## 5. GIT WORKFLOW

### Configuração inicial

```bash
git init
echo ".env" >> .gitignore
echo "__pycache__/" >> .gitignore
echo "*.pyc" >> .gitignore
echo "chamados_criados_*.xlsx" >> .gitignore   # saídas geradas não vão ao repo
git add .
git commit -m "chore: estrutura inicial do projeto"
```

### Convenção de commits (Conventional Commits)

```
feat:     nova funcionalidade
fix:      correção de bug
refactor: refatoração sem mudança de comportamento
chore:    dependências, config, CI
docs:     spec.md, readme.md, comentários
test:     adição ou ajuste de testes
```

**Exemplos:**
```
feat: adicionar detecção flexível de coluna de login (R7)
fix: corrigir timeout em criação de chamado filho
docs: atualizar spec com fase 2 — retry automático
```

### Tamanho de PR / commit

- Cada commit faz **uma coisa** (atômico e revisável).
- PRs > 200 linhas precisam justificativa. Prefira dividir em commits menores.
- Nunca commitar `.env` ou credenciais.
- `ruff check .` passa antes do `git commit`.

### Branches (quando trabalhar com equipe)

```
main          → código estável, pronto para uso
feat/<nome>   → nova funcionalidade (ex: feat/retry-automatico)
fix/<nome>    → correção (ex: fix/timeout-chamado-filho)
```

---

## 6. BOUNDARIES (Limites de Atuação do Agente)

### ✅ Sempre fazer (sem perguntar)

- Rodar `ruff check .` antes de qualquer commit
- Manter `_` em funções internas do módulo
- Capturar erros por chamado individualmente — nunca abortar o lote
- Gerar planilha de resultados ao final, mesmo que todos os chamados falhem
- Extrair **apenas** a coluna de login da planilha de entrada (descartar todo o resto)
- Atualizar `spec.md` quando uma decisão de design for tomada
- Usar `self.after(0, callback)` para qualquer atualização de UI a partir de thread de background

### ⚠️ Perguntar primeiro (requer aprovação humana)

- Adicionar nova dependência ao `requirements.txt`
- Alterar o comportamento de `executar_automacao()` (API pública)
- Mudar a estrutura de colunas da planilha de saída
- Adicionar subpastas ao projeto (viola regra de estrutura flat)
- Alterar `pyproject.toml` (configuração de lint afeta toda a equipe)
- Modificar `.env.example` (pode quebrar instalações existentes)

### 🚫 Nunca fazer

- Commitar `.env` ou qualquer credencial
- Criar estado global mutável em `automation.py` (é funcional e assim fica)
- Interromper o loop de criação por falha individual de chamado
- Transportar dados além de `Login` e `Chamados` para a planilha de saída
- Adicionar classes em `automation.py` (módulo funcional por decisão de design)
- Silenciar exceções sem logar (`except: pass` é proibido)
- Recarregar `.env` em runtime (variáveis são lidas uma vez na inicialização)

---

## 7. VISÃO DO PRODUTO

### Problema

Um técnico de TI recebe um chamado-raiz onde alguém (requerente) solicita criação de acessos para N colaboradores. Hoje, o técnico abre cada chamado filho **manualmente** no GLPI. Para 50 usuários = 50 formulários = ~2h de trabalho repetitivo.

### Solução

AutoOpen lê uma planilha de logins e cria todos os chamados automaticamente, herdando os dados do ticket original.

### Critérios de Sucesso

| # | Critério | Como verificar |
|---|---|---|
| S1 | N chamados criados a partir de 1 raiz | Planilha de saída tem N linhas sem `"ERRO"` |
| S2 | Dados do raiz herdados automaticamente | Campos iguais ao raiz quando UI está em branco |
| S3 | Requerente do raiz mantido em todos os filhos | Campo requerente idêntico em cada chamado filho |
| S4 | Usuários da planilha adicionados como observadores | Campo observador preenchido no GLPI |
| S5 | Planilha `.xlsx` com Login × Nº do Chamado gerada | Arquivo existe, abre sem erro, tem 2 colunas |
| S6 | UI não trava durante execução | Log atualiza em tempo real, botões respondem |
| S7 | Erros individuais não interrompem o lote | Chamado com falha → `"ERRO"` na planilha; próximo executa |

---

## 8. FLUXO PRINCIPAL (Workflow com Critérios de Saída)

### Fase A — Entrada do Usuário

```
Técnico abre main.py
  → .env lido → status verde/vermelho no cabeçalho
  → Preenche: Nº Chamado Raiz (obrigatório) + campos opcionais
  → Seleciona planilha .xlsx/.csv com coluna Login/Rede/Usuário
  → Clica em ▶ INICIAR AUTOMAÇÃO
```

**Critério de saída:** `chamado_raiz` preenchido E `planilha_path` apontando para arquivo existente.

### Fase B — Preparação (automation.py)

```
_ler_planilha()
  → Detecta coluna de login (case-insensitive: Login, Rede, Usuário...)
  → Extrai lista de logins — descarta todas as outras colunas
  → Valida: lista não vazia

_login()
  → Abre Chromium (headed ou headless via GLPI_HEADLESS)
  → Autentica com GLPI_TECNICO_LOGIN / GLPI_TECNICO_SENHA
```

**Critério de saída:** Chromium autenticado + lista de logins em memória.

### Fase C — Extração do Chamado Raiz

```
_ler_chamado_raiz(chamado_id)
  → Navega para URL do chamado raiz
  → Extrai: título, descrição, categoria, localização, requerente
  → Mescla com params da UI (UI sobrescreve se preenchido)
```

**Critério de saída:** Dict com todos os campos preenchidos (raiz ou UI).

### Fase D — Loop de Criação (por login)

```
Para cada login na lista:
  try:
    _criar_chamado_filho(login, dados_mesclados)
      → Abre formulário de novo chamado
      → Preenche: título, requerente (do raiz), observador (login), categoria, localização, descrição, técnico
      → Submete
      → Captura nº do chamado (via URL ou DOM)
      → Registra: {"Login": login, "Chamados": numero}
  except Exception as e:
    log("❌ Erro em login {login}: {e}")
    registra: {"Login": login, "Chamados": "ERRO"}
    continua para o próximo   # ← regra R4, nunca abortar
```

**Critério de saída:** Lista de resultados com N entradas (uma por login).

### Fase E — Saída

```
_salvar_resultados(resultados)
  → Gera chamados_criados_YYYYMMDD_HHMMSS.xlsx
  → Colunas: Login | Chamados
  → Colunas auto-ajustadas

main.py exibe messagebox com resumo (X criados, Y erros)
```

**Critério de saída:** Arquivo `.xlsx` existe no disco com 2 colunas.

---

## 9. REGRAS DE DOMÍNIO

| ID | Regra | Verificação |
|----|-------|-------------|
| R1 | **Requerente único:** herdado do chamado raiz (ou sobrescrito pela UI). Nunca vem da planilha. | Campo requerente = raiz em todos os filhos |
| R2 | **Observador = login da planilha.** Não é o requerente. | Campo observador = login processado |
| R3 | **Herança de campos:** UI vazia → valor do raiz. UI preenchida → sobrescreve. | Cada campo verificado individualmente |
| R4 | **Tolerância a falhas:** falha individual → `"ERRO"` no resultado → loop continua. | Lote nunca aborta por falha única |
| R5 | **Planilha de saída sempre gerada**, mesmo se todos falharem. | Arquivo existe ao final |
| R6 | **Apenas coluna de login transita.** Nenhum dado extra da entrada vai para saída ou GLPI. | Planilha de saída tem exatamente 2 colunas |
| R7 | **Detecção flexível de coluna:** `Login`, `Rede`, `Usuário` (qualquer casing). | `ValueError` se nenhuma coluna reconhecida |

---

## 10. CONTRATOS DAS FUNÇÕES PRINCIPAIS

```python
# API pública — único ponto de entrada de automation.py
async def executar_automacao(
    params: dict,           # ver modelo abaixo
    log_fn: Callable[[str], None],    # callback de log para a UI
    progress_fn: Callable[[int, int], None],  # callback de progresso (atual, total)
) -> str:                   # retorna caminho do arquivo .xlsx gerado
    ...

# Helpers internos (prefixo _)
async def _login(page: Page) -> None
async def _ler_chamado_raiz(page: Page, chamado_id: str) -> dict
async def _criar_chamado_filho(page: Page, login: str, dados: dict) -> str  # retorna nº chamado
async def _fill_autocomplete(page: Page, selector: str, value: str) -> None
async def _read_selected_option(page: Page, selector: str) -> tuple[str, str]  # (texto, value)
async def _set_select(page: Page, selector: str, value: str) -> None
def _detectar_coluna_login(colunas: list[str]) -> str   # retorna nome da coluna ou ValueError
def _ler_planilha(path: str) -> list[str]               # retorna lista de logins
def _salvar_resultados(resultados: list[dict]) -> str   # retorna caminho do .xlsx
```

---

## 11. MODELOS DE DADOS

### params (entrada para executar_automacao)

```python
params = {
    "chamado_raiz":  str,   # obrigatório — ID do ticket pai
    "requerente":    str,   # opcional — sobrescreve o do raiz se preenchido
    "titulo":        str,   # opcional — sobrescreve o do raiz se preenchido
    "descricao":     str,   # opcional — sobrescreve o do raiz se preenchido
    "localizacao":   str,   # opcional — sobrescreve o do raiz se preenchido
    "categoria":     str,   # opcional — sobrescreve o do raiz se preenchido
    "planilha_path": str,   # obrigatório — caminho do arquivo .xlsx/.csv
    "saida_dir":     str,   # opcional — pasta onde salvar a planilha de saída (padrão: mesma de entrada)
}
```

### Planilha de entrada (qualquer número de colunas — apenas login é usado)

| Nome Completo | CPF | **Rede** | Setor | E-mail |
|---|---|---|---|---|
| João da Silva | 123... | joao.silva | Financeiro | joao@... |

→ Sistema extrai apenas `["joao.silva", ...]` da coluna `Rede`.

**Nomes aceitos para coluna de login** (case-insensitive):
`Login`, `login`, `LOGIN`, `Rede`, `REDE`, `rede`, `Usuário`, `usuário`, `USUÁRIO`

### Planilha de saída (sempre 2 colunas, nunca mais)

| Login | Chamados |
|---|---|
| joao.silva | 4521 |
| maria.santos | ERRO |

### .env (variáveis de ambiente)

| Variável | Obrigatória | Default | Descrição |
|---|---|---|---|
| `GLPI_URL` | ✅ | — | URL base sem `/` final |
| `GLPI_TECNICO_LOGIN` | ✅ | — | Login do técnico |
| `GLPI_TECNICO_SENHA` | ✅ | — | Senha do técnico |
| `GLPI_HEADLESS` | ❌ | `false` | Modo headless (`true`/`false`) |
| `GLPI_TIMEOUT` | ❌ | `30000` | Timeout em ms para Playwright |

---

## 12. TESTES

### Estado atual: Sem testes automatizados

### Estratégia por fase

| Fase | O que testar | Ferramentas |
|------|-------------|-------------|
| **Unitário** (Fase 1) | `_detectar_coluna_login`, `_ler_planilha`, `_salvar_resultados`, `_extrair_numero_chamado` | `pytest`, dados em memória |
| **Integração** (Fase 2) | `executar_automacao` com GLPI de homologação | `pytest-asyncio`, Playwright headed |
| **Manual** | Fluxo completo via interface gráfica | Checklist abaixo |

### Checklist de aceite manual

- [ ] Login no GLPI funciona
- [ ] Dados do chamado raiz são extraídos corretamente
- [ ] Chamados filhos criados com requerente correto (R1)
- [ ] Usuários da planilha aparecem como observadores (R2)
- [ ] Campos opcionais herdados do raiz quando UI em branco (R3)
- [ ] Erro individual não aborta o lote (R4)
- [ ] Planilha de resultados gerada mesmo com todos os erros (R5)
- [ ] Planilha de saída tem **exatamente** 2 colunas (R6)
- [ ] Coluna de login detectada com nomes variados/casing (R7)
- [ ] Interface não trava durante execução

---

## 13. ANTI-RACIONALIZAÇÃO

*Estes são os atalhos que parecem razoáveis mas não são. Pré-refutações para decisões ruins.*

| Racionalização | Por que está errada | Ação correta |
|---|---|---|
| "Esse campo é simples, não preciso de try/except individual." | R4 existe exatamente para campos simples. Um timeout numa campo é suficiente para derrubar o chamado. | Envolva cada campo com `try/except` e log `⚠️`. |
| "Vou transportar o nome do usuário para a planilha de saída — é útil." | Viola R6 explicitamente. Dados além de Login/Chamados nunca transitam. | A saída tem **exatamente** 2 colunas. Ponto. |
| "Vou adicionar uma classe em automation.py para organizar melhor." | O módulo é funcional por decisão arquitetural deliberada. Adicionar classe = alterar contrato da API. | Boundaries: 🚫 Nunca. Se precisar discutir, atualize a spec primeiro. |
| "O ruff está passando em tudo, posso pular o `--fix` desta vez." | O `--check` apenas verifica. Sem `--fix`, o código pode ainda ter formatação inconsistente. | `ruff check . --fix && ruff format .` sempre juntos antes do commit. |
| "Este commit é pequeno, não precisa de mensagem convencional." | Commits pequenos sem convenção acumulam e tornam `git log` ilegível. | Sempre use `feat:`, `fix:`, `chore:` etc. Leva 5 segundos. |
| "O lote está quase terminando, vou abortar para economizar tempo." | R4 é absoluto. O técnico precisa da planilha de resultados completa. | Registre `"ERRO"` e continue. A planilha incompleta é pior que lenta. |
| "Posso salvar o `.env` no git — ninguém vai ver." | Credenciais no git são permanentes (mesmo após remoção via `git rm`). | `.gitignore` tem `.env`. Nunca, sob nenhuma circunstância. |

---

## 14. ROADMAP POR FASE (Gated)

> Não avançar para a próxima fase sem validar os critérios de saída da atual.

### Fase 0 — Fundação

- [ ] Estrutura de arquivos flat
- [x] Interface gráfica CustomTkinter (dark mode, campos, log, progresso)
- [x] Leitura `.xlsx`/`.csv`
- [ ] Automação Playwright (login, leitura de raiz, criação de filhos)
- [ ] Geração planilha de resultados
- [ ] Refatoração e eliminação de duplicação

**Critério de saída:** Fluxo completo manual funciona end-to-end.

### Fase 1 — Validação *(em andamento)*

- [ ] Implementar `_detectar_coluna_login()` — mapeamento case-insensitive (R7)
- [ ] Adicionar ruff ao projeto (`pyproject.toml` + `requirements.txt`)
- [ ] Inicializar repositório git com `.gitignore` correto
- [ ] Testar com GLPI real (homologação) — 5 a 10 usuários
- [ ] Ajustar seletores CSS para versão do GLPI em uso
- [ ] Tratar edge cases: login inexistente, chamado raiz inválido, planilha vazia

**Critério de saída:** Checklist de aceite manual 100% ✅ + `ruff check .` = zero erros.

### Fase 2 — Robustez

- [ ] Retry automático (1–2 tentativas antes de marcar `"ERRO"`)
- [ ] Log salvo em arquivo `.log` além da interface
- [ ] Botão de cancelamento durante execução

**Critério de saída:** Teste de estresse com 50 usuários sem degradação de UI.

### Fase 3 — Evolução

- [ ] Vincular chamados filhos ao chamado raiz (link pai-filho no GLPI)
- [ ] Suporte a colunas extras opcionais (`Nome`, `Setor` → enriquecer descrição)
- [ ] Modo batch via CLI sem interface gráfica (`cli.py` com `argparse`)
- [ ] Suporte a Select2 (GLPI 10+) — seletores `.select2-results__option`

**Critério de saída:** Cada item tem seu próprio PR atômico com teste de aceitação.

---

## 15. O QUE O SISTEMA NÃO FAZ (e por quê)

| Limite | Justificativa |
|---|---|
| Não vincula chamados pai-filho | GLPI exige navegação extra para links entre tickets. Complexidade não justificada agora. |
| Não altera chamados existentes | Escopo é apenas criação. Alterar tickets existentes é outro problema. |
| Não gerencia sessão/cookies | Login do zero a cada execução. Simples e confiável. |
| Não valida logins contra o GLPI | O autocomplete do GLPI faz isso. Campo fica vazio se login inexistir. |
| Não suporta 2FA / SSO | Apenas formulário padrão do GLPI. |
| Não recarrega `.env` em runtime | Variáveis lidas uma vez na inicialização. Alterar exige reiniciar. |

---

## 16. SELF-CHECK (antes de qualquer alteração)

Execute esta lista mentalmente antes de submeter código:

- [ ] `ruff check .` retorna zero erros?
- [ ] A mudança respeita R1 (requerente único)?
- [ ] Usuários da planilha continuam sendo observadores (R2)?
- [ ] Campos opcionais ainda herdam do raiz se vazios (R3)?
- [ ] Erros individuais **não** interrompem o lote (R4)?
- [ ] Planilha de resultados **sempre** gerada (R5)?
- [ ] Dados extras da entrada **não** vazam para saída ou GLPI (R6)?
- [ ] Coluna de login detectada com nomes variados (R7)?
- [ ] UI continua responsiva (thread separada + `self.after(0, ...)`)?
- [ ] Nenhum import desnecessário adicionado?
- [ ] Lógica duplicada foi extraída para helper?
- [ ] Seletores CSS longos estão em constantes nomeadas?
- [ ] O commit segue a convenção (`feat:`, `fix:`, etc.)?
- [ ] `.env` não está no staging (`git status` verificado)?