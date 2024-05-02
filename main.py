from flask import Flask, request, render_template

from routes.database_routes import database_routes
from routes.drop_submit_route import drop_submission_route
import os

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')

app.register_blueprint(drop_submission_route, url_prefix='/drop_submit_route')
app.register_blueprint(database_routes, url_prefix="/db")

if __name__ == "__main__":
    from waitress import serve

    print("Starting server...")
    port = os.environ.get('PORT', 8080)
    serve(app, host="0.0.0.0", port=port)
