from django.test import TestCase, Client
from django.urls import reverse
from .models import Kategorie, Szkolenie

class PublicOfferTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.kat = Kategorie.objects.create(nazwa="Programowanie", kolejnosc=1, publikuj=True)
        self.s1 = Szkolenie.objects.create(
            kategoria=self.kat,
            numer="P1",
            tytul="B_Django dla początkujących",
            cena=150.00,
            liczba_godzin=16,
            kolejnosc=2,
            publikuj=True,
            opis="Podstawy Django"
        )
        self.s2 = Szkolenie.objects.create(
            kategoria=self.kat,
            numer="P2",
            tytul="A_Python w analizie danych",
            cena=300.00,
            liczba_godzin=8,
            kolejnosc=1,
            publikuj=True,
            opis="Analiza danych"
        )

    def test_kategorie_list(self):
        response = self.client.get(reverse('kategorie'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Programowanie")

    def test_lista_szkolen_kat_filters_and_sorting(self):
        # 1. Test search
        response = self.client.get(reverse('lista_szkolen_kat', args=[self.kat.nazwa]) + "?q=początkujących")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "B_Django dla początkujących")
        self.assertNotContains(response, "A_Python w analizie danych")

        # 2. Test sorting by price
        response = self.client.get(reverse('lista_szkolen_kat', args=[self.kat.nazwa]) + "?sort=cena&dir=desc")
        self.assertEqual(response.status_code, 200)
        courses = list(response.context['szkolenia'])
        self.assertEqual(courses[0].numer, "P2") # 300.00
        self.assertEqual(courses[1].numer, "P1") # 150.00

