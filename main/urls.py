from django.urls import path
from . import views

urlpatterns = [
    path('schedule/', views.schedule_view, name='schedule'),
    path('api/schedule/<int:cafe_id>/', views.get_schedule_data, name='schedule_data'),
    path('api/shift/update/', views.update_shift, name='update_shift'),
]