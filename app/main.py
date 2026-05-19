from flask import Flask
from app.api.routes import api_bp

app = Flask(__name__)

# register API routes
app.register_blueprint(api_bp, url_prefix="/api")


@app.route("/")
def home():
    return {
        "status": "ok",
        "service": "marathon-coach-api",
        "mode": "dashboard-ready"
    }


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
