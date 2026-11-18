document.addEventListener("DOMContentLoaded", () => {
  // Flujo unico: si viene ?nuevo=1, FORZAR formulario visible
  const urlParams = new URLSearchParams(window.location.search);
  const nuevo = urlParams.get("nuevo");
  const container = document.getElementById("contenedor-formulario");
  const form = document.querySelector(".formulario-servicio");
  const imagenInput = document.getElementById("imagen_url");
  const imagenError = document.getElementById("imagen-url-error");
  const imagenPreview = document.getElementById("imagen-preview");
  const previewMensaje = document.getElementById("imagen-preview-mensaje");

  if (form && imagenInput && imagenError && imagenPreview && previewMensaje) {
    const validarImagenUrl = () => {
      const valor = imagenInput.value.trim();
      let mensaje = "";
      let url = null;

      if (!valor) {
        mensaje = "El enlace de la imagen es obligatorio.";
      } else {
        try {
          url = new URL(valor);
          if (!["http:", "https:"].includes(url.protocol) || !url.hostname) {
            mensaje = "Ingresá una URL válida que comience con http:// o https://.";
          }
        } catch {
          mensaje = "Ingresá una URL válida que comience con http:// o https://.";
        }
      }

      imagenInput.setCustomValidity(mensaje);
      imagenInput.setAttribute("aria-invalid", mensaje ? "true" : "false");
      imagenError.textContent = mensaje;

      if (mensaje || !url) {
        imagenPreview.hidden = true;
        imagenPreview.removeAttribute("src");
        previewMensaje.textContent = mensaje || "La vista previa aparecerá cuando ingreses un enlace válido.";
        previewMensaje.hidden = false;
        return false;
      }

      const enlaceActual = valor;
      imagenPreview.onload = () => {
        if (imagenInput.value.trim() === enlaceActual) {
          previewMensaje.hidden = true;
          imagenPreview.hidden = false;
        }
      };
      imagenPreview.onerror = () => {
        if (imagenInput.value.trim() === enlaceActual) {
          imagenPreview.hidden = true;
          previewMensaje.textContent = "No se pudo cargar la vista previa desde ese enlace.";
          previewMensaje.hidden = false;
        }
      };
      imagenPreview.hidden = false;
      previewMensaje.hidden = true;
      imagenPreview.src = url.href;
      return true;
    };

    imagenInput.addEventListener("input", validarImagenUrl);
    imagenInput.addEventListener("blur", validarImagenUrl);
    imagenInput.addEventListener("invalid", validarImagenUrl);
    form.addEventListener("submit", (event) => {
      if (!validarImagenUrl()) {
        event.preventDefault();
        imagenInput.reportValidity();
      }
    });
    if (imagenInput.value) validarImagenUrl();
  }
  
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