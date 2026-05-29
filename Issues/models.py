from django.db import models

class ZgloszenieProblemu(models.Model):
    # Wybór modułu aplikacji (zdefiniowany jako krotka/tuple opcji)
    CHOICES_MODUL = [
        ('oferta_publiczna', 'Oferta Publiczna'),
        ('panel_oferty', 'Panel Zarządzania Ofertą'),
        ('rejestracja', 'Rejestracja i Zgłoszenia'),
        ('inny', 'Inny moduł / Ogólne'),
    ]

    # Automatycznie zapisuje datę i godzinę zgłoszenia (UTS/UTC)
    data_i_godzina_zgloszenia = models.DateTimeField(auto_now_add=True)
    
    # Autor zgłoszenia (np. Imię i nazwisko lub E-mail)
    autor_zgloszenia = models.CharField(max_length=150)
    
    temat_zgloszenia = models.CharField(max_length=200)
    
    # Treść - opis problemu
    tresc = models.TextField()
    
    # Wybór modułu aplikacji z listy rozwijanej (HTML Select)
    modul_aplikacji = models.CharField(
        max_length=50, 
        choices=CHOICES_MODUL, 
        default='inny'
    )
    
    # Opcjonalne załączniki graficzne. 
    # null=True i blank=True sprawiają, że pole nie jest wymagane.
    zalacznik_graficzny = models.ImageField(
        upload_to='issues_attachments/', 
        null=True, 
        blank=True
    )

    def __str__(self):
        return f"{self.temat_zgloszenia} - {self.autor_zgloszenia}"