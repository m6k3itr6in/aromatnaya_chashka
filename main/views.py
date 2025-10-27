# main/views.py
import calendar
from datetime import datetime, date
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json
from django.db import models

from .models import CoffeeShop, Shift, Worker, SwapCounter
from django.shortcuts import render

def index(request):
    cafes = CoffeeShop.objects.all()
    return render(request, 'main/index.html', {'cafes':cafes})

def get_schedule_data(request, cafe_id):
    try:
        cafe = get_object_or_404(CoffeeShop, id=cafe_id)
        today = date.today()
        year = today.year
        month = today.month

        days_in_month = calendar.monthrange(year, month)[1]
        first_weekday = calendar.monthrange(year, month)[0]


        weekdays = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']
        header = []
        for day in range(1, days_in_month + 1):
            weekday_index = (first_weekday + day - 1) % 7
            header.append({
                'day': day,
                'weekday': weekdays[weekday_index],
                'date': f"{year}-{month:02d}-{day:02d}"
            })

        workers = Worker.objects.filter(coffee_shop=cafe)

        shifts_in_month = Shift.objects.filter(
            worker__in=workers,
            date__year=year,
            date__month=month
        )

        worker_count_per_day = {}
        for day in range(1, days_in_month + 1):
            d = date(year, month, day)
            count = shifts_in_month.filter(date=d).filter(models.Q(start_time__isnull=False) | models.Q(other_coffee_shop__isnull=False)).count()
            worker_count_per_day[d] = count

        rows = []
        for worker in workers:
            counter, _ = SwapCounter.objects.get_or_create(
                worker=worker,
                month=date(year, month, 1),
                defaults={'swaps_this_month': 0}
            )

            row_data = []
            for day_info in header:
                d = date.fromisoformat(day_info['date'])
                try:
                    shift = Shift.objects.get(worker=worker, date=d)
                    if shift.display_value:
                        cell_value = shift.display_value
                    elif shift.other_coffee_shop:
                        cell_value = f"+ {shift.other_coffee_shop.short_code}"
                    elif shift.start_time:
                        cell_value = shift.start_time
                    else:
                        cell_value = ''
                except Shift.DoesNotExist:
                    cell_value = ''
                row_data.append(cell_value)

            rows.append({
                'id': worker.id,
                'name': worker.name,
                'data': row_data,
                'swaps': counter.swaps_this_month
            })

        red_days = [
            day_info['day'] for day_info in header
            if worker_count_per_day.get(date.fromisoformat(day_info['date']), 0) < cafe.minimum_workers]

        return JsonResponse({
            'cafe_name': cafe.name,
            'header': header,
            'rows': rows,
            'red_days': red_days,
            'minimum_required': cafe.minimum_workers,
            'current_month': f"{year}-{month:02d}",
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
        other_cafe_id = data.get('other_cafe_id')
        display_value = data.get('display_value')

        worker = Worker.objects.get(id=worker_id)
        d = date.fromisoformat(date_str)

        other_cafe = None
        if other_cafe_id:
            other_cafe = CoffeeShop.objects.get(id=other_cafe_id)

        shift, created = Shift.objects.update_or_create(
            worker=worker,
            date=d,
            defaults={
                'coffee_shop': worker.coffee_shop,
                'start_time': start_time,
                'other_coffee_shop': other_cafe,
                'display_value': display_value
            }
        )

        check_and_notify_understaffed(worker.coffee_shop, d)
        return JsonResponse({'status': 'ok'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


def check_and_notify_understaffed(cafe, d):
    actual = Shift.objects.filter(coffee_shop=cafe, date=d, start_time__isnull=False).count()

    if actual < cafe.minimum_workers:
        print(f"Недобор в {cafe.name} на {d}: {actual} < {cafe.minimum_workers}")
        # здесь можно отправить push-уведомление через Web Push или FCM
        # пока просто логируем — позже добавим реальные пушки
    else:
        # можно сбросить уведомление, если оно было
        pass

@csrf_exempt
def increment_swap(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST only'}, status=405)
    
    try:
        data = json.loads(request.body)
        worker_id = data['worker_id']
        worker = Worker.objects.get(id=worker_id)
        today = date.today()
        month_key = date(today.year, today.month, 1)

        counter, _ = SwapCounter.objects.get_or_create(
            worker=worker,
            month=month_key,
            defaults={'swaps_this_month': 0}
        )
        counter.swaps_this_month += 1
        counter.save()

        return JsonResponse({'swaps': counter.swaps_this_month})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

def get_coffee_shops(request):
    shops = CoffeeShop.objects.all()
    data = [{'id': s.id, 'short_code': s.short_code} for s in shops]
    return JsonResponse(data, safe=False)

def schedule_view(request, cafe_id):
    return render(request, 'main/cafe/schedule.html', {'cafe_id': cafe_id})