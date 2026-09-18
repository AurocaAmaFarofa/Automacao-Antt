import json
import os

NOME_ARQUIVO = "config.json"

def obter_caminho_config():
    pasta = os.path.join(
        os.environ.get(
            "LOCALAPPDATA",
            os.path.expanduser("~")
        ),
        "AnttAutomator"
    )

    os.makedirs(pasta, exist_ok=True)

    return os.path.join(
        pasta,
        NOME_ARQUIVO
    )



def salvar_configuracao(caminho_chrome, pasta_destino):
    configuracao = {
        "chrome": caminho_chrome,
        "pasta_destino": pasta_destino
    }

    caminho_config = obter_caminho_config()

    with open(caminho_config, "w", encoding="utf-8") as arquivo:
        json.dump(configuracao, arquivo, indent=4)


def carregar_configuracao():
    caminho_config = obter_caminho_config()

    if not os.path.exists(caminho_config):
        return {}

    try:
        with open(caminho_config, "r", encoding="utf-8") as arquivo:
            return json.load(arquivo)

    except (json.JSONDecodeError, OSError):
        return {}