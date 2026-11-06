import os
from dotenv import load_dotenv
from flask import Flask, session

from routes.dashboard_routes import dashboard_bp
from routes.home_routes import home_bp
from routes.peliculas_routes import peliculas_bp
from routes.compra_routes import compra_bp

load_dotenv()

app = Flask(__name__)

# Configuración básica de la aplicación
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "cine-paradiso-secret-dev")

# Registro de rutas (Blueprints)
app.register_blueprint(home_bp)
app.register_blueprint(peliculas_bp)
app.register_blueprint(dashboard_bp)


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
