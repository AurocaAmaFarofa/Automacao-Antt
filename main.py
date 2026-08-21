import asyncio

from playwright.async_api import async_playwright


URL = "https://consultapublica.antt.gov.br/Site/ConsultaRNTRC.aspx"

import os
from datetime import datetime


async def main():
    async with async_playwright() as p:
        print("Iniciando navegador...")

        navegador = await p.chromium.launch(
            headless=False,
            executable_path=r"C:\Program Files\Google\Chrome\Application\chrome.exe"
        )

        pagina = await navegador.new_page()
        await pagina.goto(URL)

        print("Página carregada.")

        # 1. Selecionar "Por Veículo"
        radio_veiculo = pagina.locator("#Corpo_rbTipoConsulta_2")

        await radio_veiculo.evaluate(
            "element => element.click()"
        )

        print("Consulta 'Por Veículo' selecionada.")

        await pagina.wait_for_timeout(3000)

        # 2. Localizar campos
        placa = pagina.locator("#Corpo_txtPlaca")
        rntrc = pagina.locator("#Corpo_txtRNTRC")
        cpf_cnpj = pagina.locator("#Corpo_txtCpfCnpj")

        # 3. Preencher campos
        await placa.fill("MBZ1I49")
        await rntrc.fill("055614433")

        print("Campos preenchidos.")

        # 4. Localizar ALTCHA
        altcha = pagina.locator("altcha-widget#altcha")

        if await altcha.count() == 0:
            print("ERRO: ALTCHA não encontrado.")

            await pagina.wait_for_timeout(30000)
            await navegador.close()

            return

        print("ALTCHA encontrado.")

        # 5. Localizar checkbox interno
        checkbox = altcha.locator("input[type='checkbox']")

        if await checkbox.count() > 0:
            print(
                "Checkbox encontrado:",
                await checkbox.is_visible()
            )

        # 6. Aguardar resolução manual do ALTCHA
        print("\nResolva o ALTCHA manualmente no navegador.")
        print("A automação ficará aguardando a validação.\n")

        # 7. Monitorar ALTCHA
        altcha_interno = altcha.locator(".altcha")

        for i in range(120):
            estado = await altcha_interno.get_attribute("data-state")

            checkbox = altcha.locator("input[type='checkbox']")
            checkbox_marcado = False

            if await checkbox.count() > 0:
                checkbox_marcado = await checkbox.is_checked()

            print(
                f"[{i + 1:03d}s] "
                f"estado={estado} | "
                f"checkbox={checkbox_marcado}"
            )

            if estado == "verified":
                print("\nALTCHA VALIDADO!\n")
                break

            await pagina.wait_for_timeout(1000)

        else:
            print("\nALTCHA não foi validado.")
            print("Estado final:", estado)
            print("Checkbox marcado:", checkbox_marcado)

            await pagina.wait_for_timeout(10000)
            await navegador.close()

            return

        # 8. Clicar em "Consultar"
        botao_consultar = pagina.locator("#Corpo_btnConsulta")

        if await botao_consultar.count() == 0:
            print("ERRO: botão 'Consultar' não encontrado.")

            await pagina.wait_for_timeout(10000)
            await navegador.close()

            return

        await botao_consultar.click()

        print("Consulta executada.")

        await pagina.wait_for_load_state("networkidle")
        await pagina.wait_for_timeout(2000)

        # 9. Diagnóstico do resultado
        print("\nResultado da consulta:")
        print("URL:", pagina.url)
        print("Título:", await pagina.title())

        caminho_screenshot = "resultado_consulta.png"

        await pagina.screenshot(
            path=caminho_screenshot,
            full_page=True
        )

        caminho_html = "resultado_consulta.html"
        conteudo_html = await pagina.content()

        with open(caminho_html, "w", encoding="utf-8") as arquivo:
            arquivo.write(conteudo_html)

        texto_pagina = await pagina.inner_text("body")

        termos_interessantes = [
            "apto",
            "não apto",
            "inapto"
        ]

        for termo in termos_interessantes:
            if termo.lower() in texto_pagina.lower():
                print(f"Encontrado: '{termo}'")

        # 10. Investigar "Avaliar Serviço"
        texto_avaliar = pagina.get_by_text(
            "AVALIAR SERVIÇO",
            exact=False
        )

        if await texto_avaliar.count() > 0:
            elemento_titulo = texto_avaliar.first

            painel_html = await elemento_titulo.evaluate(
                """
                el => {
                    let atual = el;

                    for (let nivel = 0; nivel < 4; nivel++) {
                        if (atual.parentElement) {
                            atual = atual.parentElement;
                        }
                    }

                    return atual.outerHTML;
                }
                """
            )

        # 11. Investigar "Imprimir Protocolo"
        botao_protocolo = pagina.locator("#Corpo_btnProtocolo")

        if await botao_protocolo.count() > 0:
            elemento_protocolo = botao_protocolo.first

            outer_html = await elemento_protocolo.evaluate(
                "el => el.outerHTML"
            )

            print("\nHTML do botão:")
            print(outer_html)

        # 12. Fechar painel "Avaliar Serviço"
        botao_fechar = pagina.locator(
            ".ui-dialog-titlebar-close"
        )

        if await botao_fechar.count() > 0:
            await botao_fechar.first.click()

            print("\nPainel 'Avaliar Serviço' fechado.")

            await pagina.wait_for_timeout(1000)

        # 13. Testar "Imprimir Protocolo"
        if await botao_protocolo.count() == 0:
            print("Botão 'Imprimir Protocolo' não encontrado.")

        else:
            paginas_antes = len(pagina.context.pages)

            print("\nClicando em 'Imprimir Protocolo'...")

            try:
                await botao_protocolo.click()
                print("Clique executado.")

            except Exception as erro:
                print("ERRO durante o clique:", erro)

            await pagina.wait_for_timeout(3000)

            paginas_depois = len(pagina.context.pages)

            print("\nResultado após o clique:")
            print("Quantidade de páginas antes:", paginas_antes)
            print("Quantidade de páginas depois:", paginas_depois)
            print("URL:", pagina.url)
            print("Título:", await pagina.title())

            # Verificar nova aba/janela
            if paginas_depois > paginas_antes:
                print("\nNova página/aba detectada!")

                nova_pagina = pagina.context.pages[-1]

                for indice, pagina_aberta in enumerate(
                    pagina.context.pages,
                    start=1
                ):
                    print(f"\nPágina {indice}:")
                    print("URL:", pagina_aberta.url)
                    print("Título:", await pagina_aberta.title())

                try:
                    await nova_pagina.wait_for_load_state(
                        "load",
                        timeout=15000
                    )
                except Exception as erro:
                    print("Aviso ao aguardar load:", erro)

                await nova_pagina.wait_for_timeout(1000)

                print("\nURL final da nova página:", nova_pagina.url)

                print("\n===================================")
                print("Capturando PDF...")
                print("===================================")

                try:
                    pasta_saida = "protocolos"
                    os.makedirs(pasta_saida, exist_ok=True)

                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    nome_arquivo = f"protocolo_055614433_MBZ1I49_{timestamp}.pdf"
                    caminho_pdf = os.path.join(pasta_saida, nome_arquivo)

                    print(f"Tentando requisitar: {nova_pagina.url}")

                    resposta = await pagina.context.request.get(nova_pagina.url)
                    print(f"Status da resposta: {resposta.status}")

                    pdf_bytes = await resposta.body()
                    print(f"Bytes recebidos: {len(pdf_bytes)}")
                    print(f"Primeiros 20 bytes: {pdf_bytes[:20]}")

                    if pdf_bytes[:4] != b"%PDF":
                        print("Primeira tentativa retornou HTML. Aguardando 2s e tentando novamente...")
                        await pagina.wait_for_timeout(2000)
                        resposta = await pagina.context.request.get(nova_pagina.url)
                        pdf_bytes = await resposta.body()
                        print(f"Bytes na segunda tentativa: {len(pdf_bytes)}")

                    with open(caminho_pdf, "wb") as arquivo_pdf:
                        arquivo_pdf.write(pdf_bytes)

                    print("PDF CAPTURADO")
                    print("===================================")
                    print("Caminho:", caminho_pdf)
                    print("Tamanho:", len(pdf_bytes), "bytes")

                    primeiros_bytes = pdf_bytes[:8]
                    eh_pdf = pdf_bytes[:4] == b"%PDF"

                    print("Primeiros bytes:", primeiros_bytes)
                    print("É PDF:", eh_pdf)

                except Exception as erro:
                    print("FALHA NA CAPTURA DO PDF")
                    print("===================================")
                    print("Motivo:", str(erro))
                    import traceback
                    traceback.print_exc()

            else:
                print("\nNenhuma nova página/aba detectada.")

            # Salvar HTML após o clique
            caminho_html_protocolo = "resultado_pos_imprimir.html"

            try:
                conteudo_html = await pagina.content()

                with open(
                    caminho_html_protocolo,
                    "w",
                    encoding="utf-8"
                ) as arquivo:
                    arquivo.write(conteudo_html)

                print(
                    "HTML pós-clique salvo em:",
                    caminho_html_protocolo
                )

            except Exception as erro:
                print(
                    "Erro ao salvar HTML pós-clique:",
                    erro
                )

        # 14. Manter navegador aberto para inspeção
        print("\nAutomação concluída.")
        print("O navegador permanecerá aberto por 60 segundos.")

        await pagina.wait_for_timeout(60000)
        await navegador.close()


asyncio.run(main())