from discord.ext import commands
from flask import Flask, request, render_template

from routes.user_routes import user_routes
from routes.database_routes import database_routes
from routes.dink import drop_submission_route
import os
import threading
import discord
import bot

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'development secret')


@app.route('/')
def home():
    return render_template('home.html')


app.register_blueprint(drop_submission_route, url_prefix='/dink')
app.register_blueprint(database_routes, url_prefix="/db")
app.register_blueprint(user_routes, url_prefix="/user")


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
