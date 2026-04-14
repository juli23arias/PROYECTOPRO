from datetime import timedelta

def add_business_days(start_date, total_days):
    """
    Calcula la fecha de fin sumando N días hábiles (Lunes a Viernes).
    Si total_days es 1, la fecha de fin es el mismo start_date (si es día hábil).
    Si start_date es fin de semana, comienza a contar desde el próximo lunes.
    """
    if total_days <= 0:
        return start_date
        
    current_date = start_date
    # Si el inicio es fin de semana, saltar al lunes
    while current_date.weekday() >= 5:
        current_date += timedelta(days=1)
        
    days_counted = 1
    while days_counted < total_days:
        current_date += timedelta(days=1)
        if current_date.weekday() < 5:
            days_counted += 1
            
    return current_date
