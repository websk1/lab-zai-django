import { dom, state } from "./config.js";
import { dodajPoleDoFormularza, wstawPoleDoSzablonu } from "./logic.js";
import { pobierzDokumentZBackendu } from "./api.js";

// ================= LOGIKA UI (POMOCNICZA) =================
/*
  Blokuje radio buttony od wyboru miejsca zapisu w przypadku
  kiedy wczytano plik do edycji.
*/
export function przelaczBlokadeWyboruZrodla(
  czyZablokowac,
  wymuszoneZrodlo = null
) {
  dom.radiosTrybZapisu.forEach((radio) => {
    radio.disabled = czyZablokowac;
    if (czyZablokowac && wymuszoneZrodlo && radio.value === wymuszoneZrodlo) {
      radio.checked = true;
    }
    const label = radio.closest(".opcja-zapisu");
    if (label) {
      if (czyZablokowac) label.classList.add("zablokowane");
      else label.classList.remove("zablokowane");
    }
  });
}

// ================= LOGIKA UI (RESET) ================
/*
  Resetuje widok do stanu pierwotnego
*/
export function zresetujWidok(wymuszonyTryb) {
  state.edytowanyDokumentId = null;
  state.edytowaneZrodlo = null;

  dom.kontenerPolFormularza.innerHTML = "";
  dom.textareaSzablon.value = "";
  dom.wynikRenderowania.textContent = "";
  dom.sekcjaPodgladu.style.display = "none";
  dom.inputNazwaDokumentu.value = "";

  przelaczBlokadeWyboruZrodla(false);
  aktualizujBelkeStatusu();
  zmienTryb(wymuszonyTryb);
}

// Aktualizuje belkę statusu (element obok wyboru trybu)
export function aktualizujBelkeStatusu() {
  if (state.edytowanyDokumentId === null) {
    dom.statusBelka.textContent = `Tryb: Nowy Dokument`;
    dom.statusBelka.style.color = "#aaa";
  } else {
    dom.statusBelka.textContent = `Tryb: Edycja (ID: ${
      state.edytowanyDokumentId
    }, Źródło: ${state.edytowaneZrodlo.toUpperCase()})`;
    dom.statusBelka.style.color = "#e67e22";
  }
}

// Wczytuje odpowiednie działania podczas wczytania dokumentu z listy
export function wczytajDokumentDoEdycji(doc) {
  state.edytowanyDokumentId = doc.id;
  state.edytowaneZrodlo = doc.zrodlo;

  zmienTryb(doc.typ);
  dom.inputNazwaDokumentu.value = doc.nazwa;
  przelaczBlokadeWyboruZrodla(true, doc.zrodlo);

  if (doc.typ === "formularz") {
    dom.kontenerPolFormularza.innerHTML = "";
    if (Array.isArray(doc.pola)) {
      doc.pola.forEach((p) => dodajPoleDoFormularza(p, true));
    }
  } else {
    dom.textareaSzablon.value = doc.tresc || "";
  }

  aktualizujBelkeStatusu();
  pokazKomunikat(`Wczytano: ${doc.nazwa}`, "sukces");
}

// Renderuje przyciski pól
export function generujPrzyciskiPol(pola) {
  dom.kontenerPrzyciskow.innerHTML = "";
  pola.forEach((pole) => {
    const btn = document.createElement("button");
    btn.className = "btn-pole";
    btn.textContent = pole;
    btn.type = "button";
    btn.onclick = () => {
      if (state.aktualnyTryb === "formularz") dodajPoleDoFormularza(pole);
      else wstawPoleDoSzablonu(pole);
    };
    dom.kontenerPrzyciskow.appendChild(btn);
  });
}

// Renderuje liste dokumentów
export function generujListeDokumentow(dane) {
  dom.listaDokumentow.innerHTML = "";
  const template = dom.szablonElementuListy;
  dane.forEach((doc) => {
    const clone = template.content.cloneNode(true);
    const div = clone.querySelector(".element-listy");
    div.dataset.id = doc.id;
    div.dataset.source = doc.zrodlo;

    clone.querySelector(".nazwa-pliku").textContent = doc.nazwa;
    const badge = clone.querySelector(".znacznik-zrodla");
    badge.textContent = doc.zrodlo === "json" ? "JSON" : "DB";
    badge.classList.add(doc.zrodlo === "json" ? "typ-json" : "typ-db");

    div.onclick = function () {
      pobierzDokumentZBackendu(this.dataset.id, this.dataset.source);
    };
    dom.listaDokumentow.appendChild(clone);
  });
}

// Zmienia tryb - ukrywa odpowiednie kontenery poprzez klasy aktywny-ukryty
export function zmienTryb(tryb) {
  state.aktualnyTryb = tryb;
  if (tryb === "formularz") {
    dom.widokFormularz.classList.remove("ukryty");
    dom.widokSzablon.classList.add("ukryty");
    dom.btnFormularz.classList.add("aktywny");
    dom.btnSzablon.classList.remove("aktywny");
  } else {
    dom.widokFormularz.classList.add("ukryty");
    dom.widokSzablon.classList.remove("ukryty");
    dom.btnFormularz.classList.remove("aktywny");
    dom.btnSzablon.classList.add("aktywny");
  }
}

// Wyświetla powiadomienie AJAX
export function pokazKomunikat(msg, typ) {
  dom.powiadomienia.textContent = `Server: ${msg}`;
  dom.powiadomienia.className = `komunikaty-systemowe ${typ}`;
  setTimeout(() => {
    dom.powiadomienia.className = "komunikaty-systemowe";
    dom.powiadomienia.textContent = "Gotowy";
  }, 3000);
}
