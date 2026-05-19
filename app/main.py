from flask import Flask, render_template
from app.api.routes import api_bp

app = Flask(__name__)

app.register_blueprint(api_bp, url_prefix="/api")


@app.route("/")
def dashboard():
    return render_template("dashboard.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
