from django.db import models

# Create your models here.
class Kategorie(models.Model):
    publikuj = models.BooleanField(default=True)
    kolejnosc = models.IntegerField(default=0)
    # null=True pozwala na brak rodzica
    kategoria_nadrzedna = models.ForeignKey(
        'self', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='podkategorie'
    )
    nazwa = models.CharField(max_length=255)

    def __str__(self):
        return self.nazwa

    class Meta:
        verbose_name = "Kategoria"
        verbose_name_plural = "Kategorie"


class Szkolenie(models.Model):
    # Relacja fk do modelu Kategorie (Id kategorii)
    kategoria = models.ForeignKey(Kategorie, on_delete=models.CASCADE, related_name='szkolenia')
    publikuj = models.BooleanField(default=True)
    kolejnosc = models.IntegerField(default=0)
    liczba_godzin = models.IntegerField()
    numer = models.CharField(max_length=50, unique=True)
    cena = models.DecimalField(max_digits=10, decimal_places=2)
    tytul = models.CharField(max_length=255)
    opis = models.TextField()

    def __str__(self):
        return f"{self.numer} - {self.tytul}"

    class Meta:
        verbose_name = "Szkolenie"
        verbose_name_plural = "Szkolenia"