from django.urls import path
from . import views

urlpatterns = [
    path('schedule/<int:cafe_id>/', views.schedule_view, name='schedule'),
    path('api/schedule/<int:cafe_id>/', views.get_schedule_data, name='schedule_data'),
    path('api/shift/update/', views.update_shift, name='update_shift'),
    path('api/swap/increment/', views.increment_swap, name='increment_swap'),
    path('api/coffee-shops/', views.get_coffee_shops, name='coffee_shops'),
    path('', views.index, name='index'),
]