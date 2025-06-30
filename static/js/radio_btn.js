// Script para permitir solo una selección en orientación sexual e identidad de género

document.addEventListener('DOMContentLoaded', function() {
    
  // Grupos de orientación sexual (checkboxes que actúan como radio buttons)
  const orientacionSexual = [
      'Ori_Lesbiana',
      'Ori_Gay', 
      'Ori_Bisexual',
      'Ori_Hetero',
      'Ori_Omitir'
  ];
  
  // Grupos de identidad de género (radio buttons)
  const identidadGenero = [
      'femenino',
      'masculino', 
      'transgenero',
      'omite_genero'
  ];
  
  // Grupos de ciclos ginecológicos (radio buttons)
  const ciclosGinecologicos = [
      'Gin_Ciclos_R',
      'Gin_Ciclos_I'
  ];
  
  // Función para manejar selección única en orientación sexual
  function handleOrientacionSelection(selectedId) {
      orientacionSexual.forEach(id => {
          const checkbox = document.getElementById(id);
          if (checkbox && checkbox.id !== selectedId) {
              checkbox.checked = false;
          }
      });
  }
  
  // Función para manejar selección única en identidad de género
  function handleIdentidadSelection(selectedId) {
      identidadGenero.forEach(id => {
          const radio = document.getElementById(id);
          if (radio && radio.id !== selectedId) {
              radio.checked = false;
          }
      });
  }
  
  // Función para manejar selección única en ciclos ginecológicos
  function handleCiclosSelection(selectedId) {
      ciclosGinecologicos.forEach(id => {
          const radio = document.getElementById(id);
          if (radio && radio.id !== selectedId) {
              radio.checked = false;
          }
      });
  }
  
  // Agregar event listeners para orientación sexual
  orientacionSexual.forEach(id => {
      const checkbox = document.getElementById(id);
      if (checkbox) {
          checkbox.addEventListener('change', function() {
              if (this.checked) {
                  handleOrientacionSelection(this.id);
              }
          });
      }
  });
  
  // Agregar event listeners para identidad de género (aunque ya funcionan como radio buttons)
  identidadGenero.forEach(id => {
      const radio = document.getElementById(id);
      if (radio) {
          radio.addEventListener('change', function() {
              if (this.checked) {
                  handleIdentidadSelection(this.id);
              }
          });
      }
  });
  
  // Agregar event listeners para ciclos ginecológicos
  ciclosGinecologicos.forEach(id => {
      const radio = document.getElementById(id);
      if (radio) {
          radio.addEventListener('change', function() {
              if (this.checked) {
                  handleCiclosSelection(this.id);
              }
          });
      }
  });
  
  // Función adicional para resetear todas las selecciones si es necesario
  function resetSelections() {
      // Reset orientación sexual
      orientacionSexual.forEach(id => {
          const checkbox = document.getElementById(id);
          if (checkbox) checkbox.checked = false;
      });
      
      // Reset identidad de género
      identidadGenero.forEach(id => {
          const radio = document.getElementById(id);
          if (radio) radio.checked = false;
      });
      
      // Reset ciclos ginecológicos
      ciclosGinecologicos.forEach(id => {
          const radio = document.getElementById(id);
          if (radio) radio.checked = false;
      });
  }
  
  // Exponer función de reset globalmente si es necesaria
  window.resetGenderSelections = resetSelections;
  
  console.log('Script de selección única cargado correctamente');
});

// Versión alternativa más compacta si prefieres:
/*
document.addEventListener('DOMContentLoaded', function() {
  // Para orientación sexual - convertir checkboxes en comportamiento de radio
  const oriCheckboxes = document.querySelectorAll('input[name^="Ori_"]');
  oriCheckboxes.forEach(checkbox => {
      checkbox.addEventListener('change', function() {
          if (this.checked) {
              oriCheckboxes.forEach(cb => {
                  if (cb !== this) cb.checked = false;
              });
          }
      });
  });
  
  // Para identidad de género - asegurar comportamiento de radio
  const genRadios = document.querySelectorAll('input[name^="Iden_"]');
  genRadios.forEach(radio => {
      radio.addEventListener('change', function() {
          if (this.checked) {
              genRadios.forEach(r => {
                  if (r !== this) r.checked = false;
              });
          }
      });
  });
  
  // Para ciclos ginecológicos - asegurar comportamiento de radio
  const ciclosRadios = document.querySelectorAll('input[name^="Gin_Ciclos_"]');
  ciclosRadios.forEach(radio => {
      radio.addEventListener('change', function() {
          if (this.checked) {
              ciclosRadios.forEach(r => {
                  if (r !== this) r.checked = false;
              });
          }
      });
  });
});
*/