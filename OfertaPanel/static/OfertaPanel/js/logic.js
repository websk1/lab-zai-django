import { dom, bazaTestowaWartosci } from "./config.js";
import { pokazKomunikat } from "./ui.js";

// ================= LOGIKA OPERACYJNA =================
export function dodajPoleDoFormularza(nazwa, cicho = false) {
  const exists = Array.from(dom.kontenerPolFormularza.children).find(
    (d) => d.dataset.pole === nazwa
  );
  if (exists) {
    if (!cicho) pokazKomunikat("Już dodano!", "blad");
    return;
  }

  const clone = dom.szablonWierszaPola.content.cloneNode(true);
  const div = clone.querySelector(".wiersz-pola");
  div.dataset.pole = nazwa;
  clone.querySelector(".etykieta-pola").textContent = nazwa;
  dom.kontenerPolFormularza.appendChild(clone);
  if (!cicho) pokazKomunikat("Dodano pole", "sukces");
}

export function wstawPoleDoSzablonu(nazwa) {
  const start = dom.textareaSzablon.selectionStart;
  const txt = dom.textareaSzablon.value;
  const insert = `{${nazwa}}`;
  dom.textareaSzablon.value =
    txt.substring(0, start) +
    insert +
    txt.substring(dom.textareaSzablon.selectionEnd);
  dom.textareaSzablon.focus();
  pokazKomunikat("Wstawiono zmienną", "sukces");
}

export function renderujSzablon() {
  let txt = dom.textareaSzablon.value;
  if (!txt) return pokazKomunikat("Pusty szablon", "blad");
  for (const [k, v] of Object.entries(bazaTestowaWartosci)) {
    const regex = new RegExp(`{${k}}`, "gi");
    txt = txt.replace(regex, v);
  }
  dom.wynikRenderowania.textContent = txt;
  dom.sekcjaPodgladu.style.display = "block";
}
