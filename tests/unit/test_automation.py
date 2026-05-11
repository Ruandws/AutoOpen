"""Testes unitários para automation.py"""

import tempfile
from pathlib import Path

import pandas as pd
import pytest

from automation import (
    _detectar_coluna_login,
    _ler_planilha,
    _normalizar_coluna,
    _salvar_resultados,
)

# ---------------------------------------------------------------------------
# TESTES: _normalizar_coluna
# ---------------------------------------------------------------------------


class Test_NormalizarColuna:
    """Testes para normalização de nomes de coluna."""

    def test_minuscula(self):
        """Converte para minúsculas."""
        assert _normalizar_coluna("Login") == "login"

    def test_espacos(self):
        """Remove espaços em branco."""
        assert _normalizar_coluna("  login  ") == "login"

    def test_acentuacao(self):
        """Mantém acentuação."""
        assert _normalizar_coluna("Usuário") == "usuário"


# ---------------------------------------------------------------------------
# TESTES: _detectar_coluna_login
# ---------------------------------------------------------------------------


class Test_DetectarColunaLogin:
    """Testes para detecção automática de coluna de login."""

    def test_login_exato(self):
        """Encontra 'login' em maiúscula."""
        resultado = _detectar_coluna_login(["ID", "Login", "Data"])
        assert resultado == "Login"

    def test_rede_exato(self):
        """Encontra 'rede' em maiúscula."""
        resultado = _detectar_coluna_login(["ID", "Rede", "Data"])
        assert resultado == "Rede"

    def test_usuario_exato(self):
        """Encontra 'usuario' sem acento."""
        resultado = _detectar_coluna_login(["ID", "Usuario", "Data"])
        assert resultado == "Usuario"

    def test_usuario_acentuado(self):
        """Encontra 'usuário' com acento."""
        resultado = _detectar_coluna_login(["ID", "Usuário", "Data"])
        assert resultado == "Usuário"

    def test_case_insensitive(self):
        """Case-insensitive: encontra 'LOGIN' em maiúscula."""
        resultado = _detectar_coluna_login(["ID", "LOGIN", "Data"])
        assert resultado == "LOGIN"

    def test_com_espacos(self):
        """Encontra coluna com espaços em branco."""
        resultado = _detectar_coluna_login(["ID", "  login  ", "Data"])
        assert resultado == "  login  "

    def test_nenhuma_coluna_encontrada(self):
        """Levanta erro se nenhuma coluna de login."""
        with pytest.raises(ValueError, match="Nenhuma coluna de login"):
            _detectar_coluna_login(["ID", "Nome", "Data"])

    def test_lista_vazia(self):
        """Levanta erro se lista vazia."""
        with pytest.raises(ValueError, match="Nenhuma coluna de login"):
            _detectar_coluna_login([])


# ---------------------------------------------------------------------------
# TESTES: _ler_planilha
# ---------------------------------------------------------------------------


class Test_LerPlanilha:
    """Testes para leitura de planilha."""

    def test_csv_simples(self):
        """Lê CSV simples."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write("Login,Descricao\n")
            f.write("user1,Descrição 1\n")
            f.write("user2,Descrição 2\n")
            temp_path = f.name

        try:
            logins = _ler_planilha(temp_path)
            assert logins == ["user1", "user2"]
        finally:
            Path(temp_path).unlink()

    def test_csv_com_branco(self):
        """CSV com espaços em branco nos logins."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write("Login,Descricao\n")
            f.write("  user1  ,Descrição 1\n")
            f.write("user2,Descrição 2\n")
            temp_path = f.name

        try:
            logins = _ler_planilha(temp_path)
            assert logins == ["user1", "user2"]
        finally:
            Path(temp_path).unlink()

    def test_csv_duplicados(self):
        """Remove duplicados mantendo ordem."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write("Login,Descricao\n")
            f.write("user1,Desc 1\n")
            f.write("user2,Desc 2\n")
            f.write("user1,Desc 3\n")
            temp_path = f.name

        try:
            logins = _ler_planilha(temp_path)
            assert logins == ["user1", "user2"]
        finally:
            Path(temp_path).unlink()

    def test_csv_com_nulos(self):
        """Ignora linhas vazias/nulas."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write("Login,Descricao\n")
            f.write("user1,Desc 1\n")
            f.write(",\n")
            f.write("user2,Desc 2\n")
            temp_path = f.name

        try:
            logins = _ler_planilha(temp_path)
            assert logins == ["user1", "user2"]
        finally:
            Path(temp_path).unlink()

    def test_xlsx_simples(self):
        """Lê XLSX simples."""
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as f:
            temp_path = f.name

        try:
            df = pd.DataFrame({"Login": ["user1", "user2"], "Descricao": ["Desc 1", "Desc 2"]})
            df.to_excel(temp_path, index=False)

            logins = _ler_planilha(temp_path)
            assert logins == ["user1", "user2"]
        finally:
            Path(temp_path).unlink()

    def test_arquivo_nao_existe(self):
        """Levanta erro se arquivo não existe."""
        with pytest.raises(FileNotFoundError):
            _ler_planilha("/tmp/inexistente_12345.csv")

    def test_planilha_vazia(self):
        """Levanta erro se planilha está vazia."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write("")
            temp_path = f.name

        try:
            with pytest.raises(ValueError, match="vazia"):
                _ler_planilha(temp_path)
        finally:
            Path(temp_path).unlink()

    def test_formato_invalido(self):
        """Levanta erro para formato não suportado."""
        with tempfile.NamedTemporaryFile(mode="wb", suffix=".txt", delete=False) as f:
            f.write(b"user1\nuser2\n")
            temp_path = f.name

        try:
            with pytest.raises(ValueError, match="Formato inválido"):
                _ler_planilha(temp_path)
        finally:
            Path(temp_path).unlink()

    def test_nenhum_login_valido(self):
        """Levanta erro se nenhum login válido."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write("Descricao\n")
            f.write("Apenas descrição\n")
            temp_path = f.name

        try:
            with pytest.raises(ValueError, match="Nenhuma coluna de login"):
                _ler_planilha(temp_path)
        finally:
            Path(temp_path).unlink()

    def test_coluna_login_variados_nomes(self):
        """Detecta 'Usuário' como coluna de login."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write("Usuário,Descricao\n")
            f.write("user1,Desc 1\n")
            f.write("user2,Desc 2\n")
            temp_path = f.name

        try:
            logins = _ler_planilha(temp_path)
            assert logins == ["user1", "user2"]
        finally:
            Path(temp_path).unlink()


# ---------------------------------------------------------------------------
# TESTES: _salvar_resultados
# ---------------------------------------------------------------------------


class Test_SalvarResultados:
    """Testes para salvamento de resultados."""

    def test_csv_duas_colunas(self):
        """Salva CSV com exatamente 2 colunas."""
        with tempfile.TemporaryDirectory() as tmpdir:
            temp_path = Path(tmpdir) / "resultado.csv"

            resultados = [
                {"login": "user1", "chamado": "12345"},
                {"login": "user2", "chamado": "12346"},
            ]

            _salvar_resultados(resultados, str(temp_path))

            # Verifica que o arquivo foi criado
            assert temp_path.exists()

            # Verifica conteúdo
            df = pd.read_csv(temp_path, dtype=str)
            assert list(df.columns) == ["login", "chamado"]
            assert len(df) == 2
            assert df.iloc[0]["login"] == "user1"
            assert df.iloc[0]["chamado"] == "12345"

    def test_xlsx_duas_colunas(self):
        """Salva XLSX com exatamente 2 colunas."""
        with tempfile.TemporaryDirectory() as tmpdir:
            temp_path = Path(tmpdir) / "resultado.xlsx"

            resultados = [
                {"login": "user1", "chamado": "12345"},
                {"login": "user2", "chamado": "ERRO"},
            ]

            _salvar_resultados(resultados, str(temp_path))

            # Verifica que o arquivo foi criado
            assert temp_path.exists()

            # Verifica conteúdo
            df = pd.read_excel(temp_path)
            assert list(df.columns) == ["login", "chamado"]
            assert len(df) == 2
            assert df.iloc[1]["chamado"] == "ERRO"

    def test_ignora_colunas_extras(self):
        """Ignora colunas extras, mantém só 2."""
        with tempfile.TemporaryDirectory() as tmpdir:
            temp_path = Path(tmpdir) / "resultado.csv"

            resultados = [
                {"login": "user1", "chamado": "12345", "extra": "ignorado"},
                {"login": "user2", "chamado": "12346", "outra": "coluna"},
            ]

            _salvar_resultados(resultados, str(temp_path))

            df = pd.read_csv(temp_path)
            # Deve ter exatamente 2 colunas (R6)
            assert len(df.columns) == 2
            assert "extra" not in df.columns

    def test_cria_diretorio_se_nao_existe(self):
        """Cria diretório pai se não existir."""
        with tempfile.TemporaryDirectory() as tmpdir:
            temp_path = Path(tmpdir) / "subdir" / "resultado.csv"

            resultados = [{"login": "user1", "chamado": "12345"}]

            _salvar_resultados(resultados, str(temp_path))

            assert temp_path.exists()
            assert temp_path.parent.exists()

    def test_lista_vazia(self):
        """Levanta erro se lista vazia."""
        with tempfile.TemporaryDirectory() as tmpdir:
            temp_path = Path(tmpdir) / "resultado.csv"

            with pytest.raises(ValueError, match="vazia"):
                _salvar_resultados([], str(temp_path))

    def test_formato_invalido(self):
        """Levanta erro para formato não suportado."""
        with tempfile.TemporaryDirectory() as tmpdir:
            temp_path = Path(tmpdir) / "resultado.txt"

            resultados = [{"login": "user1", "chamado": "12345"}]

            with pytest.raises(ValueError, match="Formato inválido"):
                _salvar_resultados(resultados, str(temp_path))
