import asyncio

from playwright.async_api import async_playwright


async def main():
    async with async_playwright() as p:
        navegador = await p.chromium.launch(
            executable_path=r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            headless=False
        )

        pagina = await navegador.new_page()

        await pagina.goto("https://www.google.com")

        print(await pagina.title())

        await pagina.wait_for_timeout(10000)

        await navegador.close()


asyncio.run(main())