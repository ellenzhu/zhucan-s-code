from django.conf.urls import *
from countrydata.views import *

urlpatterns = patterns('',
    #URL for getting JSON data for a given continent code (ex 7.2)
    url(r"^data/(\w{2}).json",         continent_json),

    #URL for getting JSON data for a given country codes (in given continent) (ex 7.2)
    url(r"^data/(\w{2})/(\w{2}).json", country_json),

    #URL for getting HTML page with list of continents (ex 7.3)
    url(r"^$",                         show_continent),
    #URL for getting HTML partial page for a given continent (ex 7.3)
    url(r"^(\w{2}).html$",             show_continent),
    
    #URL for getting the ajax file
    #NOTE: this is not the way to get static files it in real environments
    url(r"^js/ajax_ui.js",             render_javascript),
)
