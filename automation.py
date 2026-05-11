# automation.py
# Lógica de leitura de planilhas do AutoOpen
from pathlib import Path

import pandas as pd
from pandas.errors import EmptyDataError

# ---------------------------------------------------------------------------
# CONSTANTES
# ---------------------------------------------------------------------------

COLUNAS_LOGIN_ACEITAS = {
    "login",
    "rede",
    "usuário",
    "usuario",
}

# ---------------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------------


def _normalizar_coluna(nome: str) -> str:
    """Normaliza nome de coluna para comparação case-insensitive."""
    return str(nome).strip().lower()


def _detectar_coluna_login(colunas: list[str]) -> str:
    """Detecta automaticamente a coluna de login. Case-insensitive"""
    for coluna in colunas:
        coluna_normalizada = _normalizar_coluna(coluna)

        if coluna_normalizada in COLUNAS_LOGIN_ACEITAS:
            return coluna

    raise ValueError("Nenhuma coluna de login encontrada.\nColunas aceitas: Login, Rede, Usuário.")


def _ler_planilha(path: str) -> list[str]:
    """Leitura de planilha e coleta de logins."""
    arquivo = Path(path)

    if not arquivo.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {path}")

    extensao = arquivo.suffix.lower()

    # -----------------------------------------------------------------------
    # LEITURA
    # -----------------------------------------------------------------------

    if extensao == ".xlsx":
        df = pd.read_excel(arquivo)

    elif extensao == ".csv":
        try:
            df = pd.read_csv(arquivo)
        except UnicodeDecodeError:
            df = pd.read_csv(arquivo, encoding="latin1")
        except EmptyDataError as err:
            raise ValueError("A planilha está vazia.") from err

    else:
        raise ValueError("Formato inválido. Utilize apenas .xlsx ou .csv")

    # -----------------------------------------------------------------------
    # VALIDAÇÕES
    # -----------------------------------------------------------------------

    if df.empty:
        raise ValueError("A planilha está vazia.")

    coluna_login = _detectar_coluna_login(df.columns.tolist())

    # -----------------------------------------------------------------------
    # EXTRAÇÃO
    # -----------------------------------------------------------------------

    logins = df[coluna_login].dropna().astype(str).str.strip()

    # remove vazios
    logins = logins[logins != ""]

    # remove duplicados mantendo ordem
    logins = list(dict.fromkeys(logins.tolist()))

    if not logins:
        raise ValueError("Nenhum login válido encontrado na planilha.")

    return logins


def _salvar_resultados(resultados: list[dict], path: str) -> None:
    """Salva resultados da automação em planilha (CSV ou XLSX) com 2 colunas: Login e Chamado."""
    if not resultados:
        raise ValueError("Lista de resultados vazia.")

    arquivo = Path(path)
    arquivo.parent.mkdir(parents=True, exist_ok=True)

    # Garante exatamente 2 colunas: Login e Chamado
    df = pd.DataFrame(resultados)[["login", "chamado"]]

    extensao = arquivo.suffix.lower()

    if extensao == ".xlsx":
        df.to_excel(arquivo, index=False)
    elif extensao == ".csv":
        df.to_csv(arquivo, index=False)
    else:
        raise ValueError("Formato inválido. Utilize apenas .xlsx ou .csv")
