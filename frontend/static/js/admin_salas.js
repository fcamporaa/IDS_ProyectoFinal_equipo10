document.addEventListener("DOMContentLoaded", () => {
  const urlParams = new URLSearchParams(window.location.search);
  const nuevo = urlParams.get("nuevo");
  const container = document.getElementById("contenedor-formulario");

  if (!container) return;

  if (nuevo === "1") {
    container.classList.add("admin-salas__form-container--activo");
    const inputLocal = document.getElementById("id_local");
    if (inputLocal) {
      inputLocal.focus();
    }
  }
});
