import { pokazKomunikat } from "./ui.js";
import {
  wczytajDokumentDoEdycji,
  generujPrzyciskiPol,
  generujListeDokumentow,
} from "./ui.js";
import { backendBaseUrl } from "./config.js";

// ================= LOGIKA BACKENDU (FETCH) =================
export async function pobierzPolaZBackendu() {
  try {
    const response = await fetch(`${backendBaseUrl}/get_fields/`);
    if (!response.ok) throw new Error("Błąd sieci");
    const pola = await response.json();
    generujPrzyciskiPol(pola);
  } catch (error) {
    console.error(error);
    pokazKomunikat("Błąd API: get_fields", "blad");
  }
}

export async function pobierzListeDokumentowZBackendu() {
  try {
    const response = await fetch(`${backendBaseUrl}/list/`);
    if (!response.ok) throw new Error("Błąd sieci");
    const lista = await response.json();
    generujListeDokumentow(lista);
  } catch (error) {
    console.error(error);
    pokazKomunikat("Błąd API: list", "blad");
  }
}

export async function pobierzDokumentZBackendu(id, source) {
  pokazKomunikat("Pobieranie...", "info");
  try {
    const url = `${backendBaseUrl}/get_document/?id=${encodeURIComponent(
      id
    )}&source=${source}`;
    const response = await fetch(url);
    if (!response.ok) throw new Error("404");

    const dokument = await response.json();
    wczytajDokumentDoEdycji(dokument);
  } catch (error) {
    console.error(error);
    pokazKomunikat("Błąd pobierania dokumentu", "blad");
  }
}

