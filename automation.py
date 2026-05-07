# automation.py
# Lógica de leitura de planilhas do AutoOpen
from pathlib import Path

import pandas as pd

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
