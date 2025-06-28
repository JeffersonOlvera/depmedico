  document.addEventListener("DOMContentLoaded", function () {
    const radio1 = document.getElementById("Gin_Ciclos_R");
    const radio2 = document.getElementById("Gin_Ciclos_I");

    radio1.addEventListener("change", function () {
      if (radio1.checked) radio2.checked = false;
    });

    radio2.addEventListener("change", function () {
      if (radio2.checked) radio1.checked = false;
    });


    >
  document.addEventListener("DOMContentLoaded", function () {
    const hoy = new Date().toISOString().split('T')[0];

    // Establecer fecha en 'fecha' y 'fecha_actual' si existen
    const idsFecha = ['fecha', 'fecha_actual'];
    idsFecha.forEach(id => {
      const campo = document.getElementById(id);
      if (campo) campo.value = hoy;
    });

    // Solo uno entre Gin_Ciclos_R e I
    const radioR = document.getElementById("Gin_Ciclos_R");
    const radioI = document.getElementById("Gin_Ciclos_I");

    if (radioR && radioI) {
      radioR.addEventListener("change", () => {
        if (radioR.checked) radioI.checked = false;
      });
      radioI.addEventListener("change", () => {
        if (radioI.checked) radioR.checked = false;
      });
    }

    // Función para permitir solo un checkbox activo en un grupo
    function permitirSoloUno(grupoIds) {
      grupoIds.forEach(id => {
        const checkbox = document.getElementById(id);
        if (checkbox) {
          checkbox.addEventListener("change", function () {
            if (this.checked) {
              grupoIds.forEach(otroId => {
                if (otroId !== id) {
                  const otroCheckbox = document.getElementById(otroId);
                  if (otroCheckbox) otroCheckbox.checked = false;
                }
              });
            }
          });
        }
      });
    }

    // Grupos de checkboxes: orientación sexual e identidad de género
    const orientacionIds = ['Ori_Lesbiana', 'Ori_Gay', 'Ori_Bisexual', 'Ori_Hetero', 'Ori_Omitir'];
    const identidadIds = ['femenino', 'masculino', 'transgenero', 'omite_genero'];

    permitirSoloUno(orientacionIds);
    permitirSoloUno(identidadIds);
  });
  });
