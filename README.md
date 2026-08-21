# Automação de Consulta RNTRC - ANTT

Automação desenvolvida em Python para facilitar um processo de consulta de RNTRC que encontrei no meu trabalho.

O processo precisava ser realizado manualmente de tempos em tempos, envolvendo o preenchimento dos dados do veículo, validação do ALTCHA, realização da consulta e geração do protocolo. A partir desse problema, surgiu a ideia de desenvolver uma automação para tornar o processo mais rápido e reduzir tarefas repetitivas.

## Objetivo

Automatizar o processo de consulta de um veículo na Consulta Pública da ANTT, mantendo a validação do ALTCHA como uma etapa manual.

Atualmente, a automação é capaz de:

- Abrir a Consulta Pública da ANTT;
- Selecionar a consulta "Por Veículo";
- Preencher placa, RNTRC e CPF/CNPJ;
- Aguardar a validação manual do ALTCHA;
- Detectar quando o ALTCHA foi validado;
- Realizar a consulta;
- Identificar o resultado da consulta;
- Localizar e acionar o botão "Imprimir Protocolo";
- Detectar a nova aba contendo o protocolo em PDF.

## Tecnologias

- Python
- Playwright
- Chromium
- Git/GitHub

## Estrutura

```text
Automacao-antt/
├── main.py
├── requirements.txt
├── .gitignore
└── README.md
```
