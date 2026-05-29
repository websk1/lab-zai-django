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
