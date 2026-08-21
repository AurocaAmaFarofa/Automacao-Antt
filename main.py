import asyncio

from playwright.async_api import async_playwright


URL = "https://consultapublica.antt.gov.br/Site/ConsultaRNTRC.aspx"


async def main():

    async with async_playwright() as p:

        print("Iniciando navegador...")

        navegador = await p.chromium.launch(
            headless=False,
            executable_path=r"C:\Program Files\Google\Chrome\Application\chrome.exe"
        )

        pagina = await navegador.new_page()

        await pagina.goto(URL)

        print("\n===================================")
        print("PÁGINA CARREGADA")
        print("===================================\n")


        # ==========================================================
        # 1. SELECIONAR "POR VEÍCULO"
        # ==========================================================

        radio_veiculo = pagina.locator("#Corpo_rbTipoConsulta_2")

        print("Elemento encontrado:", await radio_veiculo.count())
        print("Visível:", await radio_veiculo.is_visible())
        print("Habilitado:", await radio_veiculo.is_enabled())
        print("Selecionado antes:", await radio_veiculo.is_checked())

        print("\nTentando selecionar 'Por Veículo'...")

        await radio_veiculo.evaluate(
            "element => element.click()"
        )

        print("Clique executado pelo JavaScript.")

        await pagina.wait_for_timeout(3000)

        print("Selecionado depois:", await radio_veiculo.is_checked())


        # ==========================================================
        # 2. LOCALIZAR CAMPOS
        # ==========================================================

        print("\n===================================")
        print("VERIFICANDO CAMPOS")
        print("===================================\n")

        placa = pagina.locator("#Corpo_txtPlaca")
        rntrc = pagina.locator("#Corpo_txtRNTRC")
        cpf_cnpj = pagina.locator("#Corpo_txtCpfCnpj")

        print("Placa encontrada:", await placa.count())
        print("Placa visível:", await placa.is_visible())

        print("RNTRC encontrado:", await rntrc.count())
        print("RNTRC visível:", await rntrc.is_visible())

        print("CPF/CNPJ encontrado:", await cpf_cnpj.count())
        print("CPF/CNPJ visível:", await cpf_cnpj.is_visible())


        # ==========================================================
        # 3. PREENCHER CAMPOS
        # ==========================================================

        print("\n===================================")
        print("PREENCHENDO CAMPOS")
        print("===================================\n")

        await placa.fill("MBZ1I49")
        await rntrc.fill("055614433")

        print(
            "Placa preenchida:",
            await placa.input_value()
        )

        print(
            "RNTRC preenchido:",
            await rntrc.input_value()
        )

        print(
            "CPF/CNPJ preenchido:",
            await cpf_cnpj.input_value()
        )


        # ==========================================================
        # 4. LOCALIZAR ALTCHA
        # ==========================================================

        print("\n===================================")
        print("LOCALIZANDO ALTCHA")
        print("===================================\n")

        altcha = pagina.locator("altcha-widget#altcha")

        print("ALTCHA encontrado:", await altcha.count())

        if await altcha.count() == 0:

            print("ERRO: ALTCHA não encontrado.")

            await pagina.wait_for_timeout(30000)

            await navegador.close()

            return


        print("ALTCHA visível:", await altcha.is_visible())


        # ==========================================================
        # 5. LOCALIZAR CHECKBOX INTERNO
        # ==========================================================

        print("\n===================================")
        print("CHECKBOX ALTCHA")
        print("===================================\n")

        checkbox = altcha.locator("input[type='checkbox']")

        print(
            "Checkbox encontrado:",
            await checkbox.count()
        )

        if await checkbox.count() > 0:

            print(
                "Checkbox visível:",
                await checkbox.is_visible()
            )

            print(
                "Checkbox marcado:",
                await checkbox.is_checked()
            )


        # ==========================================================
        # 6. PAUSAR PARA RESOLVER ALTCHA MANUALMENTE
        # ==========================================================

        print("\n===================================")
        print("AÇÃO MANUAL NECESSÁRIA")
        print("===================================\n")

        print("A janela do Chrome está aberta.")
        print("Clique em:")
        print()
        print("    [ ] Eu não sou um robô")
        print()
        print("Resolva o ALTCHA manualmente.")
        print("O programa ficará aguardando a validação.\n")


        # ==========================================================
        # 7. AGUARDAR ALTCHA SER VALIDADO
        # ==========================================================

        print("\n")
        print("===================================")
        print("MONITORANDO ALTCHA")
        print("===================================\n")

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

                print("\n===================================")
                print("ALTCHA VALIDADO!")
                print("===================================\n")

                break

            await pagina.wait_for_timeout(1000)

        else:

            print("\n===================================")
            print("ALTCHA NÃO FOI DETECTADO COMO VALIDADO")
            print("===================================\n")

            print("Estado final:", estado)
            print("Checkbox marcado:", checkbox_marcado)

            await pagina.wait_for_timeout(10000)

            await navegador.close()

            return


        # ==========================================================
        # 8. CLICAR EM "CONSULTAR" E DIAGNOSTICAR O RESULTADO
        # ==========================================================

        print("\n===================================")
        print("CLICANDO EM 'CONSULTAR'")
        print("===================================\n")

        botao_consultar = pagina.locator("#Corpo_btnConsulta")

        if await botao_consultar.count() == 0:

            print("ERRO: Botão 'Consultar' não encontrado.")

            await pagina.wait_for_timeout(10000)

            await navegador.close()

            return

        await botao_consultar.click()

        print("Clique em 'Consultar' executado.")

        await pagina.wait_for_load_state("networkidle")

        await pagina.wait_for_timeout(2000)

        print("\n===================================")
        print("DIAGNÓSTICO PÓS-CONSULTA")
        print("===================================\n")

        print("URL atual:", pagina.url)
        print("Título da página:", await pagina.title())

        caminho_screenshot = "resultado_consulta.png"

        await pagina.screenshot(path=caminho_screenshot, full_page=True)

        print("Screenshot salvo em:", caminho_screenshot)

        caminho_html = "resultado_consulta.html"

        conteudo_html = await pagina.content()

        with open(caminho_html, "w", encoding="utf-8") as arquivo:
            arquivo.write(conteudo_html)

        print("HTML salvo em:", caminho_html)

        texto_pagina = await pagina.inner_text("body")

        termos_interessantes = ["apto", "não apto", "inapto", "APTO", "INAPTO"]

        print("\nOcorrências de termos de interesse no texto da página:")

        for termo in termos_interessantes:
            if termo.lower() in texto_pagina.lower():
                print(f" - Encontrado: '{termo}'")

        botao_imprimir = pagina.get_by_text("Imprimir", exact=False)

        quantidade_imprimir = await botao_imprimir.count()

        print("\nOcorrências de elementos com texto 'Imprimir':", quantidade_imprimir)

        for i in range(quantidade_imprimir):

            elemento = botao_imprimir.nth(i)

            try:

                tag = await elemento.evaluate("el => el.tagName")
                visivel = await elemento.is_visible()

                print(f" - Elemento {i + 1}: tag={tag}, visível={visivel}")

            except Exception as erro:

                print(f" - Elemento {i + 1}: erro ao inspecionar ({erro})")

        print("\n===================================")
        print("DIAGNÓSTICO CONCLUÍDO")
        print("===================================\n")


        # ==========================================================
        # 8.1 INVESTIGAR PAINEL "AVALIAR SERVIÇO" (SEM CLICAR)
        # ==========================================================

        print("\n===================================")
        print("INVESTIGANDO PAINEL 'AVALIAR SERVIÇO'")
        print("===================================\n")

        texto_avaliar = pagina.get_by_text("AVALIAR SERVIÇO", exact=False)

        quantidade_avaliar = await texto_avaliar.count()

        print("Ocorrências do texto 'AVALIAR SERVIÇO':", quantidade_avaliar)

        if quantidade_avaliar > 0:

            elemento_titulo = texto_avaliar.first

            visivel_titulo = await elemento_titulo.is_visible()

            print("Visível:", visivel_titulo)

            # Sobe alguns níveis na árvore DOM para capturar o painel inteiro,
            # incluindo o "quadrado" no canto (provável botão de fechar).

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

            print("\nHTML do painel (subindo 4 níveis a partir do título):")
            print(painel_html)

        else:

            print("Painel 'AVALIAR SERVIÇO' não apareceu desta vez (ok, pode ser esperado).")


        # ==========================================================
        # 8.2 INVESTIGAR BOTÃO "IMPRIMIR PROTOCOLO" (SEM CLICAR)
        # ==========================================================

        print("\n===================================")
        print("INVESTIGANDO BOTÃO 'IMPRIMIR PROTOCOLO'")
        print("===================================\n")

        botao_imprimir_protocolo = pagina.get_by_text("Imprimir Protocolo", exact=False)

        quantidade_imprimir_protocolo = await botao_imprimir_protocolo.count()

        print("Ocorrências de 'Imprimir Protocolo':", quantidade_imprimir_protocolo)

        if quantidade_imprimir_protocolo > 0:

            elemento_imprimir = botao_imprimir_protocolo.first

            print("Visível:", await elemento_imprimir.is_visible())
            print("Tag:", await elemento_imprimir.evaluate("el => el.tagName"))
            print("ID:", await elemento_imprimir.get_attribute("id"))
            print("Name:", await elemento_imprimir.get_attribute("name"))
            print("Onclick:", await elemento_imprimir.get_attribute("onclick"))
            print("Target:", await elemento_imprimir.get_attribute("target"))
            print("Href:", await elemento_imprimir.get_attribute("href"))

            outer_html_imprimir = await elemento_imprimir.evaluate("el => el.outerHTML")

            print("\nOuterHTML do botão 'Imprimir Protocolo':")
            print(outer_html_imprimir)

        else:

            print("Botão 'Imprimir Protocolo' não encontrado desta vez.")

        print("\n===================================")
        print("INVESTIGAÇÃO CONCLUÍDA (NENHUM CLIQUE NOS DOIS ELEMENTOS)")
        print("===================================\n")


                # ==========================================================
        # 9. FECHAR PAINEL "AVALIAR SERVIÇO"
        # ==========================================================
        print("\n===================================")
        print("FECHANDO PAINEL 'AVALIAR SERVIÇO'")
        print("===================================\n")

        botao_fechar_avaliacao = pagina.locator(
            ".ui-dialog-titlebar-close"
        )

        quantidade_fechar = await botao_fechar_avaliacao.count()

        print(
            "Botões de fechar encontrados:",
            quantidade_fechar
        )

        if quantidade_fechar > 0:

            print(
                "Botão de fechar visível:",
                await botao_fechar_avaliacao.first.is_visible()
            )

            await botao_fechar_avaliacao.first.click()

            print("Clique no botão de fechar executado.")

            await pagina.wait_for_timeout(1000)

            modal_restante = pagina.locator(
                "#divAvaliacao"
            )

            if await modal_restante.count() > 0:
                print(
                    "Modal ainda existe no DOM."
                )

                try:
                    print(
                        "Modal visível:",
                        await modal_restante.is_visible()
                    )
                except Exception as erro:
                    print(
                        "Não foi possível verificar visibilidade:",
                        erro
                    )
            else:
                print(
                    "Modal não encontrado no DOM."
                )

        else:
            print(
                "Botão de fechar não encontrado."
            )


        # ==========================================================
        # 10. INVESTIGAR CLIQUE EM "IMPRIMIR PROTOCOLO"
        # ==========================================================
        print("\n===================================")
        print("TESTANDO 'IMPRIMIR PROTOCOLO'")
        print("===================================\n")

        botao_protocolo = pagina.locator(
            "#Corpo_btnProtocolo"
        )

        quantidade_protocolo = await botao_protocolo.count()

        print(
            "Botões 'Imprimir Protocolo' encontrados:",
            quantidade_protocolo
        )

        if quantidade_protocolo == 0:

            print(
                "ERRO: botão 'Imprimir Protocolo' não encontrado."
            )

        else:

            print(
                "Visível:",
                await botao_protocolo.is_visible()
            )

            print(
                "Habilitado:",
                await botao_protocolo.is_enabled()
            )

            print(
                "URL antes do clique:",
                pagina.url
            )

            quantidade_paginas_antes = len(
                pagina.context.pages
            )

            print(
                "Quantidade de páginas antes:",
                quantidade_paginas_antes
            )

            # ------------------------------------------------------
            # O objetivo desta etapa é APENAS descobrir o
            # comportamento do botão.
            # ------------------------------------------------------

            print("\nClicando em 'Imprimir Protocolo'...")

            try:

                await botao_protocolo.click()

                print(
                    "Clique executado."
                )

            except Exception as erro:

                print(
                    "ERRO durante o clique:",
                    erro
                )

            # ------------------------------------------------------
            # Dar tempo para o comportamento do postback acontecer.
            # ------------------------------------------------------

            await pagina.wait_for_timeout(3000)

            quantidade_paginas_depois = len(
                pagina.context.pages
            )

            print("\n-----------------------------------")
            print("DIAGNÓSTICO APÓS O CLIQUE")
            print("-----------------------------------\n")

            print(
                "Quantidade de páginas depois:",
                quantidade_paginas_depois
            )

            print(
                "URL da página original:",
                pagina.url
            )

            print(
                "Título da página original:",
                await pagina.title()
            )

            # ------------------------------------------------------
            # Verificar se apareceu uma nova aba/janela
            # ------------------------------------------------------

            if quantidade_paginas_depois > quantidade_paginas_antes:

                print(
                    "\nNOVA PÁGINA/ABA DETECTADA!"
                )

                for indice, pagina_aberta in enumerate(
                    pagina.context.pages,
                    start=1
                ):

                    print(
                        f"\nPágina {indice}:"
                    )

                    try:
                        print(
                            "URL:",
                            pagina_aberta.url
                        )

                        print(
                            "Título:",
                            await pagina_aberta.title()
                        )

                    except Exception as erro:

                        print(
                            "Erro ao inspecionar página:",
                            erro
                        )

            else:

                print(
                    "\nNenhuma nova página/aba foi detectada."
                )

                print(
                    "O botão provavelmente processou o postback "
                    "na própria página ou iniciou outro comportamento."
                )

            # ------------------------------------------------------
            # Verificar se a resposta atual parece ser PDF
            # ------------------------------------------------------

            print("\n-----------------------------------")
            print("VERIFICANDO RESULTADO")
            print("-----------------------------------\n")

            try:

                conteudo_atual = await pagina.content()

                print(
                    "HTML atual obtido com sucesso."
                )

                if "%PDF" in conteudo_atual:

                    print(
                        "ATENÇÃO: encontrado marcador de PDF no conteúdo."
                    )

                else:

                    print(
                        "Nenhum marcador '%PDF' encontrado no HTML."
                    )

            except Exception as erro:

                print(
                    "Erro ao obter conteúdo atual:",
                    erro
                )

            # ------------------------------------------------------
            # Salvar estado após o clique
            # ------------------------------------------------------

            caminho_html_protocolo = (
                "resultado_pos_imprimir.html"
            )

            try:

                conteudo_html_protocolo = (
                    await pagina.content()
                )

                with open(
                    caminho_html_protocolo,
                    "w",
                    encoding="utf-8"
                ) as arquivo:

                    arquivo.write(
                        conteudo_html_protocolo
                    )

                print(
                    "HTML pós-clique salvo em:",
                    caminho_html_protocolo
                )

            except Exception as erro:

                print(
                    "Erro ao salvar HTML pós-clique:",
                    erro
                )


        # ==========================================================
        # 11. DEIXAR A AUTOMAÇÃO ABERTA PARA INSPEÇÃO
        # ==========================================================
        print("\n===================================")
        print("AUTOMAÇÃO PAUSADA")
        print("===================================\n")

        print(
            "A consulta foi realizada e o teste do "
            "'Imprimir Protocolo' foi executado."
        )

        print(
            "A página permanecerá aberta por 60 segundos."
        )

        await pagina.wait_for_timeout(60000)

        await navegador.close()


asyncio.run(main())