(function () {
  "use strict";

  var LANGUAGES = ["pl", "en", "es", "ca", "lt", "sk", "cs", "pt"];
  var MACHINES = ["48", "128"];
  var params = new URLSearchParams(window.location.search);
  var language = LANGUAGES.indexOf(params.get("lang")) >= 0 ? params.get("lang") : "pl";
  var machine = MACHINES.indexOf(params.get("machine")) >= 0 ? params.get("machine") : "128";

  var editionForm = document.getElementById("edition-form");
  var languageSelect = document.getElementById("language");
  var machineInputs = document.querySelectorAll('input[name="machine"]');
  var tapeName = document.getElementById("tape-name");
  var releaseName = document.getElementById("release-name");
  var emulatorStatus = document.getElementById("emulator-status");
  var downloadTape = document.getElementById("download-tape");
  var stage = document.getElementById("jsspeccy");
  var emulator = null;

  languageSelect.value = language;
  document.querySelector('input[name="machine"][value="' + machine + '"]').checked = true;

  fetch("release.json", { cache: "no-store" })
    .then(function (response) {
      if (!response.ok) {
        throw new Error("release metadata unavailable");
      }
      return response.json();
    })
    .then(function (release) {
      releaseName.textContent = release.tagName || "latest";
    })
    .catch(function () {
      releaseName.textContent = "latest";
    });

  function selectedLanguage() {
    return LANGUAGES.indexOf(languageSelect.value) >= 0 ? languageSelect.value : "pl";
  }

  function selectedMachine() {
    var checked = document.querySelector('input[name="machine"]:checked');
    return checked && MACHINES.indexOf(checked.value) >= 0 ? checked.value : "128";
  }

  function tapePath() {
    return "taps/hangman-" + selectedLanguage() + "-" + selectedMachine() + ".tap";
  }

  function rememberSelection() {
    if (!window.history || !window.history.replaceState) {
      return;
    }
    var url = new URL(window.location.href);
    url.searchParams.set("lang", selectedLanguage());
    url.searchParams.set("machine", selectedMachine());
    window.history.replaceState(null, "", url.toString());
  }

  /* The JSSpeccy 3 public API has setMachine and openUrl but no start(), so a
     paused emulator would swap tapes invisibly. Replace the instance instead. */
  function loadSelectedTape(autoStart) {
    var path = tapePath();

    tapeName.textContent = path.split("/").pop();
    downloadTape.href = path;
    rememberSelection();

    if (typeof window.JSSpeccy !== "function") {
      emulatorStatus.textContent = "emulator failed to load";
      emulatorStatus.dataset.state = "error";
      return;
    }

    delete emulatorStatus.dataset.state;
    emulatorStatus.textContent = "loading " + selectedMachine() + "K tape…";

    if (emulator) {
      emulator.exit();
      emulator = null;
    }

    try {
      emulator = window.JSSpeccy(stage, {
        machine: Number(selectedMachine()),
        openUrl: path,
        autoLoadTapes: true,
        autoStart: autoStart,
        zoom: window.matchMedia("(min-width: 45rem)").matches ? 2 : 1
      });
    } catch (error) {
      console.error("JSSpeccy failed to start", error);
      emulatorStatus.textContent = "emulator failed to start";
      emulatorStatus.dataset.state = "error";
      return;
    }

    emulator.onReady(function () {
      emulatorStatus.textContent = autoStart ? "running" : "ready — press Play";
    });
  }

  /* Changing either control is enough; the button only reloads the same tape. */
  languageSelect.addEventListener("change", function () {
    loadSelectedTape(true);
  });

  Array.prototype.forEach.call(machineInputs, function (input) {
    input.addEventListener("change", function () {
      loadSelectedTape(true);
    });
  });

  editionForm.addEventListener("submit", function (event) {
    event.preventDefault();
    loadSelectedTape(true);
  });

  loadSelectedTape(false);
})();
