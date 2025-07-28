from sqlalchemy import extract

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
