# main.py
# Interface gráfica do AutoOpen (GLPI Automation)
# Apenas UI — sem lógica de automação implementada

import os
import threading
from pathlib import Path
from tkinter import filedialog, messagebox

import customtkinter as ctk
from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# CONFIGURAÇÃO GLOBAL
# ---------------------------------------------------------------------------

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

APP_TITLE = "AutoOpen — GLPI Automation"
APP_WIDTH = 1100
APP_HEIGHT = 720

# ---------------------------------------------------------------------------
# LOAD ENV
# ---------------------------------------------------------------------------

load_dotenv()

ENV_OK = all(
    [
        os.getenv("GLPI_URL"),
        os.getenv("GLPI_TECNICO_LOGIN"),
        os.getenv("GLPI_TECNICO_SENHA"),
    ]
)

# ---------------------------------------------------------------------------
# APP
# ---------------------------------------------------------------------------


class AutoOpenApp(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()

        self.title(APP_TITLE)
        self.geometry(f"{APP_WIDTH}x{APP_HEIGHT}")
        self.minsize(1000, 650)

        self.planilha_path = ""
        self.saida_dir = ""

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self._build_header()
        self._build_form()
        self._build_footer()

    # -----------------------------------------------------------------------
    # HEADER
    # -----------------------------------------------------------------------

    def _build_header(self) -> None:
        header = ctk.CTkFrame(self, corner_radius=0)
        header.grid(row=0, column=0, sticky="ew", padx=0, pady=0)

        header.grid_columnconfigure(0, weight=1)

        title = ctk.CTkLabel(
            header,
            text="AutoOpen — GLPI Automation",
            font=ctk.CTkFont(size=26, weight="bold"),
        )
        title.grid(row=0, column=0, padx=20, pady=(20, 8), sticky="w")

        subtitle = ctk.CTkLabel(
            header,
            text="Criação automática de chamados filhos via planilha",
            font=ctk.CTkFont(size=14),
            text_color="gray70",
        )
        subtitle.grid(row=1, column=0, padx=20, pady=(0, 15), sticky="w")

        status_color = "#22c55e" if ENV_OK else "#ef4444"
        status_text = "ENV OK" if ENV_OK else "ENV INCOMPLETO"

        env_status = ctk.CTkLabel(
            header,
            text=f"● {status_text}",
            text_color=status_color,
            font=ctk.CTkFont(size=13, weight="bold"),
        )
        env_status.grid(row=0, column=1, padx=20, pady=(20, 0), sticky="e")

    # -----------------------------------------------------------------------
    # FORM
    # -----------------------------------------------------------------------

    def _build_form(self) -> None:
        content = ctk.CTkFrame(self)
        content.grid(row=1, column=0, sticky="nsew", padx=20, pady=20)

        content.grid_columnconfigure(0, weight=1)
        content.grid_columnconfigure(1, weight=1)
        content.grid_rowconfigure(2, weight=1)

        # ---------------------------------------------------------------
        # COLUNA ESQUERDA
        # ---------------------------------------------------------------

        left_frame = ctk.CTkFrame(content)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=0)

        left_frame.grid_columnconfigure(0, weight=1)

        self._build_inputs(left_frame)

        # ---------------------------------------------------------------
        # COLUNA DIREITA
        # ---------------------------------------------------------------

        right_frame = ctk.CTkFrame(content)
        right_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 0), pady=0)

        right_frame.grid_columnconfigure(0, weight=1)
        right_frame.grid_rowconfigure(1, weight=1)

        self._build_progress(right_frame)
        self._build_logs(right_frame)

    # -----------------------------------------------------------------------
    # INPUTS
    # -----------------------------------------------------------------------

    def _build_inputs(self, parent: ctk.CTkFrame) -> None:
        title = ctk.CTkLabel(
            parent,
            text="Parâmetros da Automação",
            font=ctk.CTkFont(size=18, weight="bold"),
        )
        title.grid(row=0, column=0, padx=20, pady=(20, 20), sticky="w")

        # ---------------------------------------------------------------
        # CHAMADO RAIZ
        # ---------------------------------------------------------------

        self.entry_chamado_raiz = self._create_input(
            parent=parent,
            row=1,
            label="Nº do Chamado Raiz *",
            placeholder="Ex: 4521",
        )

        # ---------------------------------------------------------------
        # REQUERENTE
        # ---------------------------------------------------------------

        self.entry_requerente = self._create_input(
            parent=parent,
            row=2,
            label="Requerente (opcional)",
            placeholder="Sobrescreve o requerente do chamado raiz",
        )

        # ---------------------------------------------------------------
        # TÍTULO
        # ---------------------------------------------------------------

        self.entry_titulo = self._create_input(
            parent=parent,
            row=3,
            label="Título (opcional)",
            placeholder="Sobrescreve o título do chamado raiz",
        )

        # ---------------------------------------------------------------
        # LOCALIZAÇÃO
        # ---------------------------------------------------------------

        self.entry_localizacao = self._create_input(
            parent=parent,
            row=4,
            label="Localização (opcional)",
            placeholder="Sobrescreve a localização do chamado raiz",
        )

        # ---------------------------------------------------------------
        # CATEGORIA
        # ---------------------------------------------------------------

        self.entry_categoria = self._create_input(
            parent=parent,
            row=5,
            label="Categoria (opcional)",
            placeholder="Sobrescreve a categoria do chamado raiz",
        )

        # ---------------------------------------------------------------
        # DESCRIÇÃO
        # ---------------------------------------------------------------

        desc_label = ctk.CTkLabel(
            parent,
            text="Descrição (opcional)",
            anchor="w",
            font=ctk.CTkFont(size=13, weight="bold"),
        )
        desc_label.grid(row=6, column=0, padx=20, pady=(18, 8), sticky="ew")

        self.text_descricao = ctk.CTkTextbox(
            parent,
            height=140,
            font=ctk.CTkFont(size=13),
        )
        self.text_descricao.grid(
            row=7,
            column=0,
            padx=20,
            pady=(0, 15),
            sticky="ew",
        )

        # ---------------------------------------------------------------
        # PLANILHA
        # ---------------------------------------------------------------

        planilha_label = ctk.CTkLabel(
            parent,
            text="Planilha de Entrada *",
            anchor="w",
            font=ctk.CTkFont(size=13, weight="bold"),
        )
        planilha_label.grid(row=8, column=0, padx=20, pady=(10, 8), sticky="ew")

        planilha_frame = ctk.CTkFrame(parent, fg_color="transparent")
        planilha_frame.grid(row=9, column=0, padx=20, pady=(0, 15), sticky="ew")

        planilha_frame.grid_columnconfigure(0, weight=1)

        self.entry_planilha = ctk.CTkEntry(
            planilha_frame,
            placeholder_text="Selecione uma planilha .xlsx ou .csv",
            state="readonly",
            height=40,
        )
        self.entry_planilha.grid(row=0, column=0, sticky="ew", padx=(0, 10))

        btn_planilha = ctk.CTkButton(
            planilha_frame,
            text="Selecionar",
            width=130,
            command=self._select_planilha,
        )
        btn_planilha.grid(row=0, column=1)

        # ---------------------------------------------------------------
        # SAÍDA
        # ---------------------------------------------------------------

        saida_label = ctk.CTkLabel(
            parent,
            text="Pasta de Saída (opcional)",
            anchor="w",
            font=ctk.CTkFont(size=13, weight="bold"),
        )
        saida_label.grid(row=10, column=0, padx=20, pady=(10, 8), sticky="ew")

        saida_frame = ctk.CTkFrame(parent, fg_color="transparent")
        saida_frame.grid(row=11, column=0, padx=20, pady=(0, 20), sticky="ew")

        saida_frame.grid_columnconfigure(0, weight=1)

        self.entry_saida = ctk.CTkEntry(
            saida_frame,
            placeholder_text="Opcional — padrão: mesma pasta da planilha",
            state="readonly",
            height=40,
        )
        self.entry_saida.grid(row=0, column=0, sticky="ew", padx=(0, 10))

        btn_saida = ctk.CTkButton(
            saida_frame,
            text="Selecionar",
            width=130,
            command=self._select_saida_dir,
        )
        btn_saida.grid(row=0, column=1)

    # -----------------------------------------------------------------------
    # PROGRESS
    # -----------------------------------------------------------------------

    def _build_progress(self, parent: ctk.CTkFrame) -> None:
        frame = ctk.CTkFrame(parent)
        frame.grid(row=0, column=0, sticky="ew", padx=20, pady=20)

        frame.grid_columnconfigure(0, weight=1)

        title = ctk.CTkLabel(
            frame,
            text="Progresso",
            font=ctk.CTkFont(size=18, weight="bold"),
        )
        title.grid(row=0, column=0, sticky="w", padx=20, pady=(18, 10))

        self.progress_label = ctk.CTkLabel(
            frame,
            text="Aguardando início...",
            text_color="gray70",
        )
        self.progress_label.grid(row=1, column=0, sticky="w", padx=20)

        self.progressbar = ctk.CTkProgressBar(frame, height=18)
        self.progressbar.grid(
            row=2,
            column=0,
            sticky="ew",
            padx=20,
            pady=(12, 18),
        )
        self.progressbar.set(0)

    # -----------------------------------------------------------------------
    # LOGS
    # -----------------------------------------------------------------------

    def _build_logs(self, parent: ctk.CTkFrame) -> None:
        frame = ctk.CTkFrame(parent)
        frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))

        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(1, weight=1)

        title = ctk.CTkLabel(
            frame,
            text="Logs da Execução",
            font=ctk.CTkFont(size=18, weight="bold"),
        )
        title.grid(row=0, column=0, sticky="w", padx=20, pady=(18, 10))

        self.log_box = ctk.CTkTextbox(
            frame,
            font=("Consolas", 12),
            wrap="word",
        )
        self.log_box.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=20,
            pady=(0, 20),
        )

        self.log_box.insert("end", "Sistema inicializado.\n")
        self.log_box.insert(
            "end",
            "Nenhuma automação em execução.\n",
        )

        self.log_box.configure(state="disabled")

    # -----------------------------------------------------------------------
    # FOOTER
    # -----------------------------------------------------------------------

    def _build_footer(self) -> None:
        footer = ctk.CTkFrame(self, corner_radius=0)
        footer.grid(row=2, column=0, sticky="ew", padx=0, pady=0)

        footer.grid_columnconfigure(0, weight=1)

        self.btn_iniciar = ctk.CTkButton(
            footer,
            text="▶ INICIAR AUTOMAÇÃO",
            height=50,
            font=ctk.CTkFont(size=15, weight="bold"),
            command=self._on_start,
        )
        self.btn_iniciar.grid(
            row=0,
            column=0,
            padx=(20, 10),
            pady=20,
            sticky="ew",
        )

        self.btn_limpar = ctk.CTkButton(
            footer,
            text="Limpar Logs",
            height=50,
            width=160,
            fg_color="#374151",
            hover_color="#4b5563",
            command=self._clear_logs,
        )
        self.btn_limpar.grid(
            row=0,
            column=1,
            padx=(0, 20),
            pady=20,
        )

    # -----------------------------------------------------------------------
    # HELPERS UI
    # -----------------------------------------------------------------------

    def _create_input(
        self,
        parent: ctk.CTkFrame,
        row: int,
        label: str,
        placeholder: str,
    ) -> ctk.CTkEntry:
        label_widget = ctk.CTkLabel(
            parent,
            text=label,
            anchor="w",
            font=ctk.CTkFont(size=13, weight="bold"),
        )
        label_widget.grid(
            row=row * 2,
            column=0,
            padx=20,
            pady=(10, 8),
            sticky="ew",
        )

        entry = ctk.CTkEntry(
            parent,
            placeholder_text=placeholder,
            height=40,
            font=ctk.CTkFont(size=13),
        )
        entry.grid(
            row=(row * 2) + 1,
            column=0,
            padx=20,
            pady=(0, 5),
            sticky="ew",
        )

        return entry

    def _append_log(self, message: str) -> None:
        self.log_box.configure(state="normal")
        self.log_box.insert("end", f"{message}\n")
        self.log_box.see("end")
        self.log_box.configure(state="disabled")

    # -----------------------------------------------------------------------
    # FILE PICKERS
    # -----------------------------------------------------------------------

    def _select_planilha(self) -> None:
        file_path = filedialog.askopenfilename(
            title="Selecionar planilha",
            filetypes=[
                ("Planilhas Excel", "*.xlsx"),
                ("CSV", "*.csv"),
                ("Todos os arquivos", "*.*"),
            ],
        )

        if not file_path:
            return

        self.planilha_path = file_path

        self.entry_planilha.configure(state="normal")
        self.entry_planilha.delete(0, "end")
        self.entry_planilha.insert(0, file_path)
        self.entry_planilha.configure(state="readonly")

        self._append_log(f"📄 Planilha selecionada: {Path(file_path).name}")

    def _select_saida_dir(self) -> None:
        directory = filedialog.askdirectory(
            title="Selecionar pasta de saída",
        )

        if not directory:
            return

        self.saida_dir = directory

        self.entry_saida.configure(state="normal")
        self.entry_saida.delete(0, "end")
        self.entry_saida.insert(0, directory)
        self.entry_saida.configure(state="readonly")

        self._append_log(f"📁 Pasta de saída: {directory}")

    # -----------------------------------------------------------------------
    # START
    # -----------------------------------------------------------------------

    def _on_start(self) -> None:
        chamado_raiz = self.entry_chamado_raiz.get().strip()

        if not chamado_raiz:
            messagebox.showerror(
                "Campo obrigatório",
                "Informe o número do chamado raiz.",
            )
            return

        if not self.planilha_path:
            messagebox.showerror(
                "Planilha obrigatória",
                "Selecione uma planilha de entrada.",
            )
            return

        params = {
            "chamado_raiz": chamado_raiz,
            "requerente": self.entry_requerente.get().strip(),
            "titulo": self.entry_titulo.get().strip(),
            "descricao": self.text_descricao.get("1.0", "end").strip(),
            "localizacao": self.entry_localizacao.get().strip(),
            "categoria": self.entry_categoria.get().strip(),
            "planilha_path": self.planilha_path,
            "saida_dir": self.saida_dir,
        }

        self._append_log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        self._append_log("🚀 Automação iniciada")
        self._append_log(f"🎫 Chamado raiz: {params['chamado_raiz']}")
        self._append_log("⏳ Aguardando implementação da automação...")
        self._append_log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

        self.btn_iniciar.configure(state="disabled")
        self.progressbar.set(0.2)
        self.progress_label.configure(text="Preparando execução...")

        threading.Thread(
            target=self._fake_execution,
            daemon=True,
        ).start()

    # -----------------------------------------------------------------------
    # MOCK EXECUTION
    # -----------------------------------------------------------------------

    def _fake_execution(self) -> None:
        import time

        steps = [
            "Lendo planilha...",
            "Validando parâmetros...",
            "Inicializando Playwright...",
            "Preparando automação...",
            "Aguardando implementação...",
        ]

        total = len(steps)

        for index, step in enumerate(steps, start=1):
            time.sleep(0.7)

            progress = index / total

            self.after(0, lambda s=step: self._append_log(f"⚙️ {s}"))
            self.after(
                0,
                lambda p=progress: self.progressbar.set(p),
            )
            self.after(
                0,
                lambda i=index, t=total: self.progress_label.configure(
                    text=f"Etapa {i}/{t}",
                ),
            )

        self.after(0, self._finish_mock_execution)

    def _finish_mock_execution(self) -> None:
        self._append_log("✅ Interface pronta para integração com automation.py")

        self.progressbar.set(1)
        self.progress_label.configure(text="Execução finalizada")

        self.btn_iniciar.configure(state="normal")

        messagebox.showinfo(
            "AutoOpen",
            "Interface gráfica concluída.\n\nA lógica da automação ainda não foi implementada.",
        )

    # -----------------------------------------------------------------------
    # CLEAR LOGS
    # -----------------------------------------------------------------------

    def _clear_logs(self) -> None:
        self.log_box.configure(state="normal")
        self.log_box.delete("1.0", "end")
        self.log_box.configure(state="disabled")


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    app = AutoOpenApp()
    app.mainloop()
