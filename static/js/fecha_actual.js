document.addEventListener("DOMContentLoaded", function() {
    const hoy = new Date().toISOString().split('T')[0];

    const campoFecha = document.getElementById('fecha');
    if (campoFecha) campoFecha.value = hoy;

    const campoFechaActual = document.getElementById('Fecha_actualizacion');
    if (campoFechaActual) campoFechaActual.value = hoy;
  });