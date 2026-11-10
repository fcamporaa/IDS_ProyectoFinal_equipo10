import os
from dotenv import load_dotenv
from flask import Flask, session

from routes.dashboard_routes import dashboard_bp
from routes.home_routes import home_bp

from routes.peliculas_routes import peliculas_bp 
from routes.admin_funciones_routes import admin_funciones_bp
from routes.compras_routes import compras_bp




from routes.compra_routes import compra_bp
from routes.auth_routes import auth_bp

load_dotenv()

app = Flask(__name__)

# Configuración básica de la aplicación
if len(os.getenv("SECRET_KEY", "")) < 32:
    raise RuntimeError("Configurá SECRET_KEY (mínimo 32 caracteres) en el frontend.")
app.config["SECRET_KEY"] = os.environ["SECRET_KEY"]

# Registro de rutas (Blueprints)
app.register_blueprint(home_bp)
app.register_blueprint(compra_bp)
app.register_blueprint(compras_bp)
app.register_blueprint(peliculas_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(admin_funciones_bp)

app.register_blueprint(auth_bp)

app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"


@app.context_processor
def inyectar_contexto_sesion():
    """Expone la sesión activa a todos los templates (navbar y permisos)."""
    usuario_activo = session.get("usuario")
    return {
        "usuario_activo": usuario_activo,
        "es_admin": bool(
            usuario_activo and usuario_activo.get("rol") == "ADMINISTRADOR"
        ),
    }


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5001))
    debug = os.getenv("FLASK_DEBUG", "True").lower() == "true"
    app.run(host="0.0.0.0", port=port, debug=debug)
