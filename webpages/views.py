from django.shortcuts import render


def home_view(request):
    template_name = 'home.html'
    return render(request, template_name, context={})
