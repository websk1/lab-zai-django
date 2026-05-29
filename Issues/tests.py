from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import ZgloszenieProblemu

class IssuesTests(TestCase):
    def setUp(self):
        self.client = Client()
        # Create a test issue
        self.test_issue = ZgloszenieProblemu.objects.create(
            autor_zgloszenia="Testowy Autor",
            temat_zgloszenia="Testowy Temat",
            tresc="Testowa Tresc",
            modul_aplikacji="oferta_publiczna"
        )

    def test_zgloszenie_problemu_get(self):
        response = self.client.get(reverse('zgloszenie_problemu'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'Issues/zgloszenie_problemu.html')

    def test_zgloszenie_problemu_post(self):
        response = self.client.post(reverse('zgloszenie_problemu'), {
            'autor_zgloszenia': 'Nowy Zgloszeniodawca',
            'temat_zgloszenia': 'Problem z płatnością',
            'modul_aplikacji': 'rejestracja',
            'tresc': 'Nie mogę sfinalizować rejestracji szkolenia.'
        })
        # Should redirect to lista_problemow
        self.assertRedirects(response, reverse('lista_problemow'))
        # Check database
        self.assertTrue(ZgloszenieProblemu.objects.filter(autor_zgloszenia='Nowy Zgloszeniodawca').exists())

    def test_lista_problemow(self):
        response = self.client.get(reverse('lista_problemow'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'Issues/lista_problemow.html')
        self.assertContains(response, "Testowy Temat")

    def test_widok_problemu_with_query_param(self):
        # Access details using ?id=<id>
        response = self.client.get(f"{reverse('widok_problemu')}?id={self.test_issue.id}")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'Issues/widok_problemu.html')
        self.assertContains(response, "Testowy Temat")
        self.assertContains(response, "Testowa Tresc")

    def test_widok_problemu_missing_param(self):
        response = self.client.get(reverse('widok_problemu'))
        # Should redirect to list
        self.assertRedirects(response, reverse('lista_problemow'))

    def test_api_problems_json(self):
        response = self.client.get(reverse('api_problems'))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['temat_zgloszenia'], "Testowy Temat")
        self.assertEqual(data[0]['autor_zgloszenia'], "Testowy Autor")

    def test_api_problem_report_post_json(self):
        import json
        payload = {
            'autor_zgloszenia': 'API User',
            'temat_zgloszenia': 'API Issue',
            'modul_aplikacji': 'inny',
            'tresc': 'Problem zgloszony przez API.'
        }
        response = self.client.post(
            reverse('api_problem_report'),
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()['status'], 'success')
        self.assertTrue(ZgloszenieProblemu.objects.filter(autor_zgloszenia='API User').exists())

    def test_api_problem_report_post_form(self):
        response = self.client.post(reverse('api_problem_report'), {
            'autor_zgloszenia': 'API Form User',
            'temat_zgloszenia': 'API Form Issue',
            'modul_aplikacji': 'panel_oferty',
            'tresc': 'Problem zgloszony przez API form.'
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()['status'], 'success')
        self.assertTrue(ZgloszenieProblemu.objects.filter(autor_zgloszenia='API Form User').exists())

    def test_lista_problemow_filters_and_sorting(self):
        ZgloszenieProblemu.objects.all().delete()
        
        pr1 = ZgloszenieProblemu.objects.create(
            autor_zgloszenia="Alicja",
            temat_zgloszenia="B_Problem z panelem",
            tresc="Cos nie dziala",
            modul_aplikacji="panel_oferty"
        )
        pr2 = ZgloszenieProblemu.objects.create(
            autor_zgloszenia="Bartosz",
            temat_zgloszenia="A_Blad na stronie glownej",
            tresc="Tekst rozjechany",
            modul_aplikacji="oferta_publiczna"
        )

        # Test search
        response = self.client.get(f"{reverse('lista_problemow')}?q=Rozjechany")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Bartosz")
        self.assertNotContains(response, "Alicja")

        # Test filter modul
        response = self.client.get(f"{reverse('lista_problemow')}?modul=panel_oferty")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Alicja")
        self.assertNotContains(response, "Bartosz")

        # Test sorting
        response = self.client.get(f"{reverse('lista_problemow')}?sort=temat_zgloszenia&dir=asc")
        probs = list(response.context['problemy'])
        self.assertEqual(probs[0].autor_zgloszenia, "Bartosz") # "A_" comes first
        self.assertEqual(probs[1].autor_zgloszenia, "Alicja")

