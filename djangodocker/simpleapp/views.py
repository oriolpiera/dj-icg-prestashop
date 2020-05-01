from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def home(request):
    return HttpResponse("<h3>Hola, aquí no hi ha res interessant a veure. <br> Potser aquí trobaràs la respota al que busques <a href='https://duckduckgo.com/'>Duck Duck Go</a>.</h3>")
