(function () {
  "use strict";

  var LANGUAGES = ["pl", "en", "es", "ca", "lt", "sk", "cs", "pt"];
  var MACHINES = ["48", "128"];
  var params = new URLSearchParams(window.location.search);
  var language = LANGUAGES.indexOf(params.get("lang")) >= 0 ? params.get("lang") : "pl";
  var machine = MACHINES.indexOf(params.get("machine")) >= 0 ? params.get("machine") : "128";
  var tapePath = "taps/hangman-" + language + "-" + machine + ".tap";

  var languageSelect = document.getElementById("language");
  var machineInput = document.querySelector('input[name="machine"][value="' + machine + '"]');
  var tapeName = document.getElementById("tape-name");
  var releaseName = document.getElementById("release-name");
  var emulatorStatus = document.getElementById("emulator-status");
  var downloadTape = document.getElementById("download-tape");

  languageSelect.value = language;
  machineInput.checked = true;
  tapeName.textContent = tapePath.split("/").pop();
  downloadTape.href = tapePath;

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

  if (typeof window.JSSpeccy !== "function") {
    emulatorStatus.textContent = "emulator failed to load";
    emulatorStatus.dataset.state = "error";
    return;
  }

  emulatorStatus.textContent = "loading " + machine + "K tape…";

  try {
    var emulator = window.JSSpeccy(document.getElementById("jsspeccy"), {
      machine: Number(machine),
      openUrl: tapePath,
      autoLoadTapes: true,
      zoom: window.matchMedia("(min-width: 45rem)").matches ? 2 : 1
    });

    emulator.onReady(function () {
      emulatorStatus.textContent = "ready — press Play";
    });
  } catch (error) {
    emulatorStatus.textContent = "emulator failed to start";
    emulatorStatus.dataset.state = "error";
  }
})();
