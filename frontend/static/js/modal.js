/* Lógica genérica de modales para el backoffice */
document.addEventListener('DOMContentLoaded', function () {
    let elementoConFoco = null;

    function abrirModal(modal) {
        if (!modal) return;
        elementoConFoco = document.activeElement;
        modal.hidden = false;
        modal.classList.add('modal--abierto');
        document.body.classList.add('modal-abierto');

        const dialogo = modal.querySelector('.modal__dialog');
        if (dialogo) dialogo.focus();
    }

    function cerrarModal(modal) {
        if (!modal) return;
        modal.hidden = true;
        modal.classList.remove('modal--abierto');
        if (!document.querySelector('.modal--abierto')) {
            document.body.classList.remove('modal-abierto');
        }
        if (elementoConFoco && typeof elementoConFoco.focus === 'function') {
            elementoConFoco.focus();
        }
    }

    document.querySelectorAll('[data-modal-open]').forEach(function (boton) {
        boton.addEventListener('click', function () {
            abrirModal(document.getElementById(boton.dataset.modalOpen));
        });
    });

    document.querySelectorAll('[data-modal-close]').forEach(function (elemento) {
        elemento.addEventListener('click', function (evento) {
            evento.preventDefault();
            cerrarModal(elemento.closest('.modal'));
        });
    });

    document.addEventListener('keydown', function (evento) {
        if (evento.key !== 'Escape') return;
        const modalAbierto = document.querySelector('.modal--abierto');
        if (modalAbierto) cerrarModal(modalAbierto);
    });

    document.querySelectorAll('form[data-confirmar-baja]').forEach(function (formulario) {
        formulario.addEventListener('submit', function (evento) {
            const modal = document.getElementById(
                formulario.dataset.modalDestino || 'modal-confirmar-baja'
            );
            const formModal = modal ? modal.querySelector('form') : null;
            if (!modal || !formModal) return;

            evento.preventDefault();
            formModal.action = formulario.action;
            abrirModal(modal);
        });
    });
});
