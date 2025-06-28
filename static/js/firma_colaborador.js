window.onload = function () {
    const canvas = document.getElementById('signature-canvas');
    
    // Función para buscar el input con cualquiera de los dos IDs
    function getFirmaInput() {
        return document.getElementById('firma_colaborador') || 
               document.getElementById('Firma_Colaborador') ||
               document.getElementById('signature') ||
                document.getElementById('firma')
    }
    
    const firmaInput = getFirmaInput();
    
    // Verificar que encontramos los elementos necesarios
    if (!canvas) {
        console.error('No se encontró el canvas con ID "signature-canvas"');
        return;
    }
    
    if (!firmaInput) {
        console.error('No se encontró el input de firma. IDs buscados: firma_colaborador, Firma_Colaborador, signature');
        return;
    }
    
    console.log('Canvas encontrado:', canvas);
    console.log('Input encontrado:', firmaInput.id);
    
    const signaturePad = new SignaturePad(canvas, {
        // Configuración opcional para mejor experiencia
        backgroundColor: 'rgba(255,255,255,0)',
        penColor: 'rgb(0, 0, 0)',
        velocityFilterWeight: 0.7,
        minWidth: 0.5,
        maxWidth: 2.5
    });
    
    function resizeCanvas() {
        const ratio = Math.max(window.devicePixelRatio || 1, 1);
        canvas.width = canvas.offsetWidth * ratio;
        canvas.height = canvas.offsetHeight * ratio;
        canvas.getContext("2d").scale(ratio, ratio);
        
        // Preservar la firma si existe
        const signatureData = firmaInput.value;
        if (signatureData) {
            const img = new Image();
            img.onload = function() {
                canvas.getContext("2d").drawImage(img, 0, 0);
            };
            img.src = signatureData;
        }
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
                console.log("Firma guardada en el input:", firmaInput.id);
                // console.log(dataURL);  // Mostrar la URL de la firma en la consola
            } else {
                firmaInput.value = '';
                console.log("Input limpiado");
            }
        } catch (error) {
            console.error("Error al guardar la firma:", error);
        }
    }
    
    // Evento cuando se firma algo nuevo
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
    
    // Función para validar si hay firma (útil para validación de formulario)
    window.validateSignature = function() {
        if (signaturePad.isEmpty() || !firmaInput.value) {
            alert("Por favor, realiza una firma antes de continuar.");
            return false;
        }
        return true;
    };
    
    // Cargar firma existente si hay una (para edición)
    if (firmaInput.value) {
        const img = new Image();
        img.onload = function() {
            signaturePad.clear();
            canvas.getContext("2d").drawImage(img, 0, 0);
        };
        img.src = firmaInput.value;
    }
};