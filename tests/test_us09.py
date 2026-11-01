"""Pruebas de funciones puras de US-09; requieren pytest en el entorno de desarrollo."""
import os
import sys
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "backend"))

from src.validators.compras_validators import validar_datos_compra
from src.services.qr_services import crear_token_qr, crear_imagen_qr
from src.utils import enviar_correo_html, renderizar_correo_html, es_email_valido


def payload_valido():
    return {
        "id_funcion": 5, "butacas_ids": [101, 102],
        "servicios": [], "medio_pago": "TARJETA_SIMULADA",
        "email_comprobante": "cliente@ejemplo.com",
    }


def compra_demo():
    return {
        "codigo_reserva": "CP-EJEMPLO", "pelicula": "Volver al Futuro",
        "local": "Abasto", "sala": 2, "inicio": "2026-11-01T20:00",
        "total": 9000.0,
        "entradas": [{"fila": "F", "numero": 7}, {"fila": "F", "numero": 8}],
    }


def test_validacion_acepta_datos():
    assert validar_datos_compra(payload_valido())["butacas_ids"] == [101, 102]


def test_validacion_rechaza_duplicado():
    datos = payload_valido()
    datos["butacas_ids"] = [101, 101]
    with pytest.raises(ValueError):
        validar_datos_compra(datos)


def test_validacion_rechaza_pago_real_no_integrado():
    datos = payload_valido()
    datos["medio_pago"] = "TARJETA_CREDITO"
    with pytest.raises(ValueError) as exc:
        validar_datos_compra(datos)
    assert exc.value.args[1] == 501


def test_validacion_rechaza_bool_en_id():
    datos = payload_valido()
    datos["id_funcion"] = True
    with pytest.raises(ValueError):
        validar_datos_compra(datos)


def test_utilidad_email():
    assert es_email_valido("a@b.com")
    assert not es_email_valido("sin-correo")


def test_token_qr_aleatorio_y_png():
    assert crear_token_qr() != crear_token_qr()
    png = crear_imagen_qr(crear_token_qr())
    assert png.startswith(b"\x89PNG\r\n\x1a\n")


def test_correo_confirmado_tiene_qr_y_escape():
    compra = compra_demo()
    compra["pelicula"] = "<script>malicioso()</script>"
    html = renderizar_correo_html("compra_confirmada", compra)
    assert 'cid:entrada-qr' in html
    assert '<script>' not in html
    assert '&lt;script&gt;' in html


def test_correo_provisorio_sin_qr():
    html = renderizar_correo_html("comprobante_provisorio", compra_demo())
    assert 'cid:' not in html
    assert 'NO habilita el ingreso' in html


def test_plantilla_no_admitida():
    with pytest.raises(ValueError):
        renderizar_correo_html("../../cualquier_archivo", {})


def test_email_console_no_envia(monkeypatch):
    monkeypatch.setenv("EMAIL_MODE", "console")
    with patch("smtplib.SMTP") as smtp:
        assert enviar_correo_html("cliente@ejemplo.com", "Asunto", "comprobante_provisorio", compra_demo()) == "SIMULADO"
        smtp.assert_not_called()


def test_correo_smtp_inline(monkeypatch):
    monkeypatch.setenv("EMAIL_MODE", "smtp")
    monkeypatch.setenv("SMTP_HOST", "localhost")
    monkeypatch.setenv("SMTP_FROM", "cine@ejemplo.com")
    monkeypatch.setenv("SMTP_USER", "")
    servidor = Mock()
    servidor.__enter__ = Mock(return_value=servidor)
    servidor.__exit__ = Mock(return_value=False)
    with patch("smtplib.SMTP", return_value=servidor):
        assert enviar_correo_html(
            "cliente@ejemplo.com", "Entrada", "compra_confirmada",
            compra_demo(), {"entrada-qr": crear_imagen_qr(crear_token_qr())}
        ) == "ENVIADO"
    mensaje = servidor.send_message.call_args.args[0]
    assert 'image/png' in str(mensaje)
    assert 'Content-ID: <entrada-qr>' in str(mensaje)
