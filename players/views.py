from django.shortcuts import render
from django.http import HttpResponse

def get_api_code(request):
    code = request.GET.get('code')
    return HttpResponse(code)