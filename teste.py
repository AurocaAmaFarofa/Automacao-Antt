import asyncio
from playwright.async_api import async_playwright


async def main():
    async with async_playwright() as p:

        print("Iniciando Chromium...")

        navegador = await p.chromium.launch(
            headless=False
        )

        print("Chromium abriu!")

        pagina = await navegador.new_page()

        await pagina.goto("https://www.google.com")

        print("Página abriu!")

        await pagina.wait_for_timeout(5000)

        await navegador.close()


asyncio.run(main())