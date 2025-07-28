from sqlalchemy import extract
from escpos.printer import Usb
from datetime import datetime
import os
import tempfile
import win32api

def filtros_data(model, data_field, dia=None, mes=None, ano=None):
    filtros = []
    if mes:
        filtros.append(extract('month', getattr(model, data_field)) == mes)
    if ano:
        filtros.append(extract('year', getattr(model, data_field)) == ano)
    if dia:
        filtros.append(extract('day', getattr(model, data_field)) == dia)
    return filtros

def to_float(valor, default=0.0):
    try:
        return float(valor)
    except (TypeError, ValueError):
        return default




def gerar_notinha_txt(servico):
    nome_loja = os.getenv("NOME_LOJA", "Minha Loja")
    cnpj = os.getenv("CNPJ_LOJA", "00.000.000/0000-00")
    telefone = os.getenv("TEL_LOJA", "00 00000-0000")

    if servico.tipo == "Venda de Aparelho":
        valor = servico.preco_aparelho
    else:
        valor = servico.custo_pecas + servico.mao_de_obra

    conteudo = f"""
{nome_loja.center(32)}
CNPJ: {cnpj}
TEL: {telefone}
{'-'*32}
Data/Hora: {servico.data_hora.strftime('%d/%m/%Y %H:%M')}
Serviço: {servico.servico_descricao}
Aparelho: {servico.aparelho}
Tipo: {servico.tipo}
Valor: R$ {valor:.2f}
Pagamento: {servico.forma_pagamento}
Cliente: {servico.cliente}
{'-'*32}
Obrigado pela preferência!
    """.strip()
    return conteudo


def imprimir_notinha(servico):
    try:
        conteudo = gerar_notinha_txt(servico)
        nome_impressora = os.getenv("NOME_IMPRESSORA", "POS-58")

        # Cria arquivo temporário
        with tempfile.NamedTemporaryFile(delete=False, suffix=".txt", mode="w", encoding="utf-8") as tmp:
            tmp.write(conteudo)
            caminho = tmp.name

        # Imprime diretamente na impressora POS-58
        win32api.ShellExecute(
            0,
            "printto",
            caminho,
            f'"{nome_impressora}"',
            ".",
            0
        )
        return True, "Impressão enviada com sucesso."
    except Exception as e:
        return False, f"Erro ao imprimir: {str(e)}"