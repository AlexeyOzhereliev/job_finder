from django.shortcuts import render
from django.core.paginator import Paginator

from .forms import FindForm
from .models import Vacancy


def home_view(request):
    form = FindForm()
    return render(request, 'scraping/home.html', {'form': form})


def list_view(request):
    form = FindForm()
    city = request.GET.get('city')
    language = request.GET.get('language')
    page_obj = []
    context = {'city': city, 'language': language, 'form': form}
    if city or language:
        _filter = {}
        if city:
            _filter['city__slug'] = city
        if language:
            _filter['language__slug'] = language
        qs = Vacancy.objects.filter(**_filter)
        paginator = Paginator(qs, 10)
        page_number = request.GET.get('page')
        print(page_number)
        page_obj = paginator.get_page(page_number)
        print(page_obj)
        print(page_obj.paginator.page_range)
        context['object_list'] = page_obj
        context['num_pages'] = paginator.num_pages
        context['page_number'] = page_number
    return render(request, 'scraping/list.html', context)

