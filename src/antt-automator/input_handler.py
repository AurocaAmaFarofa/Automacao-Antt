import re
import tkinter as tk
from tkinter import filedialog


def normalizar_placa(placa: str) -> str:
    placa_limpa = re.sub(r"[^a-zA-Z0-9]", "", placa)
    return placa_limpa.upper()


def normalizar_documento(numero: str) -> str:
    return re.sub(r"\D", "", numero or "")


def selecionar_pasta():
    root = tk.Tk()
    root.withdraw()

    pasta = filedialog.askdirectory(
        title="Selecione a pasta onde os PDFs serão salvos"
    )

    root.destroy()

    return pasta


def coletar_dados_das_placas():
    """
    Etapa de coleta via CMD:

    - Pergunta quantas placas serão consultadas (máx: 4)
    - Para cada placa, pede a placa e o documento (RNTRC ou CPF/CNPJ)
    - Retorna uma lista de dicionários:
      [
          {
              "placa": "...",
              "rntrc": "...",
              "cpf_cnpj": "..."
          }
      ]
    """

    while True:
        try:
            quantidade = int(
                input("Quantas placas serão consultadas? (max: 4): ").strip()
            )
        except ValueError:
            print("Digite um número válido.")
            continue

        if quantidade < 1 or quantidade > 4:
            print("Informe um valor entre 1 e 4.")
            continue

        break

    consultas = []

    for i in range(quantidade):
        print(f"\n--- Placa {i + 1} de {quantidade} ---")

        placa_input = input("Insira placa: ").strip()
        documento_input = input(
            "Insira CNPJ/CPF ou RNTRC: "
        ).strip()

        rntrc_normalizado = ""
        cpf_cnpj_normalizado = ""

        documento_normalizado_digitos = normalizar_documento(
            documento_input
        )

        # Regra atual:
        # 9 dígitos = RNTRC
        # qualquer outra quantidade = CPF/CNPJ
        if len(documento_normalizado_digitos) == 9:
            rntrc_normalizado = documento_normalizado_digitos
        else:
            cpf_cnpj_normalizado = documento_normalizado_digitos

        consultas.append(
            {
                "placa": normalizar_placa(placa_input),
                "rntrc": rntrc_normalizado,
                "cpf_cnpj": cpf_cnpj_normalizado,
            }
        )

    return consultas