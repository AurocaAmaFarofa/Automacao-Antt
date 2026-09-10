import os

from playwright.async_api import async_playwright

from automation import consultar_placa


async def executar_consultas(consultas, pasta_destino):
    os.makedirs(
        pasta_destino,
        exist_ok=True
    )

    resultados = []

    async with async_playwright() as p:
        print("\nIniciando navegador...")

        navegador = await p.chromium.launch(
            headless=False,
            executable_path=(
                r"C:\Program Files\Google\Chrome\Application\chrome.exe"
            )
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