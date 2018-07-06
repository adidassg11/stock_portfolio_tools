from django.http import HttpResponse
from django.shortcuts import render


def index(request):
    # TODO, actually show some contents
    return HttpResponse("Portfolio viewer. Contents:")
