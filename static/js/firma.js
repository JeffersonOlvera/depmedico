window.onload = function () {
  const canvas = document.getElementById('signature-canvas');
  
  // Función para buscar el input con cualquiera de los IDs posibles
  function getFirmaInput() {
      return document.getElementById('firma_colaborador') || 
             document.getElementById('Firma_Colaborador') ||
             document.getElementById('signature') ||
             document.getElementById('firma');
  }
  
  const firmaInput = getFirmaInput();
  
  // Verificar que encontramos los elementos necesarios
  if (!canvas) {
      console.error('No se encontró el canvas con ID "signature-canvas"');
      return;
  }
  
  if (!firmaInput) {
      console.error('No se encontró el input de firma. IDs buscados: firma_colaborador, Firma_Colaborador, signature, firma');
      return;
  }
  
  console.log('Canvas encontrado:', canvas);
  console.log('Input encontrado:', firmaInput.id);
  
  const context = canvas.getContext('2d');
  const signaturePad = new SignaturePad(canvas, {
      // Configuración opcional para mejor experiencia
      backgroundColor: 'rgba(255,255,255,0)',
      penColor: 'rgb(0, 0, 0)',
      velocityFilterWeight: 0.7,
      minWidth: 0.5,
      maxWidth: 2.5
  });
  
  // Función para centrar y escalar la imagen en el canvas
  function drawCenteredImage(image) {
      const canvasAspect = canvas.width / canvas.height;
      const imageAspect = image.width / image.height;
      let renderableWidth, renderableHeight, xStart, yStart;

      // Ajustar el tamaño de la imagen para que encaje en el canvas
      if (imageAspect < canvasAspect) {
          // La imagen es más alta que el canvas, ajustar el ancho
          renderableHeight = canvas.height;
          renderableWidth = image.width * (canvas.height / image.height);
          xStart = (canvas.width - renderableWidth) / 2;
          yStart = 0;
      } else {
          // La imagen es más ancha que el canvas, ajustar la altura
          renderableWidth = canvas.width;
          renderableHeight = image.height * (canvas.width / image.width);
          xStart = 0;
          yStart = (canvas.height - renderableHeight) / 2;
      }

      // Dibujar la imagen centrada
      context.clearRect(0, 0, canvas.width, canvas.height);
      context.drawImage(image, xStart, yStart, renderableWidth, renderableHeight);
  }
  
  // Función para cargar la firma existente
  function loadExistingSignature() {
      // Intentar obtener la firma desde diferentes fuentes
      let base64FirmaGuardada = firmaInput.value;
      
      // Si hay una variable global de template, usarla
      if (typeof form_data !== 'undefined' && form_data.Firma_colaborador) {
          base64FirmaGuardada = form_data.Firma_colaborador;
      }
      
      // Si hay una variable global específica para la firma
      if (typeof firma_colaborador !== 'undefined' && firma_colaborador) {
          base64FirmaGuardada = firma_colaborador;
      }
      
      // Verificar que tenemos una firma válida para cargar
      if (base64FirmaGuardada && 
          base64FirmaGuardada.trim() !== '' && 
          !base64FirmaGuardada.includes('{{') && 
          !base64FirmaGuardada.includes('}}')) {
          
          // Verificar que el base64 tenga el formato correcto
          if (!base64FirmaGuardada.startsWith('data:image/')) {
              base64FirmaGuardada = 'data:image/png;base64,' + base64FirmaGuardada;
          }
          
          const image = new Image();
          image.onload = function () {
              // Usar SignaturePad para cargar la imagen
              signaturePad.fromDataURL(base64FirmaGuardada);
              
              // También actualizar el input hidden con el valor existente
              firmaInput.value = base64FirmaGuardada;
              console.log("Firma existente cargada");
          };
          image.onerror = function() {
              console.error('Error al cargar la firma existente - URL inválida');
          };
          image.src = base64FirmaGuardada;
      } else {
          console.log("No hay firma existente para cargar o contiene templates sin procesar");
      }
  }
  
  function resizeCanvas() {
      const ratio = Math.max(window.devicePixelRatio || 1, 1);
      canvas.width = canvas.offsetWidth * ratio;
      canvas.height = canvas.offsetHeight * ratio;
      context.scale(ratio, ratio);
      
      // Recargar la imagen después de redimensionar si existe
      loadExistingSignature();
  }
  
  // Ajustar tamaño del canvas
  window.onresize = resizeCanvas;
  resizeCanvas();
  
  // Guardar automáticamente cada vez que se dibuja
  function saveToInput() {
      try {
          if (!signaturePad.isEmpty()) {
              const dataURL = signaturePad.toDataURL('image/png');
              firmaInput.value = dataURL;
              console.log("Firma guardada automáticamente en el input:", firmaInput.id);
          } else {
              firmaInput.value = '';
              console.log("Input limpiado");
          }
      } catch (error) {
          console.error("Error al guardar la firma:", error);
      }
  }
  
  // Evento cuando se firma algo nuevo (guardado automático)
  signaturePad.onEnd = saveToInput;
  
  // Botón limpiar con verificación
  const clearButton = document.getElementById('clear-signature');
  if (clearButton) {
      clearButton.addEventListener('click', function () {
          signaturePad.clear();
          saveToInput();  // Limpiar también el input oculto
          console.log("Firma limpiada");
      });
  } else {
      console.warn('No se encontró el botón con ID "clear-signature"');
  }
  
  // Botón guardar manual (opcional, compatible con el segundo script)
  const saveButton = document.getElementById('save-signature');
  if (saveButton) {
      saveButton.addEventListener('click', function (event) {
          event.preventDefault(); // Prevenir comportamiento por defecto

          if (signaturePad.isEmpty()) {
              alert("Por favor, realiza una firma.");
          } else {
              const dataURL = signaturePad.toDataURL('image/png');
              firmaInput.value = dataURL;
              alert("Firma guardada");
              console.log("Firma guardada manualmente");
          }
      });
  }
  
  // Función para validar si hay firma (útil para validación de formulario)
  window.validateSignature = function() {
      if (signaturePad.isEmpty() || !firmaInput.value) {
          alert("Por favor, realiza una firma antes de continuar.");
          return false;
      }
      return true;
  };
  
  // Cargar firma existente al inicializar
  loadExistingSignature();
};