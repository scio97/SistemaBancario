from rest_framework.response import Response
from .serializers import AccountSerializers
from .models import Account, Transaction
from django.http import JsonResponse
from rest_framework import status
import uuid

class Utility():
    def addBalance(amount, account):
        serializer = AccountSerializers(account)
        idAcc = serializer.data.get("id")
        balance = serializer.data.get("balance")
        if (amount >= 0.0):
            balance += amount
            
        if (amount < 0.0):
            if((balance + amount) < 0.0):
                return False
            balance += amount
                
        Account.objects.filter(pk=idAcc).update(balance = balance)
        return Utility.generateTransfer(idAcc, "", amount)
    
    def generateTransfer(idSender, idReceiver, amount):
        transazione = Transaction(id=uuid.uuid4(), sender=idSender, receiver=idReceiver,amount=amount)
        transazione.save()
        return transazione.id
    
    def newTransfer(sender, receiver, amount):
        serializerSender = AccountSerializers(sender)
        serializerReceiver = AccountSerializers(receiver)
        balanceSender = serializerSender.data.get("balance")
        balanceReceiver = serializerReceiver.data.get("balance")
        if(amount >= 0 and balanceSender >= amount):
            idSender = serializerSender.data.get("id")
            idReceiver = serializerReceiver.data.get("id")
            Account.objects.filter(pk=idSender).update(balance = balanceSender - amount)
            Account.objects.filter(pk=idReceiver).update(balance = balanceReceiver + amount)
            return Utility.generateTransfer(idSender, idReceiver, amount)
        return False

    def transfer(requestData):
        try:
            senderId = requestData['from']
            receiverId = requestData['to']
            amount = float(requestData['amount'])
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        if(len(senderId) != 20 or len(receiverId) != 20 ):
            return Response("Incorrect data length", status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        if(amount<0):
            return Response("Error: negative amount", status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        
        try:
            sender = Account.objects.get(id=senderId)
            receiver = Account.objects.get(id=receiverId)
        except Account.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        result = Utility.newTransfer(sender,receiver,amount)

        if(result!= False):
            #take the updated values
            sender = Account.objects.get(id=senderId)
            receiver = Account.objects.get(id=receiverId)
            serializerSender = AccountSerializers(sender)
            serializerReceiver = AccountSerializers(receiver)
            response = {'idTransaction':result, senderId:serializerSender.data.get('balance'),
                receiverId: serializerReceiver.data.get('balance') }
            response = JsonResponse(response, safe=False) #return json
            response.status_code=status.HTTP_201_CREATED
            return response

        return Response("Error, not enough funds! ", status=status.HTTP_409_CONFLICT)
    
    def verAccountDatas(name, surname):
        if(Utility.verAccountData(name) and Utility.verAccountData(surname)):
            return True
        return False

    def verAccountData(par):
        if (len(par) == 0 or len(par) > 40):
            return False
        return True