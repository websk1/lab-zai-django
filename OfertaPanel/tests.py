import os
import json
import shutil
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.conf import settings
from .models import SzablonGeneratora

class GeneratorPanelTests(TestCase):
    def setUp(self):
        # Create a test user and log in
        self.user = User.objects.create_user(username='admin', password='password123')
        self.client = Client()
        self.client.login(username='admin', password='password123')
        
        # Setup clean templates directory for JSON
        self.temp_media_root = os.path.join(settings.BASE_DIR, 'test_media')
        self.original_media_root = settings.MEDIA_ROOT
        settings.MEDIA_ROOT = self.temp_media_root
        
        # Create initial test DB entry
        self.db_template = SzablonGeneratora.objects.create(
            nazwa="DB Test Template",
            typ="szablon",
            tresc="Witaj {imie} {nazwisko}!"
        )

    def tearDown(self):
        settings.MEDIA_ROOT = self.original_media_root
        if os.path.exists(self.temp_media_root):
            shutil.rmtree(self.temp_media_root)

    def test_api_get_fields(self):
        response = self.client.get(reverse('api_get_fields'))
        self.assertEqual(response.status_code, 200)
        self.assertIn("imie", response.json())

    def test_api_list(self):
        # Create a file JSON manually to see if list merges both
        from .views import get_json_templates_dir
        json_dir = get_json_templates_dir()
        with open(os.path.join(json_dir, 'form_test.json'), 'w', encoding='utf-8') as f:
            json.dump({"nazwa": "JSON Form", "typ": "formularz", "pola": ["email"]}, f)
            
        response = self.client.get(reverse('api_list'))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Should have both DB template and JSON template
        self.assertEqual(len(data), 2)
        names = [item['nazwa'] for item in data]
        self.assertIn("DB Test Template", names)
        self.assertIn("JSON Form", names)

    def test_api_get_document_db(self):
        response = self.client.get(f"{reverse('api_get_document')}?id={self.db_template.id}&source=db")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['nazwa'], "DB Test Template")

    def test_api_get_document_json(self):
        from .views import get_json_templates_dir
        json_dir = get_json_templates_dir()
        with open(os.path.join(json_dir, 'form_test.json'), 'w', encoding='utf-8') as f:
            json.dump({"nazwa": "JSON Form", "typ": "formularz", "pola": ["email"]}, f)

        response = self.client.get(f"{reverse('api_get_document')}?id=form_test.json&source=json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['nazwa'], "JSON Form")

    def test_api_save_db_new(self):
        payload = {
            "nazwa": "New DB Form",
            "typ": "formularz",
            "pola": ["imie", "nazwisko"]
        }
        response = self.client.post(
            f"{reverse('api_save')}?source=db",
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(SzablonGeneratora.objects.filter(nazwa="New DB Form").exists())

    def test_api_save_json_new(self):
        payload = {
            "nazwa": "New JSON Doc",
            "typ": "szablon",
            "tresc": "Treść z pliku"
        }
        response = self.client.post(
            f"{reverse('api_save')}?source=json",
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        
        # Check that the file was created
        from .views import get_json_templates_dir
        json_dir = get_json_templates_dir()
        self.assertTrue(os.path.exists(os.path.join(json_dir, 'new-json-doc.json')))

    def test_api_save_json_update(self):
        from .views import get_json_templates_dir
        json_dir = get_json_templates_dir()
        # Create a file first
        with open(os.path.join(json_dir, 'update_test.json'), 'w', encoding='utf-8') as f:
            json.dump({"nazwa": "Original", "typ": "szablon", "tresc": "Old"}, f)
            
        payload = {
            "nazwa": "Updated Name",
            "typ": "szablon",
            "tresc": "New content",
            "id": "update_test.json",
            "metoda": "UPDATE"
        }
        response = self.client.post(
            f"{reverse('api_save')}?source=json",
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        
        # Read the file and verify update
        with open(os.path.join(json_dir, 'update_test.json'), 'r', encoding='utf-8') as f:
            content = json.load(f)
            self.assertEqual(content['nazwa'], "Updated Name")
            self.assertEqual(content['tresc'], "New content")


    def test_public_form_templates(self):
        # Create a form template JSON file
        from .views import get_json_templates_dir
        json_dir = get_json_templates_dir()
        with open(os.path.join(json_dir, 'rejestracja.json'), 'w', encoding='utf-8') as f:
            json.dump({"nazwa": "Rejestracja", "typ": "formularz", "pola": ["imie", "telefon"]}, f)

        # 1. Test listing all form templates (does not require login)
        client = Client()
        response = client.get(reverse('api_form_templates'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(response.json()[0]['nazwa'], "Rejestracja")

        # 2. Test fetching single form template
        response2 = client.get(f"{reverse('api_form_templates')}?id=rejestracja.json")
        self.assertEqual(response2.status_code, 200)
        self.assertEqual(response2.json()['nazwa'], "Rejestracja")

    def test_public_message_templates(self):
        # Test fetching single message template HTML (does not require login)
        client = Client()
        
        # 1. Test with default test data replacement
        response = client.get(f"{reverse('api_message_templates')}?id={self.db_template.id}")
        self.assertEqual(response.status_code, 200)
        self.assertIn("text/html", response['content-type'])
        self.assertContains(response, "Witaj Jan Kowalski!")

        # 2. Test with custom query param replacements
        response2 = client.get(f"{reverse('api_message_templates')}?id={self.db_template.id}&imie=Adam&nazwisko=Nowak")
        self.assertEqual(response2.status_code, 200)
        self.assertContains(response2, "Witaj Adam Nowak!")

    def test_lista_kategorii_filters_and_sorting(self):
        from OfertaPubliczna.models import Kategorie
        Kategorie.objects.all().delete()
        
        k1 = Kategorie.objects.create(nazwa="B_Programowanie", kolejnosc=2, publikuj=True)
        k2 = Kategorie.objects.create(nazwa="A_BazyDanych", kolejnosc=1, publikuj=False)
        
        # Test search
        response = self.client.get(f"{reverse('lista_kategorii')}?q=Bazy")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "A_BazyDanych")
        self.assertNotContains(response, "B_Programowanie")
        
        # Test filter status
        response = self.client.get(f"{reverse('lista_kategorii')}?pub=true")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "B_Programowanie")
        self.assertNotContains(response, "A_BazyDanych")
        
        # Test sorting
        response = self.client.get(f"{reverse('lista_kategorii')}?sort=nazwa&dir=asc")
        kats = list(response.context['kategorie'])
        self.assertEqual(kats[0].nazwa, "A_BazyDanych")
        self.assertEqual(kats[1].nazwa, "B_Programowanie")

    def test_lista_szkolen_filters_and_sorting(self):
        from OfertaPubliczna.models import Kategorie, Szkolenie
        Szkolenie.objects.all().delete()
        Kategorie.objects.all().delete()
        
        kat = Kategorie.objects.create(nazwa="IT", kolejnosc=1, publikuj=True)
        s1 = Szkolenie.objects.create(kategoria=kat, numer="C1", tytul="Advanced Python", cena=100.0, liczba_godzin=10, kolejnosc=2, publikuj=True)
        s2 = Szkolenie.objects.create(kategoria=kat, numer="C2", tytul="Django Basics", cena=200.0, liczba_godzin=20, kolejnosc=1, publikuj=False)
        
        # Test search
        response = self.client.get(f"{reverse('lista_szkolen')}?q=Django")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Django Basics")
        self.assertNotContains(response, "Advanced Python")
        
        # Test status filter
        response = self.client.get(f"{reverse('lista_szkolen')}?pub=false")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Django Basics")
        self.assertNotContains(response, "Advanced Python")
        
        # Test category filter
        response = self.client.get(f"{reverse('lista_szkolen')}?kat={kat.id}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['szkolenia']), 2)
        
        # Test sorting
        response = self.client.get(f"{reverse('lista_szkolen')}?sort=cena&dir=desc")
        szkols = list(response.context['szkolenia'])
        self.assertEqual(szkols[0].numer, "C2")
        self.assertEqual(szkols[1].numer, "C1")

