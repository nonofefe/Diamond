from django.db import models

# Create your models here.

class Income(models.Model): #収入のモデル
    description = models.CharField(max_length=128)
    amount = models.IntegerField()

class Expense(models.Model): #支出のモデル
    description = models.CharField(max_length=128)
    amount = models.IntegerField()