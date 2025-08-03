from sqlalchemy import extract
from datetime import datetime, timezone
import pytz

def format_datetime_local(dt):
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    
    local_tz = pytz.timezone('America/Sao_Paulo')
    local_dt = dt.astimezone(local_tz)
    return local_dt.strftime('%d/%m/%y %H:%M')

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
