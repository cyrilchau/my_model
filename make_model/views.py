from django.shortcuts import render
from django.http import HttpResponse
from .forms import InputForm
from .models import Shop, Comment
from modules import recsys
from django.db.models import Q
from .filters import ShopFilter
# Create your views here.

def index(request):
   shops = None
   form = InputForm()
   if request.method == 'POST':
      form = InputForm(request.POST)
      if form.is_valid():
         index = recsys.recommendations(form.cleaned_data['input'])
         shops = Shop.objects.filter(pk__in=index).order_by('id')
         # recsys.recommendations(form.cleaned_data['input'])
   return render(request, 'home/index.html', {'form':form,'shops':shops})

lst = []
def test(request):
   shops = Shop.objects.all()[0:10]
   for i in shops:
      lst.append(i.name)
   str1 = ' '.join(lst)
   print(str1)
   return render(request, 'home/test.html',{'shops':shops})