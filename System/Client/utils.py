from datetime import datetime, timedelta
import jinja2
import pdfkit
import os
from django.conf import settings

def obtener_dia_semana_espanol(day_name):
    dias = {
        'Monday': 'Lunes',
        'Tuesday': 'Martes',
        'Wednesday': 'Miércoles',
        'Thursday': 'Jueves',
        'Friday': 'Viernes',
        'Saturday': 'Sábado',
        'Sunday': 'Domingo'
    }
    return dias.get(day_name, day_name)

def obtener_fecha_texto():
    now = datetime.now()
    
    nombre_mes = now.strftime('%B')
    dia = now.strftime('%d')
    año = now.strftime('%Y')
    
    texto_fecha = f"{nombre_mes}, {dia} - {año}"
    
    return texto_fecha

def obtener_numero_dia(dia):
    return dia.strftime('%d')

def preparar_contexto_citas(citas):
    today = datetime.today()
    day_current = today.strftime('%A')
    today_date = today.date()

    # Filtrar citas para la semana actual
    week_start = today_date - timedelta(days=today_date.weekday())

    days_of_week = []
    for i in range(6):  # Ajustado a 7 días para incluir el domingo
        day = week_start + timedelta(days=i)
        days_of_week.append({
            'name': obtener_dia_semana_espanol(day.strftime('%A')),
            'number': obtener_numero_dia(day),
            'date': day.strftime('%Y-%m-%d')
        })

    # Horarios disponibles
    hours_of_day = [
        '09:00:00', '09:30:00', '10:00:00', '10:30:00', '11:00:00', '11:30:00', '12:00:00', '12:30:00',
        '13:00:00', '13:30:00', '14:00:00', '14:30:00', '15:00:00', '15:30:00', '16:00:00', '16:30:00',
        '17:00:00', '17:30:00', '18:00:00', '18:30:00', '19:00:00', '19:30:00', '20:00:00'
    ]

    # Crear una estructura de tabla de horarios
    schedule_table = []

    for hour in hours_of_day:
        row = {'hour': hour, 'slots': []}
        for day in days_of_week:
            citas_en_hora_y_dia = citas.filter(hora_inicio__startswith=hour, fecha=day['date'])
            row['slots'].append(citas_en_hora_y_dia)

        schedule_table.append(row)

    contexto = {
        'days_of_week': days_of_week,
        'schedule_table': schedule_table,
        'day_current': obtener_dia_semana_espanol(day_current),
        'today': obtener_fecha_texto()
    }

    return contexto

def create_pdf(ruta_template, info, rutacss=''):
    nombre_template = os.path.basename(ruta_template)
    ruta_template_dir = os.path.dirname(ruta_template)
    
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(ruta_template_dir))
    template = env.get_template(nombre_template)
    html = template.render(info)    
    options = {
        'page-size': 'A4',
        'margin-top': '0.5in',
        'margin-right': '0.5in',
        'margin-bottom': '0.5in',
        'margin-left': '0.5in',
        'encoding': 'UTF-8',
    }
    
    config = pdfkit.configuration(wkhtmltopdf="C:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe")
    
    ruta_salida = os.path.join(settings.STATICFILES_DIRS[0], 'pdf', 'resultado.pdf')
    pdfkit.from_string(html, ruta_salida, css=rutacss if rutacss else None, options=options, configuration=config)
    return ruta_salida