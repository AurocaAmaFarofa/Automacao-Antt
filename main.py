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
        placa_input = "QIO5C12"
        rntrc_input = "050069322"

        await placa.fill(placa_input)
        await rntrc.fill(rntrc_input)

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
            print("\nClicando em 'Imprimir Protocolo'...")

            pdf_bytes_capturado = None

            async def capturar_resposta(response):
                nonlocal pdf_bytes_capturado

                if pdf_bytes_capturado is not None:
                    return

                try:
                    corpo = await response.body()
                except Exception:
                    return

                if corpo[:4] == b"%PDF":
                    pdf_bytes_capturado = corpo

                    print("\n================================")
                    print(">>> PDF REAL CAPTURADO!")
                    print("================================")
                    print("URL:", response.url)
                    print("Status:", response.status)
                    print("Tamanho:", len(corpo), "bytes")

            # Registra o listener ANTES do clique
            pagina.context.on("response", capturar_resposta)

            try:
                async with pagina.context.expect_page() as info_nova_pagina:
                    await botao_protocolo.click()

                nova_pagina = await info_nova_pagina.value

                print("Clique executado.")
                print("Nova aba aberta.")
                print("URL da nova aba:", nova_pagina.url)

                await nova_pagina.wait_for_load_state(
                    "load",
                    timeout=15000
                )

                # Dá tempo para a resposta do PDF ser capturada
                await pagina.wait_for_timeout(3000)

            except Exception as erro:
                print("Erro ao abrir o protocolo:", erro)

            finally:
                pagina.context.remove_listener(
                    "response",
                    capturar_resposta
                )

            # Salvar PDF capturado
            if pdf_bytes_capturado is not None:

                pasta_protocolos = "protocolos"

                os.makedirs(
                    pasta_protocolos,
                    exist_ok=True
                )

                nome_arquivo = f"protocolo_{placa_input}_{rntrc_input}.pdf"

                caminho_pdf = os.path.join(
                    pasta_protocolos,
                    nome_arquivo
                )

                with open(caminho_pdf, "wb") as arquivo:
                    arquivo.write(pdf_bytes_capturado)

                print("\n================================")
                print(">>> PDF SALVO COM SUCESSO!")
                print("================================")
                print("Caminho:", caminho_pdf)
                print("Tamanho:", len(pdf_bytes_capturado), "bytes")

            else:
                print("\n================================")
                print(">>> PDF NÃO FOI CAPTURADO")
                print("================================")

        # 14. Manter navegador aberto para inspeção
        print("\nAutomação concluída.")
        print("O navegador permanecerá aberto por 60 segundos.")

        await pagina.wait_for_timeout(60000)
        await navegador.close()

asyncio.run(main())