// Funcionalidad del menú móvil
function toggleMobileMenu() {
  const sidebar = document.getElementById("sidebar");
  sidebar.classList.toggle("mobile-open");
}

// Cerrar menú móvil al hacer clic fuera
document.addEventListener("click", function (event) {
  const sidebar = document.getElementById("sidebar");
  const mobileBtn = document.querySelector(".mobile-menu-btn");

  if (
    window.innerWidth <= 768 &&
    !sidebar.contains(event.target) &&
    !mobileBtn.contains(event.target)
  ) {
    sidebar.classList.remove("mobile-open");
  }
});

// Funcionalidad de búsqueda
document.getElementById("busqueda").addEventListener("input", function (e) {
  const searchTerm = e.target.value.toLowerCase();
  // Aquí puedes agregar la lógica de búsqueda
  console.log("Buscando:", searchTerm);
});

// Funcionalidad de filtro
document
  .getElementById("filtroEstado")
  .addEventListener("change", function (e) {
    const filterValue = e.target.value;
    // Aquí puedes agregar la lógica de filtrado
    console.log("Filtrando por:", filterValue);
  });

// Agregar efecto de ripple a los botones
document.querySelectorAll(".nav a").forEach((link) => {
  link.addEventListener("click", function (e) {
    // Remover active de otros elementos
    document
      .querySelectorAll(".nav a")
      .forEach((l) => l.classList.remove("active"));
    // Agregar active al elemento clickeado
    this.classList.add("active");
  });
});
