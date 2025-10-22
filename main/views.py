# main/views.py
import calendar
from datetime import datetime, date
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json

from .models import CoffeeShop, Shift, Worker

def get_schedule_data(request, cafe_id):
    try:
        cafe = get_object_or_404(CoffeeShop, id=cafe_id)
        today = date.today()
        year = today.year
        month = today.month

        # количество дней в месяце
        days_in_month = calendar.monthrange(year, month)[1]
        first_weekday = calendar.monthrange(year, month)[0]  # 0 = понедельник

        # заголовок дни месяца + день недели
        weekdays = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']
        header = []
        for day in range(1, days_in_month + 1):
            weekday_index = (first_weekday + day - 1) % 7
            header.append({'day': day, 'weekday': weekdays[weekday_index], 'date': f"{year}-{month:02d}-{day:02d}"})

        workers = Worker.objects.filter(coffee_shop=cafe)

        shifts_by_worker_and_date = {}
        for shift in Shift.objects.filter(worker__in=workers, date__year=year, date__month=month):
            shifts_by_worker_and_date[(shift.worker_id, shift.date)] = shift.start_time


        worker_count_per_day = {}
        for day in range(1, days_in_month + 1):
            d = date(year, month, day)
            count = Shift.objects.filter(coffee_shop=cafe, date=d, start_time__isnull=False).count()
            worker_count_per_day[d] = count

        
        rows = []
        for worker in workers:
            row_data = []
            for day_info in header:
                d = day_info['date']
                start_time = shifts_by_worker_and_date.get((worker.id, date.fromisoformat(d)))
                row_data.append(start_time)
            rows.append({
                'id': worker.id,
                'name': worker.name,
                'data': row_data
            })

        
        red_days = [
            day_info['day'] for day_info in header
            if worker_count_per_day.get(date.fromisoformat(day_info['date']), 0) < cafe.minimum_workers
        ]

        return JsonResponse({
                'cafe_name': cafe.name,
                'header': header,
                'rows': rows,
                'red_days': red_days,
                'minimum_required': cafe.minimum_workers,
            })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
def update_shift(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST allowed'}, status=405)

    try:
        data = json.loads(request.body)
        worker_id = data['worker_id']
        date_str = data['date']
        start_time = data.get('start_time')

        worker = Worker.objects.get(id=worker_id)
        d = date.fromisoformat(date_str)

        shift, created = Shift.objects.update_or_create(
            worker=worker,
            date=d,
            defaults={'coffee_shop': worker.coffee_shop, 'start_time': start_time})

        check_and_notify_understaffed(worker.coffee_shop, d)
        return JsonResponse({'status': 'ok'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


def check_and_notify_understaffed(cafe, d):
    actual = Shift.objects.filter(coffee_shop=cafe, date=d, start_time__isnull=False).count()

    if actual < cafe.minimum_workers:
        print(f"⚠️ Недобор в {cafe.name} на {d}: {actual} < {cafe.minimum_workers}")
        # здесь можно отправить push-уведомление через Web Push или FCM
        # пока просто логируем — позже добавим реальные пушки
    else:
        # можно сбросить уведомление, если оно было
        pass

from django.shortcuts import render

def schedule_view(request):
    return render(request, 'main/schedule.html')