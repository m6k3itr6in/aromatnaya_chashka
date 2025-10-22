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

class Shift(models.Model):
    SHIFT_CHOICES = [
        ('07:30', '7:30–22:00'),
        ('08:00', '8:00–22:00'),
        ('10:00', '10:00–22:00'),
    ]

    worker = models.ForeignKey(Worker, on_delete=models.CASCADE, related_name='shifts')
    coffee_shop = models.ForeignKey(CoffeeShop, on_delete=models.CASCADE)
    date = models.DateField()
    start_time = models.CharField(max_length=5, choices=SHIFT_CHOICES, blank=True, null=True)

    class Meta:
        unique_together = ('worker', 'date')
        ordering = ['date', 'worker__name']

    def __str__(self):
        if self.start_time:
            return f"{self.worker.name} — {self.date} ({self.get_start_time_display()})"
        return f"{self.worker.name} — {self.date} (Выходной)"
