from discord.ext import commands
from flask import Flask, request, render_template, make_response

from routes.tutorial_routes import tutorial_routes
from routes.user_routes import user_routes
from routes.admin_routes import admin_routes
from routes.dink import drop_submission_route
from routes.maxing_route import maxing_routes
from routes.board_routes import board_routes
import os
import threading
import discord
import bot

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'development secret')


@app.route('/')
def home():
    return render_template('home.html')

@app.route('/getcookie')
def get_cookie(key):
    value = request.cookies.get(key)
    return value

@app.route('/setcookie')
def set_cookie(key, value):
    resp = make_response("Cookie is set")
    resp.set_cookie(key, value, max_age=60*60*24*30,
                    samesite='Strict')
    return resp

app.register_blueprint(drop_submission_route, url_prefix='/dink')
app.register_blueprint(admin_routes, url_prefix="/admin")
app.register_blueprint(user_routes, url_prefix="/user")
app.register_blueprint(board_routes, url_prefix='/board')
app.register_blueprint(tutorial_routes, url_prefix="/tutorial")
app.register_blueprint(maxing_routes, url_prefix="/maxing")

def start_bot():
    bot.run()


def create_app():
    return app


if __name__ == "__main__":
    from waitress import serve

    print("Starting bot....")
    bot_thread = threading.Thread(target=start_bot)
    bot_thread.start()
    print("Bot started!")

    print("Starting server...")
    port = os.environ.get('PORT', 80)
    print("Server started!")
    serve(app, host="0.0.0.0", port=port)
