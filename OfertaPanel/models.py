from django.db import models

class SzablonGeneratora(models.Model):
    nazwa = models.CharField(max_length=200, unique=True)
    typ = models.CharField(max_length=50)  # 'formularz' lub 'szablon'
    pola = models.TextField(blank=True, null=True)  # JSON-serialized list of fields
    tresc = models.TextField(blank=True, null=True)  # raw content of the template

    def __str__(self):
        return f"{self.nazwa} ({self.typ})"
