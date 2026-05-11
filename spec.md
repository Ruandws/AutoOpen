# AutoOpen — Especificação do Projeto

> **Versão:** 1.1.0 | **Status:** Ativo | **Última revisão:** 2026-05-11
> Documento vivo — atualize junto com o código. Decisões de design **devem** ser registradas aqui primeiro.
> Antes de qualquer sessão de agente, injete as seções 1–5. Injete as demais sob demanda.

---

## TL;DR

**O que:** Automação Python + Playwright que lê uma planilha de logins e cria chamados em lote no GLPI, herdando dados de um chamado-raiz.
**Por quê:** Um técnico abre dezenas de tickets idênticos para usuários diferentes. AutoOpen elimina esse trabalho repetitivo.
**Quem:** Técnico de TI → `python main.py` → preenche chamado-raiz + seleciona planilha → clica Iniciar → recebe planilha de resultados.

---

## 1. COMMANDS *(leia e execute primeiro — sempre)*

```bash
# ── Setup ──────────────────────────────────────────────────────
pip install -r requirements.txt          # instala dependências fixadas
playwright install chromium              # instala navegador headless

# ── Executar ───────────────────────────────────────────────────
python main.py                           # abre interface gráfica

# ── Lint / Format (obrigatório antes de qualquer commit) ───────
ruff check .                             # verifica erros e violações
ruff check . --fix                       # corrige o que for seguro
ruff format .                            # formata código
ruff format . --check                    # verifica formatação sem alterar

# ── Git ────────────────────────────────────────────────────────
git init                                 # apenas na primeira vez
git status                               # confirme que .env NÃO aparece
git add .
git commit -m "feat: <descrição curta>"  # ver Seção 10 para convenções
git log --oneline                        # histórico compacto

# ── Testes ─────────────────────────────────────────────────────
pytest                                   # todos os testes
pytest tests/unit/ -v                    # apenas unitários
pytest --asyncio-mode=auto               # testes async (automation.py)
```

**Gate de saída desta seção:** `ruff check .` retorna zero erros. Sem isso, nenhum commit acontece.

---

## 2. BOUNDARIES *(a regra mais importante do projeto)*

### ✅ Sempre fazer (sem perguntar)
- Rodar `ruff check . --fix && ruff format .` antes de qualquer commit
- Manter prefixo `_` em funções internas do módulo
- Capturar erros **por chamado** individualmente — nunca abortar o lote inteiro
- Gerar planilha de resultados ao final, mesmo que todos os chamados falhem
- Extrair **apenas** a coluna de login da planilha de entrada; descartar o resto
- Atualizar `spec.md` quando uma decisão de design for tomada
- Usar `self.after(0, callback)` para qualquer atualização de UI a partir de thread de background
- Verificar `git status` antes de `git add` para confirmar que `.env` não está staged

### ⚠️ Perguntar primeiro (requer aprovação humana)
- Adicionar nova dependência ao `requirements.txt`
- Alterar assinatura ou comportamento de `executar_automacao()` (API pública)
- Mudar estrutura de colunas da planilha de saída
- Adicionar subpastas ao projeto (viola regra de estrutura flat)
- Alterar `pyproject.toml` (configuração de lint afeta toda a equipe)
- Modificar `.env.example` (pode quebrar instalações existentes)

### 🚫 Nunca fazer (hard stops)
- Commitar `.env` ou qualquer credencial — permanente no histórico, mesmo após `git rm`
- Criar estado global mutável em `automation.py` — módulo é funcional e permanece assim
- Interromper o loop de criação por falha individual de chamado
- Transportar dados além de `Login` e `Chamados` para a planilha de saída
- Adicionar classes em `automation.py` — decisão arquitetural deliberada
- Silenciar exceções sem logar (`except: pass` é proibido)
- Recarregar `.env` em runtime — variáveis são lidas uma vez na inicialização
- Refatorar arquivos adjacentes quando a tarefa não pede isso

---

## 3. CINCO NÃO-NEGOCIÁVEIS

> Estes se aplicam a qualquer agente ou engenheiro que toque neste projeto.
> Não são negociáveis, não têm exceções, não aceitam racionalizações.

1. **Exponha suposições antes de construir.** Suposições silenciosas são a causa mais comum de retrabalho.
2. **Pare e pergunte quando requisitos conflitam.** Não adivinhe entre dois caminhos — peça clareza.
3. **Prefira a solução óbvia e chata.** Elegância desnecessária é dívida técnica disfarçada.
4. **Toque apenas o que foi pedido.** Refatorar arquivos adjacentes não é bonus — é risco.
5. **Deixe evidência de que o trabalho está correto.** "Parece certo" nunca fecha o loop. Testes passando, ou log de execução, ou checklist manual — escolha um, use-o.

---

## 4. PROJETO

### 4.1 Estrutura (flat — sem exceções)

```
AutoOpen/
├── main.py             # Interface gráfica (CustomTkinter) — ponto de entrada
├── automation.py       # Núcleo da automação (Playwright + pandas) — sem estado global
├── requirements.txt    # Dependências com versões fixas (incluindo ruff)
├── pyproject.toml      # Configuração do ruff e ferramentas de dev
├── .env                # Credenciais locais — NUNCA versionado
├── .env.example        # Modelo de configuração — versionado
├── .gitignore          # .env, __pycache__, *.pyc, .playwright/, saídas geradas
├── spec.md             # Esta especificação — fonte da verdade
└── readme.md           # Documentação de uso para o técnico
```

> Regra: qualquer crescimento (nova pasta, novo módulo) exige discussão e atualização do spec antes da implementação.

### 4.2 Stack

| Camada        | Tecnologia              | Versão        | Por quê                                          |
|---------------|-------------------------|---------------|--------------------------------------------------|
| Linguagem     | Python                  | 3.10+         | Compatibilidade ampla, tipagem moderna           |
| Automação Web | Playwright (async)      | 1.51.0        | Controle headless/headed, seletores CSS robustos |
| Interface     | CustomTkinter           | 5.2.2         | GUI nativa moderna, sem dependência web          |
| Dados         | pandas + openpyxl       | 3.0.1 / 3.1.5 | Leitura/escrita `.xlsx` e `.csv`                 |
| Configuração  | python-dotenv           | 1.1.0         | Credenciais fora do código-fonte                 |
| Lint/Format   | ruff                    | 0.9.10+       | Substitui flake8 + isort + black — zero config   |
| Navegador     | Chromium (Playwright)   | —             | Instalado via `playwright install chromium`      |

### 4.3 Estilo de Código

**Critério de merge:** `ruff check .` com zero erros. Sem exceções.

**Convenções de nomenclatura:**

| Contexto                       | Estilo              | Exemplo                              |
|--------------------------------|---------------------|--------------------------------------|
| Funções utilitárias genéricas  | inglês, snake_case  | `_wait_and_fill`, `_read_selected_option` |
| Funções de domínio             | português, snake_case | `_ler_chamado_raiz`, `_criar_chamado_filho` |
| Variáveis de negócio           | português           | `requerente`, `localizacao`, `categoria` |
| Seletores CSS longos           | constante UPPER_SNAKE | `SEL_REQUERENTE`, `SEL_OBSERVADOR`  |
| Funções internas ao módulo     | prefixo `_`         | `_login`, `_fill_autocomplete`       |
| API pública de automation.py   | sem prefixo         | `executar_automacao`                 |

**Exemplo canônico — um snippet vale mais que três parágrafos:**

```python
SEL_REQUERENTE = "input[name='_users_id_requester']"

async def _fill_autocomplete(page: Page, selector: str, value: str) -> None:
    """Preenche um campo de autocomplete do GLPI: fill → Enter."""
    await page.fill(selector, value)
    await page.keyboard.press("Enter")
    await page.wait_for_timeout(500)
```

---

## 5. VISÃO DO PRODUTO

### Problema
Técnico recebe chamado-raiz de N colaboradores precisando de acesso. Hoje, abre cada chamado filho **manualmente** no GLPI. Para 50 usuários ≈ 2h de formulários repetitivos.

### Solução
AutoOpen lê planilha de logins e cria todos os chamados automaticamente, herdando os dados do ticket original.

### Critérios de Sucesso (verificáveis)

| ID | Critério                                              | Como verificar                                      |
|----|-------------------------------------------------------|-----------------------------------------------------|
| S1 | N chamados criados a partir de 1 raiz                 | Planilha de saída tem N linhas sem `"ERRO"`         |
| S2 | Dados do raiz herdados automaticamente                | Campos iguais ao raiz quando UI está em branco      |
| S3 | Requerente do raiz mantido em todos os filhos         | Campo requerente idêntico em cada chamado filho     |
| S4 | Usuários da planilha adicionados como observadores    | Campo observador preenchido no GLPI                 |
| S5 | Planilha `.xlsx` com Login × Nº do Chamado gerada     | Arquivo existe, abre sem erro, tem exatamente 2 colunas |
| S6 | UI não trava durante execução                         | Log atualiza em tempo real, botões respondem        |
| S7 | Erros individuais não interrompem o lote              | Chamado com falha → `"ERRO"`; próximo executa       |

---

## 6. WORKFLOW *(processo, não prosa — cada fase tem gate de saída)*

### Fase A — Entrada do Usuário

**Passos:**
1. Técnico abre `main.py`
2. `.env` é lido na inicialização → status verde/vermelho no cabeçalho da UI
3. Preenche: **Nº Chamado Raiz** (obrigatório) + campos opcionais
4. Seleciona planilha `.xlsx` ou `.csv` com coluna de login
5. Clica em ▶ **INICIAR AUTOMAÇÃO**

**Gate de saída — evidência exigida:**
- [ ] `chamado_raiz` não está vazio
- [ ] `planilha_path` aponta para arquivo existente no disco
- Sem os dois: botão Iniciar permanece desabilitado

---

### Fase B — Preparação

**Passos:**
1. `_ler_planilha(path)` detecta coluna de login (case-insensitive: `Login`, `Rede`, `Usuário`)
2. Extrai lista de logins — descarta todas as outras colunas
3. Valida: lista não vazia → se vazia, loga erro e encerra com planilha de resultados vazia
4. `_login()` abre Chromium (headed ou headless via `GLPI_HEADLESS`)
5. Autentica com `GLPI_TECNICO_LOGIN` / `GLPI_TECNICO_SENHA`

**Gate de saída — evidência exigida:**
- [ ] Chromium autenticado (página pós-login visível no DOM)
- [ ] Lista de logins em memória com pelo menos 1 entrada
- [ ] `ValueError` lançado (e logado) se nenhuma coluna reconhecida (R7)

---

### Fase C — Extração do Chamado Raiz

**Passos:**
1. `_ler_chamado_raiz(chamado_id)` navega para URL do chamado raiz
2. Extrai: título, descrição, categoria, localização, requerente
3. Mescla com `params` da UI: **UI sobrescreve se preenchido; raiz preenche se vazio**

**Gate de saída — evidência exigida:**
- [ ] Dict retornado com todos os campos (nenhum campo `None` sem fallback)
- [ ] Requerente extraído do raiz está presente (R1)

---

### Fase D — Loop de Criação *(núcleo da automação)*

**Passos por login:**

```
Para cada login na lista:
  try:
    _criar_chamado_filho(login, dados_mesclados)
      1. Abre formulário de novo chamado
      2. Preenche: título, requerente (do raiz), observador (login atual),
                   categoria, localização, descrição, técnico
      3. Submete formulário
      4. Captura nº do chamado (URL ou DOM)
      5. Registra: {"Login": login, "Chamados": numero}
  except Exception as e:
      log(f"❌ Erro em {login}: {e}")
      Registra: {"Login": login, "Chamados": "ERRO"}
      continua para o próximo  # ← R4: nunca abortar o lote
```

**Gate de saída — evidência exigida:**
- [ ] Lista de resultados com exatamente N entradas (uma por login)
- [ ] Nenhuma exceção não capturada propagada para fora do loop
- [ ] Log visível na UI para cada login processado (sucesso ou erro)

---

### Fase E — Saída

**Passos:**
1. `_salvar_resultados(resultados)` gera `chamados_criados_YYYYMMDD_HHMMSS.xlsx`
2. Colunas: `Login` | `Chamados` — apenas estas, nunca mais
3. Colunas com largura auto-ajustada
4. `main.py` exibe messagebox: "X criados, Y erros"

**Gate de saída — evidência exigida:**
- [ ] Arquivo `.xlsx` existe no disco (verificável por `os.path.exists`)
- [ ] Arquivo tem exatamente 2 colunas (R6)
- [ ] Arquivo gerado mesmo quando todos os chamados retornaram `"ERRO"` (R5)

---

## 7. REGRAS DE DOMÍNIO *(invariantes — não negociáveis)*

| ID | Regra                                                                              | Verificação                             |
|----|------------------------------------------------------------------------------------|-----------------------------------------|
| R1 | **Requerente único:** herdado do chamado raiz (ou sobrescrito pela UI). Nunca vem da planilha. | Campo requerente = raiz em todos os filhos |
| R2 | **Observador = login da planilha.** Não é o requerente.                            | Campo observador = login processado     |
| R3 | **Herança de campos:** UI vazia → valor do raiz. UI preenchida → sobrescreve.      | Cada campo verificado individualmente   |
| R4 | **Tolerância a falhas:** falha individual → `"ERRO"` → loop continua.             | Lote nunca aborta por falha única       |
| R5 | **Planilha de saída sempre gerada**, mesmo se todos falharem.                      | Arquivo existe ao final                 |
| R6 | **Apenas coluna de login transita.** Nenhum dado extra vai para saída ou GLPI.    | Planilha de saída tem exatamente 2 colunas |
| R7 | **Detecção flexível de coluna:** `Login`, `Rede`, `Usuário` (qualquer casing).    | `ValueError` se nenhuma coluna reconhecida |

---

## 8. CONTRATOS DAS FUNÇÕES

```python
# API pública — único ponto de entrada de automation.py
async def executar_automacao(
    params: dict,                              # ver Seção 9 para modelo
    log_fn: Callable[[str], None],             # callback de log para a UI
    progress_fn: Callable[[int, int], None],   # callback de progresso (atual, total)
) -> str:                                      # retorna caminho do .xlsx gerado
    ...

# Helpers internos (prefixo _)
async def _login(page: Page) -> None
async def _ler_chamado_raiz(page: Page, chamado_id: str) -> dict
async def _criar_chamado_filho(page: Page, login: str, dados: dict) -> str   # → nº chamado
async def _fill_autocomplete(page: Page, selector: str, value: str) -> None
async def _read_selected_option(page: Page, selector: str) -> tuple[str, str]  # (texto, value)
async def _set_select(page: Page, selector: str, value: str) -> None
def _detectar_coluna_login(colunas: list[str]) -> str    # → nome da coluna ou ValueError
def _ler_planilha(path: str) -> list[str]                # → lista de logins
def _salvar_resultados(resultados: list[dict]) -> str    # → caminho do .xlsx
```

---

## 9. MODELOS DE DADOS

### params (entrada para `executar_automacao`)

```python
params = {
    "chamado_raiz":  str,   # obrigatório — ID do ticket pai
    "requerente":    str,   # opcional — sobrescreve o do raiz se preenchido
    "titulo":        str,   # opcional — sobrescreve o do raiz se preenchido
    "descricao":     str,   # opcional — sobrescreve o do raiz se preenchido
    "localizacao":   str,   # opcional — sobrescreve o do raiz se preenchido
    "categoria":     str,   # opcional — sobrescreve o do raiz se preenchido
    "planilha_path": str,   # obrigatório — caminho do arquivo .xlsx/.csv
    "saida_dir":     str,   # opcional — pasta de saída (padrão: mesma de entrada)
}
```

### Planilha de entrada

Qualquer número de colunas — **apenas login é extraído**.

| Nome Completo | CPF  | **Rede**   | Setor      | E-mail  |
|---------------|------|------------|------------|---------|
| João da Silva | 123… | joao.silva | Financeiro | joao@…  |

→ Sistema extrai apenas `["joao.silva", …]`

**Nomes aceitos para coluna de login** (case-insensitive):
`Login`, `Rede`, `Usuário` — e variações de capitalização.

### Planilha de saída (sempre exatamente 2 colunas)

| Login       | Chamados |
|-------------|----------|
| joao.silva  | 4521     |
| maria.santos | ERRO    |

### .env

| Variável              | Obrigatória | Default  | Descrição                        |
|-----------------------|-------------|----------|----------------------------------|
| `GLPI_URL`            | ✅          | —        | URL base sem `/` final           |
| `GLPI_TECNICO_LOGIN`  | ✅          | —        | Login do técnico                 |
| `GLPI_TECNICO_SENHA`  | ✅          | —        | Senha do técnico                 |
| `GLPI_HEADLESS`       | ❌          | `false`  | Modo headless (`true`/`false`)   |
| `GLPI_TIMEOUT`        | ❌          | `30000`  | Timeout em ms para Playwright    |

---

## 10. GIT WORKFLOW

### Setup inicial

```bash
git init
git add .
git status                                        # confirme que .env NÃO aparece
git commit -m "chore: estrutura inicial do projeto"
```

### Convenção de commits (Conventional Commits)

| Prefixo    | Quando usar                                   |
|------------|-----------------------------------------------|
| `feat:`    | nova funcionalidade                           |
| `fix:`     | correção de bug                               |
| `refactor:`| refatoração sem mudança de comportamento      |
| `chore:`   | dependências, config, CI                      |
| `docs:`    | spec.md, readme.md, comentários               |
| `test:`    | adição ou ajuste de testes                    |

**Exemplos:**
```
feat: adicionar detecção flexível de coluna de login (R7)
fix: corrigir timeout em criação de chamado filho
docs: atualizar spec com fase 2 — retry automático
```

### Tamanho de commit

- Cada commit faz **uma coisa** (atômico e revisável).
- PRs > 200 linhas precisam justificativa — prefira dividir.
- `ruff check .` passa **antes** do `git commit`.
- Nunca commitar `.env` ou credenciais.

### Branches (quando trabalhar em equipe)

```
main            → código estável, pronto para uso
feat/<nome>     → nova funcionalidade
fix/<nome>      → correção
```

---

## 11. TESTES *(verificação não é opcional)*

> Cada fase do workflow termina com evidência concreta. "Parece certo" não fecha o loop.

### Estado atual: sem testes automatizados

### Estratégia por fase

| Fase           | O que testar                                                                  | Ferramentas                        |
|----------------|-------------------------------------------------------------------------------|------------------------------------|
| **Unitário**   | `_detectar_coluna_login`, `_ler_planilha`, `_salvar_resultados`               | `pytest`, dados em memória         |
| **Integração** | `executar_automacao` com GLPI de homologação                                  | `pytest-asyncio`, Playwright headed |
| **Manual**     | Fluxo completo via interface gráfica                                          | Checklist abaixo                   |

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

## 12. ANTI-RACIONALIZAÇÃO

> Pré-refutações para decisões ruins. Um agente (ou engenheiro cansado) vai tentar cada uma delas.

| Racionalização                                                              | Por que está errada                                                                                     | Ação correta                                                          |
|-----------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------|
| "Esse campo é simples, não preciso de try/except individual."               | R4 existe exatamente para campos simples. Um timeout num campo derruba o chamado.                        | Envolva cada campo com `try/except` e log `⚠️`.                      |
| "Vou transportar o nome do usuário para a planilha de saída — é útil."     | Viola R6 explicitamente. Dados além de Login/Chamados nunca transitam.                                  | A saída tem **exatamente** 2 colunas. Ponto.                          |
| "Vou adicionar uma classe em automation.py para organizar melhor."          | O módulo é funcional por decisão arquitetural deliberada.                                               | 🚫 Nunca. Atualize o spec primeiro se quiser discutir.               |
| "O ruff está passando em tudo, posso pular o --fix desta vez."              | O `--check` apenas verifica. Sem `--fix`, pode haver formatação inconsistente.                          | `ruff check . --fix && ruff format .` sempre juntos antes do commit.  |
| "Este commit é pequeno, não precisa de mensagem convencional."              | Commits sem convenção acumulam e tornam `git log` ilegível.                                             | Sempre `feat:`, `fix:`, `chore:` etc. Leva 5 segundos.              |
| "O lote está quase terminando, vou abortar para economizar tempo."          | R4 é absoluto. O técnico precisa da planilha de resultados completa.                                    | Registre `"ERRO"` e continue. Planilha incompleta é pior que lenta.  |
| "Posso salvar o .env no git — ninguém vai ver."                             | Credenciais no git são permanentes mesmo após `git rm`.                                                 | `.gitignore` tem `.env`. Nunca, sob nenhuma circunstância.            |
| "Essa tarefa é simples, não preciso atualizar o spec."                      | Decisões não registradas criam divergência entre código e especificação.                                | Se mudou comportamento, muda o spec. Leva 2 minutos.                 |
| "Vou refatorar este arquivo adjacente enquanto estou aqui."                 | Toca código fora do escopo. Viola o Não-Negociável #4 e aumenta risco do PR.                           | Abra um commit separado com `refactor:` ou ignore por ora.           |

---

## 13. ROADMAP *(fases gated — não avançar sem validar gate de saída)*

### Fase 0 — Fundação

- [ ] Estrutura de arquivos flat
- [x] Interface gráfica CustomTkinter (dark mode, campos, log, progresso)
- [x] Leitura `.xlsx`/`.csv`
- [ ] Automação Playwright (login, leitura de raiz, criação de filhos)
- [ ] Geração planilha de resultados
- [ ] Eliminação de duplicação

**Gate de saída:** Fluxo completo manual funciona end-to-end.

### Fase 1 — Validação *(em andamento)*

- [ ] Implementar `_detectar_coluna_login()` — case-insensitive (R7)
- [x] Adicionar ruff ao projeto (`pyproject.toml` + `requirements.txt`)
- [x] Inicializar repositório git com `.gitignore` correto
- [ ] Testar com GLPI real (homologação) — 5 a 10 usuários
- [ ] Ajustar seletores CSS para versão do GLPI em uso
- [ ] Tratar edge cases: login inexistente, chamado raiz inválido, planilha vazia

**Gate de saída:** Checklist de aceite manual 100% ✅ + `ruff check .` = zero erros.

### Fase 2 — Robustez

- [ ] Retry automático (1–2 tentativas antes de marcar `"ERRO"`)
- [ ] Log salvo em arquivo `.log` além da interface
- [ ] Botão de cancelamento durante execução

**Gate de saída:** Teste de estresse com 50 usuários sem degradação de UI.

### Fase 3 — Evolução

- [ ] Vincular chamados filhos ao chamado raiz (link pai-filho no GLPI)
- [ ] Suporte a colunas extras opcionais (`Nome`, `Setor` → enriquecer descrição)
- [ ] Modo batch via CLI sem interface gráfica (`cli.py` com `argparse`)
- [ ] Suporte a Select2 (GLPI 10+)

**Gate de saída:** Cada item tem seu próprio PR atômico com teste de aceitação.

---

## 14. O QUE O SISTEMA NÃO FAZ *(e por quê)*

| Limite                            | Justificativa                                                                 |
|-----------------------------------|-------------------------------------------------------------------------------|
| Não vincula chamados pai-filho    | Exige navegação extra para links entre tickets. Complexidade não justificada agora. |
| Não altera chamados existentes    | Escopo é apenas criação. Alterar tickets existentes é outro problema.         |
| Não gerencia sessão/cookies       | Login do zero a cada execução. Simples e confiável.                          |
| Não valida logins contra o GLPI   | O autocomplete do GLPI faz isso. Campo vazio se login inexistir.              |
| Não suporta 2FA / SSO             | Apenas formulário padrão do GLPI.                                            |
| Não recarrega `.env` em runtime   | Variáveis lidas uma vez na inicialização. Alterar exige reiniciar.           |

---

## 15. SELF-CHECK *(antes de qualquer commit — 60 segundos)*

```
[ ] ruff check . retorna zero erros?
[ ] git status confirma que .env não está staged?
[ ] A mudança respeita R1 (requerente único)?
[ ] Usuários continuam sendo observadores (R2)?
[ ] Campos opcionais herdam do raiz se vazios (R3)?
[ ] Erros individuais NÃO interrompem o lote (R4)?
[ ] Planilha de resultados SEMPRE gerada (R5)?
[ ] Dados extras NÃO vazam para saída ou GLPI (R6)?
[ ] Coluna de login detectada com nomes variados (R7)?
[ ] UI continua responsiva (thread separada + self.after(0, ...))?
[ ] Nenhum import desnecessário adicionado?
[ ] Lógica duplicada foi extraída para helper?
[ ] Seletores CSS longos estão em constantes nomeadas?
[ ] O commit segue a convenção (feat:, fix:, etc.)?
[ ] Spec.md foi atualizado se houve decisão de design?
```
