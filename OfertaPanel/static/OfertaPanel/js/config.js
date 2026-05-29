// ================= DANE LOKALNE (do renderowania) =================
export const bazaTestowaWartosci = {
  imie: "Jan",
  nazwisko: "Kowalski",
  email: "jan@firma.pl",
  telefon: "123-456-789",
  adres: "Gorzów Wielkopolski, ul. Chopina 13",
  firma: "AJP",
  pesel: "90090912345",
};

// ================= KONFIGURACJA BACKENDU =================
export const backendBaseUrl = "/offer-mng/api";

// ================= STAN =================
export const state = {
  aktualnyTryb: "formularz",
  edytowanyDokumentId: null,
  edytowaneZrodlo: null,
};

// ================= DOM ELEMENTS =================
export const dom = {
  btnFormularz: document.getElementById("przycisk-tryb-formularz"),
  btnSzablon: document.getElementById("przycisk-tryb-szablon"),
  btnDaneTestowe: document.getElementById("przycisk-dane-testowe"),
  btnZapisz: document.getElementById("akcja-zapisz"),
  statusBelka: document.getElementById("status-belka"),
  widokFormularz: document.getElementById("widok-formularza"),
  widokSzablon: document.getElementById("widok-szablonu"),
  kontenerPrzyciskow: document.getElementById("kontener-przyciskow-pol"),
  kontenerPolFormularza: document.getElementById("kontener-pol-formularza"),
  textareaSzablon: document.getElementById("pole-tekstowe-szablonu"),
  listaDokumentow: document.getElementById("lista-zapisanych-dokumentow"),
  inputFiltr: document.getElementById("filtr-dokumentow"),
  powiadomienia: document.getElementById("powiadomienia-ajax"),
  inputNazwaDokumentu: document.getElementById("input-nazwa-dokumentu"),
  wynikRenderowania: document.getElementById("wynik-renderowania"),
  sekcjaPodgladu: document.getElementById("sekcja-podgladu"),
  szablonWierszaPola: document.getElementById("szablon-wiersza-pola"),
  szablonElementuListy: document.getElementById("szablon-elementu-listy"),
  radiosTrybZapisu: document.querySelectorAll('input[name="tryb-zapisu"]'),
};
