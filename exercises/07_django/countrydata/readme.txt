INSTALLATION
============

1. Put this folder inside your Django project.
2. Add the app named "countrydata" inside INSTALLED_APPS in the settings.py file.
3. Add the following URL pattern:
    (r'^countrydata/', include("countrydata.urls")),
   in your main URL configure file.
