from django.contrib import admin
from .models import CoffeeShop, Worker

# Register your models here.
@admin.register(CoffeeShop)
class CoffeeShopAdmin(admin.ModelAdmin):
    list_display = ('name', 'minimum_workers',)

@admin.register(Worker)
class WorkerAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone_number', 'experience_years', 'start_date_experience_years', 'hourly_rate', 'coffee_shop',)