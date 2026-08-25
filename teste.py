import asyncio
import re
import os

from playwright.async_api import async_playwright


URL = "https://consultapublica.antt.gov.br/Site/ConsultaRNTRC.aspx"


def normalizar_placa(placa: str) -> str:
    placa_limpa = re.sub(r"[^a-zA-Z0-9]", "", placa)
    return placa_limpa.upper()


def normalizar_documento(numero: str) -> str:
    return re.sub(r"\D", "", numero or "")


def coletar_dados_das_placas():
    """
    Etapa de coleta via CMD:
    - Pergunta quantas placas serão consultadas (máx: 4)
    - Para cada placa, pede a placa e o documento (RNTRC ou CPF/CNPJ)
    Retorna uma lista de dicts: [{"placa": ..., "rntrc": ..., "cpf_cnpj": ...}, ...]
    """
    while True:
        try:
            quantidade = int(input("Quantas placas serão consultadas? (max: 4): ").strip())
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
        documento_input = input("Insira Cnpf/Cpf ou RTRCN: ").strip()

        rntrc_normalizado = ""
        cpf_cnpj_normalizado = ""

        documento_normalizado_digitos = normalizar_documento(documento_input)

        # Mesma regra de negócio original: se vier no campo de RNTRC,
        # é RNTRC; senão, cai em CPF/CNPJ dependendo do tamanho.
        if len(documento_normalizado_digitos) == 9:
            rntrc_normalizado = documento_normalizado_digitos
        else:
            cpf_cnpj_normalizado = documento_normalizado_digitos

        consultas.append({
            "placa": normalizar_placa(placa_input),
            "rntrc": rntrc_normalizado,
            "cpf_cnpj": cpf_cnpj_normalizado,
        })

    return consultas


async def consultar_placa(pagina, dados_placa, pasta_protocolos):
    """
    Executa o fluxo completo de consulta para UMA placa, usando a mesma
    página (aba) do navegador. Preserva a lógica original de
    preenchimento, resolução do ALTCHA, clique em Consultar e captura
    do PDF via 'Imprimir Protocolo'.
    """
    placa_input_normalizado = dados_placa["placa"]
    rntrc_normalizado = dados_placa["rntrc"]
    cpf_cnpj_normalizado = dados_placa["cpf_cnpj"]

    print(f"\n========== Consultando placa: {placa_input_normalizado} ==========")

    await pagina.goto(URL)
    print("Página carregada.")

    # 1. Selecionar "Por Veículo"
    radio_veiculo = pagina.locator("#Corpo_rbTipoConsulta_2")
    await radio_veiculo.evaluate("element => element.click()")
    print("Consulta 'Por Veículo' selecionada.")

    await pagina.wait_for_timeout(3000)

    # 2. Localizar campos
    placa = pagina.locator("#Corpo_txtPlaca")
    rntrc = pagina.locator("#Corpo_txtRNTRC")
    cpf_cnpj = pagina.locator("#Corpo_txtCpfCnpj")

    # 3. Preencher campos
    if rntrc_normalizado:
        tipo_documento = "RNTRC"
        valor_documento = rntrc_normalizado
    elif cpf_cnpj_normalizado:
        tipo_documento = "CNPJ" if len(cpf_cnpj_normalizado) > 11 else "CPF"
        valor_documento = cpf_cnpj_normalizado
    else:
        tipo_documento = None
        valor_documento = None

    await placa.fill(placa_input_normalizado)

    if tipo_documento == "RNTRC":
        await rntrc.fill(valor_documento)
    elif tipo_documento in ("CPF", "CNPJ"):
        await cpf_cnpj.fill(valor_documento)
    else:
        print("ERRO: nenhum RNTRC ou CPF/CNPJ informado.")

    print(f"Campos preenchidos. Documento utilizado: {tipo_documento or 'nenhum'}")

    # 4. Localizar ALTCHA
    altcha = pagina.locator("altcha-widget#altcha")

    if await altcha.count() == 0:
        print("ERRO: ALTCHA não encontrado.")
        return False

    print("ALTCHA encontrado.")

    # 5. Localizar checkbox interno
    checkbox = altcha.locator("input[type='checkbox']")

    if await checkbox.count() > 0:
        print("Checkbox encontrado:", await checkbox.is_visible())

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

        print(f"[{i + 1:03d}s] estado={estado} | checkbox={checkbox_marcado}")

        if estado == "verified":
            print("\nALTCHA VALIDADO!\n")
            break

        await pagina.wait_for_timeout(1000)

    else:
        print("\nALTCHA não foi validado.")
        print("Estado final:", estado)
        print("Checkbox marcado:", checkbox_marcado)
        return False

    # 8. Clicar em "Consultar"
    botao_consultar = pagina.locator("#Corpo_btnConsulta")

    if await botao_consultar.count() == 0:
        print("ERRO: botão 'Consultar' não encontrado.")
        return False

    await botao_consultar.click()
    print("Consulta executada.")

    await pagina.wait_for_load_state("networkidle")
    await pagina.wait_for_timeout(2000)

    print("\nResultado da consulta:")
    print("URL:", pagina.url)
    print("Título:", await pagina.title())

    texto_pagina = await pagina.inner_text("body")

    termos_interessantes = ["apto", "não apto", "inapto"]

    for termo in termos_interessantes:
        if termo.lower() in texto_pagina.lower():
            print(f"Encontrado: '{termo}'")

    # 9. "Imprimir Protocolo"
    botao_protocolo = pagina.locator("#Corpo_btnProtocolo")

    # 10. Fechar painel "Avaliar Serviço" (se existir)
    botao_fechar = pagina.locator(".ui-dialog-titlebar-close")

    if await botao_fechar.count() > 0:
        await botao_fechar.first.click()
        print("\nPainel 'Avaliar Serviço' fechado.")
        await pagina.wait_for_timeout(1000)

    if await botao_protocolo.count() == 0:
        print("Botão 'Imprimir Protocolo' não encontrado.")
        return False

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

    # Listener no contexto inteiro (cobre a página original)
    pagina.context.on("response", capturar_resposta)

    nova_pagina = None

    try:
        async with pagina.context.expect_page() as info_nova_pagina:
            await botao_protocolo.click()

        nova_pagina = await info_nova_pagina.value

        print("Clique executado.")
        print("Nova aba aberta.")

        # Listener dedicado na nova aba: a resposta do AbrePDF.aspx
        # pertence a essa aba, então escutamos diretamente nela também,
        # em vez de depender apenas do listener do contexto.
        nova_pagina.on("response", capturar_resposta)

        try:
            await nova_pagina.wait_for_load_state("load", timeout=15000)
        except Exception:
            pass

        print("URL da nova aba:", nova_pagina.url)

        # Espera ativa, verificando periodicamente se o PDF já foi
        # capturado por algum dos dois listeners, em vez de um único
        # sleep fixo às cegas.
        tentativas = 0
        while pdf_bytes_capturado is None and tentativas < 15:
            await pagina.wait_for_timeout(500)
            tentativas += 1

        # Fallback: se nenhum listener capturou (ex.: a resposta ocorreu
        # antes dos listeners serem registrados), tenta buscar a mesma
        # URL diretamente via requisição HTTP dentro do contexto.
        if pdf_bytes_capturado is None and "AbrePDF.aspx" in nova_pagina.url:
            try:
                resposta_direta = await pagina.context.request.get(nova_pagina.url)
                corpo_direto = await resposta_direta.body()

                if corpo_direto[:4] == b"%PDF":
                    pdf_bytes_capturado = corpo_direto

                    print("\n================================")
                    print(">>> PDF CAPTURADO (fallback direto)!")
                    print("================================")
                    print("Tamanho:", len(corpo_direto), "bytes")
            except Exception as erro_fallback:
                print("Fallback direto falhou:", erro_fallback)

    except Exception as erro:
        print("Erro ao abrir o protocolo:", erro)

    finally:
        pagina.context.remove_listener("response", capturar_resposta)

        if nova_pagina is not None:
            try:
                nova_pagina.remove_listener("response", capturar_resposta)
            except Exception:
                pass

            await nova_pagina.close()

    # Salvar PDF capturado
    if pdf_bytes_capturado is not None:
        nome_arquivo = f"{placa_input_normalizado} ANTT.pdf"
        caminho_pdf = os.path.join(pasta_protocolos, nome_arquivo)

        with open(caminho_pdf, "wb") as arquivo:
            arquivo.write(pdf_bytes_capturado)

        print("\n================================")
        print(">>> PDF SALVO COM SUCESSO!")
        print("================================")
        print("Caminho:", caminho_pdf)
        print("Tamanho:", len(pdf_bytes_capturado), "bytes")

        return True

    else:
        print("\n================================")
        print(">>> PDF NÃO FOI CAPTURADO (resposta pode ter sido HTML/expirada)")
        print("================================")
        return False


async def main():
    pasta_protocolos = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "protocolos"
    )
    os.makedirs(pasta_protocolos, exist_ok=True)

    consultas = coletar_dados_das_placas()

    resultados = []

    async with async_playwright() as p:
        print("\nIniciando navegador...")

        navegador = await p.chromium.launch(
            headless=False,
            executable_path=r"C:\Program Files\Google\Chrome\Application\chrome.exe"
        )

        pagina = await navegador.new_page()

        for dados_placa in consultas:
            sucesso = await consultar_placa(pagina, dados_placa, pasta_protocolos)
            resultados.append((dados_placa["placa"], sucesso))

        print("\nTodas as consultas foram processadas.")
        print("O navegador permanecerá aberto por 60 segundos.")

        await pagina.wait_for_timeout(60000)
        await navegador.close()

    print("\n========== RESUMO ==========")
    for placa, sucesso in resultados:
        status = "OK - PDF salvo" if sucesso else "FALHOU"
        print(f"{placa}: {status}")


if __name__ == "__main__":
    asyncio.run(main())