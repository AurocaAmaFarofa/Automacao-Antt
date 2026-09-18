import os

import winreg

from pathlib import Path

from playwright.async_api import async_playwright

from automation import consultar_placa

def encontrar_chrome():
    caminhos_possiveis = [
        Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe"),
        Path(r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"),
        Path.home() / r"AppData\Local\Google\Chrome\Application\chrome.exe",
    ]

    for caminho in caminhos_possiveis:
        if caminho.exists():
            return str(caminho)

    chaves_registro = [
        (winreg.HKEY_LOCAL_MACHINE,
         r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe"),

        (winreg.HKEY_LOCAL_MACHINE,
         r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe"),

        (winreg.HKEY_CURRENT_USER,
         r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe"),
    ]

    for hkey, caminho_chave in chaves_registro:
        try:
            with winreg.OpenKey(hkey, caminho_chave) as chave:
                caminho_chrome, _ = winreg.QueryValueEx(chave, None)

                caminho = Path(caminho_chrome)

                if caminho.exists():
                    return str(caminho)
        except (FileNotFoundError, OSError):
            continue

    return None

async def executar_consultas(consultas, pasta_destino, caminho_chrome):
    os.makedirs(
        pasta_destino,
        exist_ok=True
    )

    resultados = []

    async with async_playwright() as p:
        print("\nIniciando navegador...")

        navegador = await p.chromium.launch(
            headless=False,
            executable_path=caminho_chrome
        )

        pagina = await navegador.new_page()

        for dados_placa in consultas:
            sucesso = await consultar_placa(
                pagina,
                dados_placa,
                pasta_destino
            )

            resultados.append(
                (
                    dados_placa["placa"],
                    sucesso
                )
            )

        print("\nTodas as consultas foram processadas.")

        await navegador.close()

    return resultados