from django.http import HttpResponse


def description(request):
    return HttpResponse('Api')