from django.http import Http404
from django.shortcuts import render_to_response, get_object_or_404
import json

from countrydata.models import Continent, Country

def continent_json(request, continent_code):
    """ Write your answer in 7.2 here. """
    raise Http404("Not implemented")

def country_json(request, continent_code, country_code):
    """ Write your answer in 7.2 here. """
    raise Http404("Not implemented")

def show_continent(request, continent_code=None):
    context = {"all_continents": Continent.objects.all()}
    if continent_code:
        continent = get_object_or_404(Continent, code=continent_code)
        context["continent"] = continent

    # Add your answer in 7.3 here
    return render_to_response("countrydata/index.html", context)

def render_javascript(request):
    """ NOTE: This is a really bad way of serving a static file! 
        It is only used in this exercise to serve this single JS file easily. """
    return render_to_response("countrydata/ajax_ui.js", content_type="text/javascript")
