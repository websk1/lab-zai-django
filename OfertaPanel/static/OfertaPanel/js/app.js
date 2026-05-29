import { dom, state, backendBaseUrl } from "./config.js";
import {
  pobierzPolaZBackendu,
  pobierzListeDokumentowZBackendu,
} from "./api.js";
import { zresetujWidok, pokazKomunikat } from "./ui.js";
import { renderujSzablon } from "./logic.js";

// ================= INIT =================
async function init() {
  pobierzPolaZBackendu();
  pobierzListeDokumentowZBackendu();
  obslugaZdarzen();
  zresetujWidok("formularz");
}

function obslugaZdarzen() {
  dom.btnFormularz.onclick = () => zresetujWidok("formularz");
  dom.btnSzablon.onclick = () => zresetujWidok("szablon");
  dom.btnDaneTestowe.onclick = renderujSzablon;

  // Filtrowanie listy
  dom.inputFiltr.addEventListener("input", (e) => {
    const fraza = e.target.value.toLowerCase();
    dom.listaDokumentow.querySelectorAll(".element-listy").forEach((el) => {
      const nazwa = el.querySelector(".nazwa-pliku").textContent.toLowerCase();
      el.style.display = nazwa.includes(fraza) ? "flex" : "none";
    });
  });

  // ZAPIS (SAVE)
  dom.btnZapisz.onclick = async () => {
    const wpisanaNazwa = dom.inputNazwaDokumentu.value.trim();
    if (!wpisanaNazwa) {
      return pokazKomunikat("Podaj nazwę pliku przed zapisem!", "blad");
    }

    const wybraneZrodloRadio = Array.from(dom.radiosTrybZapisu).find(
      (radio) => radio.checked
    ).value;
    let payload = {};

    if (state.aktualnyTryb === "formularz") {
      const pola = Array.from(dom.kontenerPolFormularza.children).map(
        (d) => d.dataset.pole
      );
      if (!pola.length) return pokazKomunikat("Pusty formularz", "blad");
      payload = { typ: "formularz", pola: pola };
    } else {
      const tresc = dom.textareaSzablon.value;
      if (!tresc) return pokazKomunikat("Pusty szablon", "blad");
      payload = { typ: "szablon", tresc: tresc };
    }

    payload.nazwa = wpisanaNazwa;
    let targetSource = "";

    if (state.edytowanyDokumentId !== null) {
      payload.id = state.edytowanyDokumentId;
      payload.metoda = "UPDATE";
      targetSource = state.edytowaneZrodlo;
    } else {
      targetSource = wybraneZrodloRadio;
    }

    // Funkcja pobierająca ciasteczka dla tokenu CSRF Django
    function getCookie(name) {
      let cookieValue = null;
      if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
          const cookie = cookies[i].trim();
          if (cookie.substring(0, name.length + 1) === (name + '=')) {
            cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
            break;
          }
        }
      }
      return cookieValue;
    }

    try {
      pokazKomunikat("Zapisywanie...", "info");
      const csrftoken = getCookie('csrftoken');
      const response = await fetch(
        `${backendBaseUrl}/save/?source=${targetSource}`,
        {
          method: "POST",
          headers: { 
            "Content-Type": "application/json",
            "X-CSRFToken": csrftoken
          },
          body: JSON.stringify(payload),
        }
      );

      const result = await response.json();

      if (result.status === "ok") {
        pokazKomunikat(result.message, "sukces");
        await pobierzListeDokumentowZBackendu();
        if (state.edytowanyDokumentId === null)
          zresetujWidok(state.aktualnyTryb);
      } else {
        pokazKomunikat("Błąd serwera: " + result.message, "blad");
      }
    } catch (e) {
      console.error(e);
      pokazKomunikat("Błąd połączenia", "blad");
    }
  };

  // Delegacja zdarzeń formularza
  dom.kontenerPolFormularza.onclick = (e) => {
    const w = e.target.closest(".wiersz-pola");
    if (!w) return;
    if (e.target.classList.contains("btn-usun")) w.remove();
    if (e.target.classList.contains("btn-gora") && w.previousElementSibling)
      w.parentNode.insertBefore(w, w.previousElementSibling);
    if (e.target.classList.contains("btn-dol") && w.nextElementSibling)
      w.parentNode.insertBefore(w, w.nextElementSibling.nextElementSibling);
  };
}

init();
