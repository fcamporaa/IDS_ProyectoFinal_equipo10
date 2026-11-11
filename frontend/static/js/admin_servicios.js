document.addEventListener("DOMContentLoaded", () => {
  // Flujo unico: si viene ?nuevo=1, FORZAR formulario visible
  const urlParams = new URLSearchParams(window.location.search);
  const nuevo = urlParams.get("nuevo");
  const container = document.getElementById("contenedor-formulario");
  
  // Safety check
  if (!container) return;
  
  if (nuevo === "1") {
    // FORZAR mostrar: quitar hidden, clase activa, estilos inline
    container.removeAttribute("hidden");
    container.className = "admin-servicios__form-container admin-servicios__form-container--activo";
    container.style.display = "block";
    container.style.maxHeight = "800px";
    container.style.opacity = "1";
    
    // Focar al nombre y selecionar todo su texto
    const inputNombre = document.getElementById("nombre");
    if (inputNombre) {
      inputNombre.focus();
      inputNombre.select();
    }
    
    // Foco al select de tipo
    const inputTipo = document.getElementById("tipo");
    if (inputTipo) {
      inputTipo.focus();
    }
  }
});