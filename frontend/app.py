import os
from dotenv import load_dotenv
from flask import Flask

from routes.home_routes import home_bp

load_dotenv()

app = Flask(__name__)

# Configuración básica de la aplicación
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "cine-paradiso-secret-dev")

# Registro de rutas (Blueprints)
app.register_blueprint(home_bp)


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5001))
    debug = os.getenv("FLASK_DEBUG", "True").lower() == "true"
    app.run(host="0.0.0.0", port=port, debug=debug)
