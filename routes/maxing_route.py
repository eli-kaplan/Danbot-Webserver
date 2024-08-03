from flask import request, render_template, Blueprint, flash, redirect
from werkzeug.utils import secure_filename
import os
from utils import database

maxing_routes = Blueprint("maxing_routes", __name__)

@maxing_routes.route('/', methods=['GET'])
def home():
    return render_template('admin_templates/admin_home.html')