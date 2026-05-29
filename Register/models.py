from django.db import models

# Importujemy model Szkolenie, aby móc stworzyć relację klucza obcego
from OfertaPubliczna.models import Szkolenie

class Rejestracja(models.Model):
    # FK do szkolenia (Id szkolenia)
    szkolenie = models.ForeignKey(Szkolenie, on_delete=models.CASCADE, related_name='rejestracje')
    zgoda_rodo = models.BooleanField(default=False)
    # Status zgłoszenia (np. Nowe, Potwierdzone, Anulowane)
    status = models.CharField(max_length=50, default='Nowe')
    # Automatycznie zapisuje datę i godzinę stworzenia w strefie czasowej UTC
    data_i_godzina_rejestracji = models.DateTimeField(auto_now_add=True)
    imie = models.CharField(max_length=100)
    nazwisko = models.CharField(max_length=100)
    telefon = models.CharField(max_length=20)
    email = models.EmailField()

    def __str__(self):
        return f"{self.imie} {self.nazwisko} - {self.szkolenie.tytul}"