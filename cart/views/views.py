# from django.shortcuts import render

# Create your views here.
from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['GET'])
def ping(request):
    return Response({'message': 'pong from zid-cart'})
