  window.onload = function () {
    var canvas = document.getElementById('signature-canvas2');
    var signaturePad = new SignaturePad(canvas);

    function resizeCanvas() {
      var ratio = Math.max(window.devicePixelRatio || 1, 1);
      canvas.width = canvas.offsetWidth * ratio;
      canvas.height = canvas.offsetHeight * ratio;
      canvas.getContext("2d").scale(ratio, ratio);
    }

    window.onresize = resizeCanvas;
    resizeCanvas();

    document.getElementById('clear-signature2').addEventListener('click', function () {
      signaturePad.clear();
    });

    document.getElementById('save-signature2').addEventListener('click', function (event) {
      event.preventDefault(); // Prevenir el comportamiento por defecto

      if (signaturePad.isEmpty()) {
        alert("Por favor, realiza una firma.");
      } else {
        var dataURL = signaturePad.toDataURL('image/png');
        document.getElementById('firma_colaborador').value = dataURL;
        console.log(document.getElementById('firma_colaborador').value);
        alert("Firma guardada");
      }
    });
  };

