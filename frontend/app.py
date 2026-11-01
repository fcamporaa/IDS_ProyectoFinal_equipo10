import os
from dotenv import load_dotenv
from flask import Flask

from routes.home_routes import home_bp
from routes.compras_routes import compras_bp

load_dotenv()

app = Flask(__name__)

# Configuración básica de la aplicación
if len(os.getenv("SECRET_KEY", "")) < 32:
    raise RuntimeError("Configurá SECRET_KEY (mínimo 32 caracteres) en el frontend.")
app.config["SECRET_KEY"] = os.environ["SECRET_KEY"]

# Registro de rutas (Blueprints)
app.register_blueprint(home_bp)
app.register_blueprint(compras_bp)
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5001))
    debug = os.getenv("FLASK_DEBUG", "True").lower() == "true"
    app.run(host="0.0.0.0", port=port, debug=debug)
