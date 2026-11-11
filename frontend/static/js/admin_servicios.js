document.addEventListener("DOMContentLoaded", () => {
  // Manejo de modales (abrir/cerrar)
  const botonesAbrirModal = document.querySelectorAll("[data-modal-target]");
  const elementosCerrarModal = document.querySelectorAll("[data-modal-close]");

  botonesAbrirModal.forEach((boton) => {
    boton.addEventListener("click", () => {
      const modalId = boton.getAttribute("data-modal-target");
      const modal = document.getElementById(modalId);
      if (modal) {
        modal.removeAttribute("hidden");
        document.body.classList.add("modal-abierto");
      }
    });
  });

  const cerrarModal = (modal) => {
    if (modal) {
      modal.setAttribute("hidden", "true");
      document.body.classList.remove("modal-abierto");
    }
  };

  elementosCerrarModal.forEach((elem) => {
    elem.addEventListener("click", () => {
      const modal = elem.closest(".modal");
      cerrarModal(modal);
    });
  });

  window.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
      const modalAbierto = document.querySelector(".modal:not([hidden])");
      if (modalAbierto) {
        cerrarModal(modalAbierto);
      }
    }
  });

  // Manejo de query param ?nuevo=1 para abrir el formulario automáticamente
  const urlParams = new URLSearchParams(window.location.search);
  const containerFormulario = document.getElementById("contenedor-formulario");
  if (urlParams.get("nuevo") === "1" && containerFormulario) {
    containerFormulario.classList.add("admin-servicios__form-container--activo");
    const inputNombre = document.getElementById("nombre");
    if (inputNombre) {
      inputNombre.focus();
    }
  }
});
