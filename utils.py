from sqlalchemy import extract
from escpos.printer import Usb
from datetime import datetime
import os

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
    
def imprimir_notinha(servico):
    # Dados da loja via env
    cnpj = os.getenv("CNPJ_LOJA", "00.000.000/0000-00")
    nome_loja = os.getenv("NOME_LOJA", "Minha Loja")
    tel_loja = os.getenv("TEL_LOJA", "00 99999-9999")

    # IDs da sua impressora térmica (descubra com `lsusb`)
    vendor_id = int(os.getenv("PRINTER_VENDOR_ID", "0x04b8"), 16)
    product_id = int(os.getenv("PRINTER_PRODUCT_ID", "0x0202"), 16)
    p = Usb(vendor_id, product_id)  # Substitua pelo ID correto da sua impressora

    p.set(align='center', bold=True)
    p.text(f"{nome_loja}\n")
    p.text(f"CNPJ: {cnpj}\n")
    p.text(f"TELEFONE: {tel_loja}\n")
    p.text("-" * 32 + "\n")

    p.set(align='left')
    p.text(f"Data/Hora: {servico.data_hora.strftime('%d/%m/%Y %H:%M')}\n")
    p.text(f"Serviço: {servico.servico_descricao}\n")
    p.text(f"Aparelho: {servico.aparelho}\n")
    p.text(f"Tipo: {servico.tipo}\n")

    if servico.tipo == "Venda de Aparelho":
        valor = servico.preco_aparelho
    else:
        valor = servico.custo_pecas + servico.mao_de_obra

    p.text(f"Valor: R$ {valor:.2f}\n")
    p.text(f"Pagamento: {servico.forma_pagamento}\n")
    p.text(f"Cliente: {servico.cliente}\n")

    p.text("-" * 32 + "\n")
    p.text("Obrigado pela preferência!\n")
    p.cut()
