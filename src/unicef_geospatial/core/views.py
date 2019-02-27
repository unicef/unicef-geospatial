from django.template.response import TemplateResponse


def index(request):
    context = {'page': 'index', 'title': 'Geospatial Server'}
    return TemplateResponse(request, 'index.html', context)
