from django.db import models
from datetime import datetime

class Account(models.Model):
    id = models.CharField(primary_key=True, max_length=20)
    name = models.CharField(max_length=40)
    surname = models.CharField(max_length=40)
    balance = models.FloatField(default=0.0, max_length=40)

    def __str__(self):
        return self.id + ' ' + self.name + ' ' + self.surname + ' ' + str(self.balance)         

class Transaction(models.Model):
    id = models.CharField(primary_key=True, max_length=40)
    sender = models.CharField(max_length=20, null=False)
    receiver = models.CharField(max_length=20)
    amount = models.FloatField(max_length=40, null=False)
    date = models.DateTimeField(default=datetime.now)

    def __str__(self):
        return self.id + ' ' + self.sender + ' ' + self.receiver + ' ' + str(self.amount) + ' ' + str(self.date)