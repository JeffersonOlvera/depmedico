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
    
    // Grupo de evaluación (checkboxes que actúan como radio buttons)
    const evaluacion = [
        'ingreso',
        'periodico',
        'reintegro'
    ];
    
    // Grupo de aptitud (radio buttons)
    const aptitud = [
        'apto',
        'apto_observacion',
        'apto_limitaciones',
        'no_apto'
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
    
    // Función para manejar selección única en evaluación
    function handleEvaluacionSelection(selectedId) {
        evaluacion.forEach(id => {
            const checkbox = document.getElementById(id);
            if (checkbox && checkbox.id !== selectedId) {
                checkbox.checked = false;
            }
        });
    }
    
    // Función para manejar selección única en aptitud
    function handleAptitudSelection(selectedId) {
        aptitud.forEach(id => {
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
    
    // Agregar event listeners para identidad de género
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
    
    // Agregar event listeners para evaluación
    evaluacion.forEach(id => {
        const checkbox = document.getElementById(id);
        if (checkbox) {
            checkbox.addEventListener('change', function() {
                if (this.checked) {
                    handleEvaluacionSelection(this.id);
                }
            });
        }
    });
    
    // Agregar event listeners para aptitud
    aptitud.forEach(id => {
        const radio = document.getElementById(id);
        if (radio) {
            radio.addEventListener('change', function() {
                if (this.checked) {
                    handleAptitudSelection(this.id);
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
        
        // Reset evaluación
        evaluacion.forEach(id => {
            const checkbox = document.getElementById(id);
            if (checkbox) checkbox.checked = false;
        });
        
        // Reset aptitud
        aptitud.forEach(id => {
            const radio = document.getElementById(id);
            if (radio) radio.checked = false;
        });
    }
    
    // Exponer función de reset globalmente si es necesaria
    window.resetGenderSelections = resetSelections;
    
    console.log('Script de selección única cargado correctamente');
});