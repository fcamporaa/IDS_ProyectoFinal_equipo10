from flask import Flask, jsonify
from werkzeug.exceptions import HTTPException

from src.utils import construir_error_api
from src.routes.auth_routes import register_auth_routes
from src.routes.peliculas_routes import register_peliculas_routes
from src.routes.salas_routes import register_salas_routes
from src.routes.funciones_routes import register_funciones_routes
from src.routes.servicios_routes import register_servicios_routes
from src.routes.compras_routes import register_compras_routes
from src.routes.validaciones_routes import register_validaciones_routes
from src.routes.dashboard_routes import register_dashboard_routes

app = Flask(__name__)
app.json.ensure_ascii = False
app.json.sort_keys = False


# Manejador de error general HTTP (404, 405, etc.)
@app.errorhandler(Exception)
def handle_unexpected_error(error):
    if isinstance(error, HTTPException):
        return jsonify(
            construir_error_api(
                code=f"http.{error.code}",
                message=error.name,
                description=error.description,
            )
        ), error.code

    return jsonify(
        construir_error_api(
            code="internal.server.error",
            message="Error interno del servidor",
            description="Ocurrió un error inesperado al procesar la solicitud",
        )
    ), 500


# Manejo de error de validación estándar (ValueError lanzado en validadores/servicios)
@app.errorhandler(ValueError)
def handle_value_error(error):
    status = error.args[1] if len(error.args) > 1 else 400
    return jsonify(error.args[0]), status


# Registro de rutas modulares por dominio
register_auth_routes(app)
register_peliculas_routes(app)
register_salas_routes(app)
register_funciones_routes(app)
register_servicios_routes(app)
register_compras_routes(app)
register_validaciones_routes(app)
register_dashboard_routes(app)

if __name__ == "__main__":
    app.run(debug=True)
