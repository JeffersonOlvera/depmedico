// Elementos del DOM
const slider = document.getElementById("tokenAmount");
const sliderValue = document.getElementById("sliderValue");
const tokensTextarea = document.getElementById("tokensTextarea");
const tokenCount = document.getElementById("tokenCount");
const generateBtn = document.getElementById("generateBtn");
const copyBtn = document.getElementById("copyBtn");
const downloadBtn = document.getElementById("downloadBtn");
const clearBtn = document.getElementById("clearBtn");
const toastNotification = document.getElementById("toastNotification");
const toastMessage = document.getElementById("toastMessage");
const loaderOverlay = document.getElementById("loaderOverlay");
const presetBtns = document.querySelectorAll(".preset-btn");
const formInterno = document.getElementById("form-interno");

// Actualizar contador de tokens existentes
function actualizarContadorTokens() {
  const text = tokensTextarea.value.trim();
  const lines = text
    ? text.split("\n").filter((line) => line.trim() !== "")
    : [];
  const count = lines.length;
  tokenCount.querySelector("span").textContent =
    count + (count === 1 ? " token" : " tokens");

  // Habilitar/deshabilitar botones según haya contenido
  const hasContent = count > 0;
  copyBtn.disabled = !hasContent;
  downloadBtn.disabled = !hasContent;
  clearBtn.disabled = !hasContent;

  if (!hasContent) {
    copyBtn.classList.add("disabled");
    downloadBtn.classList.add("disabled");
    clearBtn.classList.add("disabled");
  } else {
    copyBtn.classList.remove("disabled");
    downloadBtn.classList.remove("disabled");
    clearBtn.classList.remove("disabled");
  }
}

// Inicializar contador al cargar la página
window.addEventListener("DOMContentLoaded", actualizarContadorTokens);

// Actualizar el valor del slider visible
slider.addEventListener("input", () => {
  sliderValue.textContent = slider.value;

  // Actualizar botones de preset
  presetBtns.forEach((btn) => {
    if (parseInt(btn.dataset.value) === parseInt(slider.value)) {
      btn.classList.add("active");
    } else {
      btn.classList.remove("active");
    }
  });
});

// Manejar clics en botones de preset
presetBtns.forEach((btn) => {
  btn.addEventListener("click", () => {
    const value = parseInt(btn.dataset.value);
    slider.value = value;
    sliderValue.textContent = value;

    // Actualizar estado activo
    presetBtns.forEach((b) => b.classList.remove("active"));
    btn.classList.add("active");
  });
});

// Copiar tokens al portapapeles
function copiarTokens() {
  const text = tokensTextarea.value.trim();
  if (!text) {
    mostrarNotificacion("No hay tokens para copiar", "warning");
    return;
  }

  tokensTextarea.select();
  tokensTextarea.setSelectionRange(0, 99999); // para móviles

  navigator.clipboard
    .writeText(text)
    .then(() => {
      mostrarNotificacion("Tokens copiados al portapapeles", "success");

      // Efecto visual en botón
      copyBtn.classList.add("btn-success");
      copyBtn.innerHTML = '<i class="fas fa-check"></i> Copiado';

      setTimeout(() => {
        copyBtn.classList.remove("btn-success");
        copyBtn.innerHTML = '<i class="fas fa-copy"></i> Copiar';
      }, 2000);
    })
    .catch(() => {
      mostrarNotificacion(
        "Error al copiar. Por favor, copia manualmente.",
        "warning"
      );
    });
}

// Descargar tokens como archivo .txt
function descargarTokens() {
  const text = tokensTextarea.value.trim();
  if (!text) {
    mostrarNotificacion("No hay tokens para descargar", "warning");
    return;
  }

  const blob = new Blob([text], { type: "text/plain" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;

  // Nombre del archivo con fecha y hora
  const now = new Date();
  const timestamp = now.toISOString().replace(/[:.]/g, "-").substring(0, 19);
  a.download = `tokens_${timestamp}.txt`;

  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);

  mostrarNotificacion("Archivo descargado correctamente", "success");

  // Efecto visual en botón
  downloadBtn.classList.add("btn-success");
  downloadBtn.innerHTML = '<i class="fas fa-check"></i> Descargado';

  setTimeout(() => {
    downloadBtn.classList.remove("btn-success");
    downloadBtn.innerHTML = '<i class="fas fa-download"></i> Descargar';
  }, 2000);
}

// Limpiar tokens
function limpiarTokens() {
  if (tokensTextarea.value.trim() === "") {
    return;
  }

  tokensTextarea.value = "";
  actualizarContadorTokens();
  mostrarNotificacion("Tokens eliminados", "success");
}

// Mostrar notificación temporal
function mostrarNotificacion(mensaje, tipo = "success") {
  toastMessage.textContent = mensaje;
  toastNotification.className = "toast-notification";

  if (tipo === "success") {
    toastNotification.classList.add("toast-success");
    toastNotification.querySelector(".toast-icon").className =
      "fas fa-check-circle toast-icon";
  } else if (tipo === "warning") {
    toastNotification.classList.add("toast-warning");
    toastNotification.querySelector(".toast-icon").className =
      "fas fa-exclamation-circle toast-icon";
  }

  toastNotification.classList.add("show");
  setTimeout(() => toastNotification.classList.remove("show"), 3000);
}

// Simular carga al generar tokens
formInterno.addEventListener("submit", (e) => {
  loaderOverlay.classList.add("show");
  generateBtn.disabled = true;
  generateBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Generando...';

  // Este timeout es solo para simular la carga en esta demo
  // En un entorno real, esto no sería necesario ya que la página se recargaría
  setTimeout(() => {
    loaderOverlay.classList.remove("show");
    generateBtn.disabled = false;
    generateBtn.innerHTML = '<i class="fas fa-key"></i> Generar Tokens';
  }, 3000);
});

