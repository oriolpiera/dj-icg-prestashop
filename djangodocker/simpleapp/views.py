from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import TemplateView
from .forms import ProductForm
from . import controller, prestashop
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .constants  import *
import logging
from datetime import datetime

# Create your views here.
def home(request):
    return HttpResponse("<h3>Hola, aquí no hi ha res interessant a veure. <br> Potser aquí trobaràs la respota al que busques <a href='https://duckduckgo.com/'>Duck Duck Go</a>.</h3>")

@method_decorator(csrf_exempt, name='dispatch')
class ProductView(TemplateView):
    template_name = 'home/home.html'

    def get(self, request):
        form = ProductForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        logger = logging.getLogger('simpleapp.views')
        form = ProductForm(request.POST)

        data_form = request.POST.copy()
        data = data_form.get('data')
        token = data_form.get('token')
        tipus = data_form.get('tipus')
        if token != MSSQL_TOKEN:
            return HttpResponse('Unauthorized', status=401)

        c = controller.ControllerICGProducts()
        if tipus == "product":
            c.saveNewProducts(None,data)
        elif tipus == "price":
            c.saveNewPrices(None, data)
        elif tipus == "stock":
            c.saveNewStocks(None, data)

        logger.error("[" + str(datetime.now()) + "] Ens arribat una request PHP tipus: " + tipus + "\n" + data)
        return HttpResponse('Created', status=201)

