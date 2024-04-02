from .models import Account, Transaction
from rest_framework import serializers

class AccountSerializers(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ['id', 'name', 'surname', 'balance']

class TransactionSerializers(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['id', 'sender', 'receiver', 'amount', 'date']
