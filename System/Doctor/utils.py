from datetime import datetime, timedelta

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

    week_start = today_date - timedelta(days=today_date.weekday())

    days_of_week = []
    for i in range(6): 
        day = week_start + timedelta(days=i)
        days_of_week.append({
            'name': obtener_dia_semana_espanol(day.strftime('%A')),
            'number': obtener_numero_dia(day),
            'date': day.strftime('%Y-%m-%d')
        })

    hours_of_day = [
        '09:00:00', '09:30:00', '10:00:00', '10:30:00', '11:00:00', '11:30:00', '12:00:00', '12:30:00',
        '13:00:00', '13:30:00', '14:00:00', '14:30:00', '15:00:00', '15:30:00', '16:00:00', '16:30:00',
        '17:00:00', '17:30:00', '18:00:00', '18:30:00', '19:00:00', '19:30:00', '20:00:00'
    ]

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