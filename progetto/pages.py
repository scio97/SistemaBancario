from django.shortcuts import render

def index (request):
    return render(request, 'index.html')

def transfer (request):
    return render(request, 'transfer.html')