from django.db import models

# Create your models here.
class CoffeeShop(models.Model):
    name = models.CharField(max_length=50)
    minimum_workers = models.IntegerField(default=4)

    def __str__(self):
        return self.name

class Worker(models.Model):
    name = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=15)
    experience_years = models.IntegerField()
    start_date_experience_years = models.DateField()
    hourly_rate = models.IntegerField()
    coffee_shop = models.ForeignKey(CoffeeShop, on_delete = models.PROTECT, related_name = 'workers')
    
    def __str__(self):
        return self.name

# class Schedule(models.Model):
#     worker = models.ForeignKey(Worker, on_delete=models.CASCADE, related_name='schedules')
#     date = models.DateField()
#     start_time = models.TimeField()
#     end_time = models.TimeField()
    
#     class Meta:
#         unique_together = ['worker', 'date', 'start_time']
    
#     def __str__(self):
#         return f"{self.worker.name} - {self.date} {self.start_time}-{self.end_time}"
