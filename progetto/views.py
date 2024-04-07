from django.http import JsonResponse
from asyncio.windows_events import NULL
from .models import Account, Transaction
from .serializers import AccountSerializers, TransactionSerializers
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from progetto import utility
import secrets

@api_view(['GET', 'POST', 'DELETE'])
def account_controller(request):

    if request.method == 'GET':
        accounts = Account.objects.all() #get all the accounts
        serializer = AccountSerializers(accounts, many=True) #serialize them
        response = JsonResponse(serializer.data, safe=False) #return json
        response.status_code=status.HTTP_200_OK
        return response 

    if request.method == 'POST':
        try:
            name = request.data['name']
            surname = request.data['surname']
            if (not utility.Utility.verAccountDatas(name, surname)):
                return Response("Incorrect data length", status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        except:
            return Response("Bad request", status=status.HTTP_400_BAD_REQUEST) #absent name or surname
        
        new_data = request.data.copy()
        new_data['id'] = secrets.token_hex(10)
        serializer = AccountSerializers(data=new_data)

        if serializer.is_valid():
            serializer.save()
        return Response(serializer.data.get('id'), status=status.HTTP_201_CREATED)
    
    if request.method == 'DELETE':
        try:
            id_Ricevuto = request.GET["id"]
        except:
            return Response("Bad request, no ID parameter", status=status.HTTP_400_BAD_REQUEST)
        try:
            account = Account.objects.get(id=id_Ricevuto)
        except Account.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        account.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'POST', 'PUT', 'PATCH', 'HEAD'])
def account_detail(request, id_Request):
    if (len(id_Request) != 20):
        return Response("Incorrect data length", status=status.HTTP_422_UNPROCESSABLE_ENTITY)

    try:
        account = Account.objects.get(id=id_Request) #verify that account exist 
    except Account.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        serializer = AccountSerializers(account)
        risposta = serializer.data
        array = Transaction.objects.raw('SELECT id FROM progetto_transaction WHERE sender = \"' + id_Request + '\" ORDER BY date ASC')
        risposta['transaction']= []
        for n in array:
            serializer2 = TransactionSerializers(n)
            risposta['transaction'] += [serializer2.data.get('id')]
        
        response = Response(risposta)
        response['X-Sistema-Bancario']= serializer.data.get('name')+';'+ serializer.data.get('surname')
        return response
    
    if request.method == 'POST':
        try:
            amount = float(request.data['amount'])
        except:
            return Response("Bad request, no amount parameter", status=status.HTTP_400_BAD_REQUEST)
        result = utility.Utility.addBalance(amount, account)
        if(result != False):
            account = Account.objects.get(id=id_Request) # refresh account data
            serializer = AccountSerializers(account)
            result={'saldo': str(serializer.data.get('balance')), 'id': str(result)}
            return Response(result, status=status.HTTP_200_OK)
        return Response("NON ENAUGH MONEY",status=status.HTTP_204_NO_CONTENT)
    
    if request.method == 'PUT':
        try:
            name = request.data['name']
            surname = request.data['surname']
        except:
            return Response("Bad request, missing parameter", status=status.HTTP_400_BAD_REQUEST)
        if (not utility.Utility.verAccountDatas(name, surname)):
            return Response("Incorrect data length", status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        Account.objects.filter(pk=id_Request).update(name = name, surname = surname)
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    if request.method == 'PATCH':
        try:
            name = request.data['name']
        except:
            name=NULL
        try:
            surname = request.data['surname']
        except:
            surname=NULL
        
        if(name != NULL and surname == NULL):
            if(not utility.Utility.verAccountData(name)):
                return Response("Incorrect data length", status=status.HTTP_422_UNPROCESSABLE_ENTITY)
            Account.objects.filter(pk=id_Request).update(name = name)
            return Response(status=status.HTTP_204_NO_CONTENT)
        elif(surname != NULL and name == NULL):
            if(not utility.Utility.verAccountData(surname)):
                return Response("Incorrect data length", status=status.HTTP_422_UNPROCESSABLE_ENTITY)
            Account.objects.filter(pk=id_Request).update(surname = surname)
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'HEAD':
        serializer = AccountSerializers(account)
        response = Response(status=status.HTTP_204_NO_CONTENT)
        response['X-Sistema-Bancario']= serializer.data.get('name')+';'+ serializer.data.get('surname')
        return response

@api_view(['POST'])
def transfer_endpoint(request):
    return utility.Utility.transfer(request.data)

@api_view(['POST'])
def divert(request):
    try:
        idTransaction =request.data['id']
    except :
        return Response(status=status.HTTP_400_BAD_REQUEST)
    if(len(idTransaction) != 36):
            return Response("Incorrect data length", status=status.HTTP_422_UNPROCESSABLE_ENTITY)
    try:
        transaction = Transaction.objects.get(id=idTransaction)
    except :
        return Response(status=status.HTTP_404_NOT_FOUND)
    serTransaction = TransactionSerializers(transaction)
    
    response= utility.Utility.transfer({'from':serTransaction.data.get('receiver'), 
        'to':serTransaction.data.get('sender'),'amount':serTransaction.data.get('amount')})
    if(response.status_code==201):
        return Response(status=status.HTTP_204_NO_CONTENT)
    return response
    
@api_view(['GET'])
def account_detail_complete(request, id_Request):
    if (len(id_Request) != 20):
        return Response("Incorrect data length", status=status.HTTP_422_UNPROCESSABLE_ENTITY)
    
    try:
        account = Account.objects.get(id=id_Request)
    except Account.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = AccountSerializers(account)
        risposta = serializer.data
        array = Transaction.objects.raw('SELECT id FROM progetto_transaction WHERE sender = \"'+id_Request+'\" ORDER BY date DESC')
        risposta['transaction']= []
        for n in array:
            serializer2 = TransactionSerializers(n)
            risposta['transaction'] += [serializer2.data.get('sender'),serializer2.data.get('receiver'),serializer2.data.get('amount')]
        
        response = Response(risposta)
        response['X-Sistema-Bancario']= serializer.data.get('name')+';'+ serializer.data.get('surname')
        return response