from django.test import TestCase
import unittest
import json
from countrydata.models import Continent, Country
from django.test.client import Client
from django.db import models
from django.core.exceptions import ValidationError
from django.template.loader import render_to_string


class BasicDataTestCase(TestCase, unittest.TestCase):
    fixtures = ['countrydata.xml']

    def testGettingContinent(self):
        europe = Continent.objects.get(code="eu")
        self.assertEqual(europe.name, "Europe", "Getting continent Europe")
    
    def testCreatingContinent(self):
        Continent.objects.create(name="Testcontinent", code="tc")
        
        testcontinent = Continent.objects.get(code="tc")
        self.assertEqual(testcontinent.name, "Testcontinent", "Getting a just created continent")

    def _testfieldtype(self, model, modelname, fieldname, type):
        try:
          field = model._meta.get_field(fieldname)
          self.assertTrue(isinstance(field, type), "Testing the type of %s field in model %s"%(fieldname, modelname))
        except FieldDoesNotExist:
          self.assertTrue(False, "Testing if field %s exists in model %s"%(fieldname, modelname))
        return field

    def testFieldTypes(self):
      self._testfieldtype(Continent, 'Continent', 'name', models.CharField)
      self._testfieldtype(Continent, 'Continent', 'code', models.CharField)
      self._testfieldtype(Country, 'Country', 'code', models.CharField)
      self._testfieldtype(Country, 'Country', 'name', models.CharField)
      self._testfieldtype(Country, 'Country', 'capital', models.CharField)
      self._testfieldtype(Country, 'Country', 'population', models.PositiveIntegerField)
      self._testfieldtype(Country, 'Country', 'area', models.PositiveIntegerField)
      self._testfieldtype(Country, 'Country', 'code', models.CharField)
    
    def testModelOrdering(self):
        prev = None
        # Check both Continent and Country classes
        for ModelClass in (Continent, Country):
            # Iterate over all objects and check that the next is greater than the previous
            for cur in ModelClass.objects.all():
                if prev:
                    self.assertTrue(prev.name < cur.name, "Checking ordering of objects in " + cur.__class__.__name__ + ". Did you remember to set the default ordering?")
                prev = cur
            prev = None
    
    def testCountryCreationValidation(self):
        europe = Continent.objects.get(code="eu")
        
        code_conflict = Country(name="Example",
                                 population=100,
                                 area=1000,
                                 capital="capital",
                                 code="fi", 
                                 continent=europe)
        
        valid_country = Country(name="Example",
                                 population=100,
                                 area=1000,
                                 capital="capital",
                                 code="xx", 
                                 continent=europe)
                
        # Cleaning conflicting code should raise an error
        self.assertRaises(ValidationError, code_conflict.full_clean, "Code for Country should be unique")
                
        # This should not raise any errors
        try:
          valid_country.full_clean()
        except:
          self.assertTrue(False, "Saving a country with valid data failed")

    def testCountryThroughContinent(self):
        # Get continent
        europe = Continent.objects.get(code="eu")
        
        # Test that foreign key relation works backwards
        try:
          fi = europe.countries.get(code="fi")
        except:
          self.assertTrue(False, "Getting country failed. Did you remember that countries should be accessed through attribute countries?")
        self.assertEqual(fi.name, "Finland", "Getting a country from a continent")
        
class JsonTestCase(TestCase, unittest.TestCase):
    fixtures = ['countrydata.xml']
    def setUp(self):
        # Initialize a Django test client
        self.client = Client()
    
    def testJsonContinents(self):
        for continent in Continent.objects.all():
            response = self.client.get('/countrydata/data/%s.json' % continent.code)
            self.assertEquals(response.status_code, 200, "Testing JSON continent request status code.")
            country_dict = json.loads(response._container[0].decode(encoding="utf-8"))
            
            # Check that each country name can be found under the corresponding code in dict
            for country in continent.countries.all():
                self.assertEquals(country.name, country_dict[country.code])

    def testJsonCountries(self):
        for country in Country.objects.all():
            response = self.client.get('/countrydata/data/%s/%s.json' % (country.continent.code, country.code))
            self.assertEquals(response.status_code, 200, "Testing JSON country request status code.")
            
            fields = json.loads(response._container[0].decode(encoding="utf-8"))
            
            # Check that each field can be found in fields dict
            self.assertEquals(country.population, fields["population"])
            self.assertEquals(country.area, fields["area"])
            self.assertEquals(country.capital, fields["capital"])
    
    def testJsonCallback(self):
        response = self.client.get('/countrydata/data/eu/no.json', {"callback": "custom_callback"})
        self.assertContains(response, "custom_callback(")
        
        response = self.client.get('/countrydata/data/eu.json', {"callback": "trigger"})
        self.assertContains(response, "trigger(")

    def testInvalidParameters(self):
        # Norway should not be found under North America
        response = self.client.get('/countrydata/data/na/no.json')
        self.assertEquals(response.status_code, 404, "Looking for a real country in a wrong continent.")
        
        # There is no country "xx" in North America
        response = self.client.get('/countrydata/data/na/xx.json')
        self.assertEquals(response.status_code, 404, "Looking for a non existent country in a real continent.")
        
        # There is no continent with a "xx" code
        response = self.client.get('/countrydata/data/xx/fi.json')
        self.assertEquals(response.status_code, 404, "Looking for a real country in a non existent continent.")
        
        # Norway should be found under Europe
        response = self.client.get('/countrydata/data/eu/no.json')
        self.assertEquals(response.status_code, 200, "Testing valid request status code.")

class TemplateTestCase(TestCase):
    fixtures = ['countrydata.xml']
    def setUp(self):
        self.client = Client()
    
    #@max_score(1)
    def testInvalidUrl(self):
        response = self.client.get('/countrydata/xx.html')
        self.assertEquals(response.status_code, 404, "Requesting a page with an invalid country code.")
    
    #@max_score(4)
    def testPageContents(self):
        """ This test requests pages for all continents and checks that all relevant data of
        their countries can be found on the page. """
        for continent in Continent.objects.all():
            url = '/countrydata/%s.html' % continent.code
            response = self.client.get(url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
            self.assertEquals(response.status_code, 200, "Testing request status code.")
            
            for country in Country.objects.all():
                if country.continent == continent:
                    self.assertContains(response, country.name)
                    self.assertContains(response, country.capital)
                    self.assertContains(response, country.population)
                    self.assertContains(response, country.area)
                else:
                    # Parts of some countries names are found in two different continents
                    if country.name in ("Georgia", "France", "Netherlands", "Spain", "Guinea", "Antarctica"):
                        continue
                    self.assertNotContains(response, country.name)
                    
    #@max_score(4)
    def testContinentMenu(self):
        """ Tests that the continent menu is rendered correctly """
        all_continents = ({'code': 'qq', 'name': 'Quu'},
                          {'code': 'ww', 'name': 'Wee'})
        ren = render_to_string("countrydata/continentmenu.html", {'all_continents': all_continents})
        from django.core.urlresolvers import reverse
        for continent in all_continents:
          self.assertTrue(ren.find(reverse('countrydata.views.show_continent', args=[continent['code']])) > -1,
                "Testing if the rendered menu contains correct URL for continent")
          self.assertTrue(ren.find(continent['name']) > -1,
                "Testing if the rendered menu contains correct continent name")
    
    #@max_score(3)
    def testPartialContents(self):
        """ Tests that the response is different when requesting a page with an Ajax request. """
        for continent in Continent.objects.all():
            url = '/countrydata/%s.html' % continent.code
            
            # Test with an Ajax request
            response = self.client.get(url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
            self.assertEquals(response.status_code, 200, "Testing request status code.")
            self.assertNotContains(response, "<html>")
            self.assertNotContains(response, "<body>")
            self.assertEquals(response.status_code, 200, "Testing request status code.")
            self.assertTemplateUsed(response, "countrydata/countrytable.html", "Testing that the right template was rendered")
            self.assertTemplateNotUsed(response, "countrydata/index.html", "Testing that index.html was not rendered on Ajax request")
            self.assertTemplateNotUsed(response, "countrydata/continentmenu.html", "Testing that continentmenu.html was not rendered on Ajax request")
            
            for country in Country.objects.all():
                if country.continent == continent:
                    self.assertContains(response, country.name)
                    self.assertContains(response, country.capital)
                    self.assertContains(response, country.population)
                    self.assertContains(response, country.area)
                else:
                    # Parts of some countries names are found in two different continents
                    if country.name in ("Georgia", "France", "Netherlands", "Spain", "Guinea", "Antarctica"):
                        continue
                    self.assertNotContains(response, country.name)
            
            # Test with a non-Ajax request
            response = self.client.get(url)
            self.assertEquals(response.status_code, 200, "Testing request status code.")
            self.assertContains(response, "<html>")
            self.assertContains(response, "<body>")

class TemplateTestCase(TestCase):
    fixtures = ['countrydata.xml']
    def setUp(self):
        self.client = Client()
    
    def testInvalidUrl(self):
        response = self.client.get('/countrydata/xx.html')
        self.assertEquals(response.status_code, 404, "Requesting a page with an invalid country code.")
    
    def testPageContents(self):
        """ This test requests pages for all continents and checks that all relevant data of
        their countries can be found on the page. """
        for continent in Continent.objects.all():
            url = '/countrydata/%s.html' % continent.code
            response = self.client.get(url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
            self.assertEquals(response.status_code, 200, "Testing request status code.")
            
            for country in Country.objects.all():
                if country.continent == continent:
                    self.assertContains(response, country.name)
                    self.assertContains(response, country.capital)
                    self.assertContains(response, country.population)
                    self.assertContains(response, country.area)
                else:
                    # Parts of some countries names are found in two different continents
                    if country.name in ("Georgia", "France", "Netherlands", "Spain", "Guinea", "Antarctica"):
                        continue
                    self.assertNotContains(response, country.name)
                    
    def testContinentMenu(self):
        """ Tests that the continent menu is rendered correctly """
        all_continents = ({'code': 'qq', 'name': 'Quu'},
                          {'code': 'ww', 'name': 'Wee'})
        ren = render_to_string("countrydata/continentmenu.html", {'all_continents': all_continents})
        from django.core.urlresolvers import reverse
        for continent in all_continents:
          self.assertTrue(ren.find(reverse('countrydata.views.show_continent', args=[continent['code']])) > -1,
                "Testing if the rendered menu contains correct URL for continent")
          self.assertTrue(ren.find(continent['name']) > -1,
                "Testing if the rendered menu contains correct continent name")
    
    def testPartialContents(self):
        """ Tests that the response is different when requesting a page with an Ajax request. """
        for continent in Continent.objects.all():
            url = '/countrydata/%s.html' % continent.code
            
            # Test with an Ajax request
            response = self.client.get(url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
            self.assertEquals(response.status_code, 200, "Testing request status code.")
            self.assertNotContains(response, "<html>")
            self.assertNotContains(response, "<body>")
            self.assertEquals(response.status_code, 200, "Testing request status code.")
            self.assertTemplateUsed(response, "countrydata/countrytable.html", "Testing that the right template was rendered")
            self.assertTemplateNotUsed(response, "countrydata/index.html", "Testing that index.html was not rendered on Ajax request")
            self.assertTemplateNotUsed(response, "countrydata/continentmenu.html", "Testing that continentmenu.html was not rendered on Ajax request")
            
            for country in Country.objects.all():
                if country.continent == continent:
                    self.assertContains(response, country.name)
                    self.assertContains(response, country.capital)
                    self.assertContains(response, country.population)
                    self.assertContains(response, country.area)
                else:
                    # Parts of some countries names are found in two different continents
                    if country.name in ("Georgia", "France", "Netherlands", "Spain", "Guinea", "Antarctica"):
                        continue
                    self.assertNotContains(response, country.name)
            
            # Test with a non-Ajax request
            response = self.client.get(url)
            self.assertEquals(response.status_code, 200, "Testing request status code.")
            self.assertContains(response, "<html>")
            self.assertContains(response, "<body>")

