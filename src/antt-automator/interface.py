import asyncio
import threading
import os

import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk

from runner import executar_consultas, encontrar_chrome
from config import salvar_configuracao, carregar_configuracao


class InterfaceANTT:

    def __init__(self, root):
        self.root = root

        self.root.title("Automação ANTT")
        self.root.geometry("750x800")
        self.root.resizable(False, False)

        self.pasta_destino = ""
        self.consultas = []
        self.caminho_chrome = ""

        self.configuracao = carregar_configuracao()

        self.criar_interface()

    def criar_interface(self):

        # ============================================================
        # TÍTULO
        # ============================================================

        titulo = tk.Label(
            self.root,
            text="AnttFlow",
            font=("Segoe UI", 22, "bold")
        )

        titulo.pack(pady=(25, 5))

        subtitulo = tk.Label(
            self.root,
            text="Consulta de RNTRC e geração automática dos protocolos",
            font=("Segoe UI", 10)
        )

        subtitulo.pack(pady=(0, 20))

        # ============================================================
        # PASTA DE DESTINO
        # ============================================================

        frame_pasta = tk.LabelFrame(
            self.root,
            text=" Pasta dos PDFs ",
            font=("Segoe UI", 10, "bold"),
            padx=10,
            pady=10
        )

        frame_pasta.pack(
            fill="x",
            padx=30,
            pady=10
        )

        self.entry_pasta = tk.Entry(
            frame_pasta,
            font=("Segoe UI", 10)
        )

        self.entry_pasta.pack(
            side="left",
            fill="x",
            expand=True,
            padx=(0, 10)
        )

        botao_pasta = tk.Button(
            frame_pasta,
            text="Selecionar",
            command=self.selecionar_pasta,
            font=("Segoe UI", 10)
        )
        botao_pasta.pack(side="right")

        pasta_salva = self.configuracao.get("pasta_destino", "")

        if pasta_salva and os.path.isdir(pasta_salva):
            self.pasta_destino = pasta_salva
            self.entry_pasta.insert(0, pasta_salva)

        # ============================================================
        # CAMINHO DO CHROME
        # ============================================================

        frame_chrome = tk.LabelFrame(
        self.root,
        text=" Navegador Chrome ",
        font=("Segoe UI", 10, "bold"),
        padx=10,
        pady=10
        )
        frame_chrome.pack(fill="x", padx=30, pady=10)

        self.entry_chrome = tk.Entry(
            frame_chrome,
            font=("Segoe UI", 10)
        )
        self.entry_chrome.pack(
            side="left",
            fill="x",
            expand=True,
            padx=(0, 10)
        )

        botao_chrome = tk.Button(
            frame_chrome,
            text="Selecionar",
            command=self.selecionar_chrome,
            font=("Segoe UI", 10)
        )
        botao_chrome.pack(side="right")

        chrome_salvo = self.configuracao.get("chrome", "")

        if chrome_salvo and os.path.isfile(chrome_salvo):
            self.caminho_chrome = chrome_salvo
            self.entry_chrome.insert(0, chrome_salvo)

        else:
            chrome_detectado = encontrar_chrome()
            print("CHROME ENCONTRADO:", chrome_detectado)

            if chrome_detectado:
                self.caminho_chrome = chrome_detectado
                self.entry_chrome.insert(0, chrome_detectado)

                salvar_configuracao(
                    chrome_detectado,
                    self.pasta_destino
                )

        # ============================================================
        # NOVA CONSULTA
        # ============================================================

        frame_nova = tk.LabelFrame(
            self.root,
            text=" Nova consulta ",
            font=("Segoe UI", 10, "bold"),
            padx=10,
            pady=10
        )

        frame_nova.pack(
            fill="x",
            padx=30,
            pady=10
        )

        label_placa = tk.Label(
            frame_nova,
            text="Placa:",
            font=("Segoe UI", 10)
        )

        label_placa.grid(
            row=0,
            column=0,
            padx=(0, 8),
            pady=5
        )

        self.entry_placa = tk.Entry(
            frame_nova,
            width=18,
            font=("Segoe UI", 10)
        )

        self.entry_placa.grid(
            row=0,
            column=1,
            padx=(0, 20),
            pady=5
        )

        label_documento = tk.Label(
            frame_nova,
            text="RNTRC / CPF / CNPJ:",
            font=("Segoe UI", 10)
        )

        label_documento.grid(
            row=0,
            column=2,
            padx=(0, 8),
            pady=5
        )

        self.entry_documento = tk.Entry(
            frame_nova,
            width=25,
            font=("Segoe UI", 10)
        )

        self.entry_documento.grid(
            row=0,
            column=3,
            padx=(0, 10),
            pady=5
        )

        botao_adicionar = tk.Button(
            frame_nova,
            text="Adicionar",
            command=self.adicionar_consulta,
            font=("Segoe UI", 10, "bold")
        )

        botao_adicionar.grid(
            row=0,
            column=4,
            pady=5
        )

        # ============================================================
        # LISTA DE CONSULTAS
        # ============================================================

        frame_lista = tk.LabelFrame(
            self.root,
            text=" Consultas ",
            font=("Segoe UI", 10, "bold"),
            padx=10,
            pady=10
        )

        frame_lista.pack(
            fill="both",
            padx=30,
            pady=10
        )

        colunas = (
            "placa",
            "documento",
            "tipo"
        )

        self.tabela = ttk.Treeview(
            frame_lista,
            columns=colunas,
            show="headings",
            height=8
        )

        self.tabela.heading(
            "placa",
            text="Placa"
        )

        self.tabela.heading(
            "documento",
            text="Documento"
        )

        self.tabela.heading(
            "tipo",
            text="Tipo"
        )

        self.tabela.column(
            "placa",
            width=150,
            anchor="center"
        )

        self.tabela.column(
            "documento",
            width=250,
            anchor="center"
        )

        self.tabela.column(
            "tipo",
            width=150,
            anchor="center"
        )

        scrollbar = ttk.Scrollbar(
            frame_lista,
            orient="vertical",
            command=self.tabela.yview
        )

        self.tabela.configure(
            yscrollcommand=scrollbar.set
        )

        self.tabela.pack(
            side="left",
            fill="both",
            expand=True
        )

        scrollbar.pack(
            side="right",
            fill="y"
        )

        # ============================================================
        # BOTÃO REMOVER
        # ============================================================

        botao_remover = tk.Button(
            self.root,
            text="Remover selecionada",
            command=self.remover_consulta,
            font=("Segoe UI", 10)
        )

        botao_remover.pack(
            pady=(0, 10)
        )

        # ============================================================
        # BOTÃO INICIAR
        # ============================================================

        self.botao_iniciar = tk.Button(
            self.root,
            text="INICIAR CONSULTAS",
            command=self.iniciar_consultas,
            font=("Segoe UI", 12, "bold"),
            width=25,
            height=2
        )

        self.botao_iniciar.pack(
            pady=(5, 15)
        )

        # ============================================================
        # STATUS
        # ============================================================

        self.label_status = tk.Label(
            self.root,
            text="Aguardando consultas...",
            font=("Segoe UI", 10)
        )

        self.label_status.pack(
            pady=(0, 20)
        )

    # ================================================================
    # SELECIONAR PASTA
    # ================================================================

    def selecionar_pasta(self):
        pasta = filedialog.askdirectory(
            title="Selecione a pasta onde os PDFs serão salvos"
        )

        if pasta:
            self.pasta_destino = pasta

            self.entry_pasta.delete(0, tk.END)
            self.entry_pasta.insert(0, pasta)

            salvar_configuracao(
                self.caminho_chrome,
                self.pasta_destino
            )

    # ================================================================
    # SELECIONAR CHROME
    # ================================================================

    def selecionar_chrome(self):
        caminho = filedialog.askopenfilename(
            title="Selecione o executável do Google Chrome",
            filetypes=[
                ("Executável do Chrome", "chrome.exe"),
                ("Todos os arquivos", "*.*")
            ]
        )

        if caminho:
            if caminho.lower().endswith("chrome.exe") and os.path.isfile(caminho):

                self.caminho_chrome = caminho

                self.entry_chrome.delete(0, tk.END)
                self.entry_chrome.insert(0, caminho)

                salvar_configuracao(
                    self.caminho_chrome,
                    self.pasta_destino
                )

                self.label_status.config(
                    text="Chrome selecionado com sucesso."
                )

            else:
                messagebox.showwarning(
                    "Chrome inválido",
                    "Selecione o arquivo chrome.exe do Google Chrome."
                )

    # ================================================================
    # ADICIONAR CONSULTA
    # ================================================================

    def adicionar_consulta(self):

        placa = self.entry_placa.get().strip().upper()

        documento = self.entry_documento.get().strip()

        if not placa:
            messagebox.showwarning(
                "Atenção",
                "Informe a placa."
            )
            return

        if not documento:
            messagebox.showwarning(
                "Atenção",
                "Informe o RNTRC, CPF ou CNPJ."
            )
            return

        documento_numeros = "".join(
            caractere
            for caractere in documento
            if caractere.isdigit()
        )

        if len(documento_numeros) == 9:

            tipo = "RNTRC"

            consulta = {
                "placa": placa,
                "rntrc": documento_numeros,
                "cpf_cnpj": ""
            }

        else:

            tipo = (
                "CNPJ"
                if len(documento_numeros) > 11
                else "CPF"
            )

            consulta = {
                "placa": placa,
                "rntrc": "",
                "cpf_cnpj": documento_numeros
            }

        self.consultas.append(consulta)

        self.tabela.insert(
            "",
            tk.END,
            values=(
                placa,
                documento_numeros,
                tipo
            )
        )

        self.entry_placa.delete(
            0,
            tk.END
        )

        self.entry_documento.delete(
            0,
            tk.END
        )

        self.label_status.config(
            text=f"{len(self.consultas)} consulta(s) adicionada(s)."
        )

    # ================================================================
    # REMOVER CONSULTA
    # ================================================================

    def remover_consulta(self):

        selecionado = self.tabela.selection()

        if not selecionado:
            messagebox.showwarning(
                "Atenção",
                "Selecione uma consulta para remover."
            )
            return

        item = selecionado[0]

        indice = self.tabela.index(item)

        self.tabela.delete(item)

        del self.consultas[indice]

        self.label_status.config(
            text=f"{len(self.consultas)} consulta(s) adicionada(s)."
        )

    # ================================================================
    # INICIAR CONSULTAS
    # ================================================================

    def iniciar_consultas(self):
        self.caminho_chrome = self.entry_chrome.get().strip()
        self.pasta_destino = self.entry_pasta.get().strip()

        if not self.caminho_chrome:
            messagebox.showwarning(
                "Chrome não encontrado",
                "O Google Chrome não foi encontrado.\n\n"
                "Clique em 'Selecionar' e escolha o arquivo chrome.exe."
            )
            return

        if not os.path.isfile(self.caminho_chrome):
            messagebox.showwarning(
                "Chrome inválido",
                "O caminho informado para o Chrome não existe."
            )
            return

        if not self.pasta_destino:
            messagebox.showwarning(
                "Atenção",
                "Selecione a pasta onde os PDFs serão salvos."
            )
            return

        if not os.path.isdir(self.pasta_destino):
            messagebox.showwarning(
                "Pasta inválida",
                "A pasta selecionada não existe."
            )
            return

        if not self.consultas:
            messagebox.showwarning(
                "Atenção",
                "Adicione pelo menos uma consulta."
            )
            return

        salvar_configuracao(
            self.caminho_chrome,
            self.pasta_destino
        )

        self.botao_iniciar.config(
            state="disabled"
        )

        self.label_status.config(
            text="Iniciando automação ANTT..."
        )

        thread = threading.Thread(
            target=self.executar_automacao,
            daemon=True
        )

        thread.start()

    # ================================================================
    # EXECUTAR AUTOMAÇÃO
    # ================================================================

    def executar_automacao(self):

        try:

            resultados = asyncio.run(
                executar_consultas(
                    self.consultas,
                    self.pasta_destino,
                    self.caminho_chrome
                )
            )

            sucessos = sum(
                1
                for _, sucesso in resultados
                if sucesso
            )

            falhas = len(resultados) - sucessos

            self.root.after(
                0,
                lambda: self.finalizar_automacao(
                    resultados,
                    sucessos,
                    falhas
                )
            )

        except Exception as erro:

            self.root.after(
                0,
                lambda erro=erro: self.erro_automacao(
                    erro
                )
            )

    # ================================================================
    # FINALIZAR AUTOMAÇÃO
    # ================================================================

    def finalizar_automacao(
        self,
        resultados,
        sucessos,
        falhas
    ):

        self.botao_iniciar.config(
            state="normal"
        )

        self.label_status.config(
        text="Automação concluída."
        )

        messagebox.showinfo(
            "Automação concluída",
            (
                f"Consultas finalizadas!\n\n"
                f"PDFs salvos: {sucessos}\n"
                f"Erros: {falhas}"
            )
        )

        for placa, sucesso in resultados:
            if sucesso:
                for item in self.tabela.get_children():
                    valores = self.tabela.item(item, "values")

                    if valores[0] == placa:
                        self.tabela.delete(item)
                        break

                for consulta in self.consultas[:]:
                    if consulta["placa"] == placa:
                        self.consultas.remove(consulta)
                        break

        self.label_status.config(
        text="Aguardando novas consultas..."
        )

    # ================================================================
    # ERRO NA AUTOMAÇÃO
    # ================================================================

    def erro_automacao(self, erro):

        self.botao_iniciar.config(
            state="normal"
        )

        self.label_status.config(
            text="Erro durante a automação."
        )

        messagebox.showerror(
            "Erro",
            f"Ocorreu um erro durante a automação:\n\n{erro}"
        )


# ====================================================================
# INICIAR INTERFACE
# ====================================================================

def iniciar_interface():

    root = tk.Tk()

    InterfaceANTT(root)

    root.mainloop()