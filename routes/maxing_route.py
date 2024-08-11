from collections import defaultdict

from flask import request, render_template, Blueprint, flash, redirect, session
from werkzeug.utils import secure_filename
import os
from utils import database

maxing_routes = Blueprint("maxing_routes", __name__)

@maxing_routes.route('/', methods=['GET'])
def home():
    session_data = defaultdict(lambda: defaultdict(lambda: defaultdict(dict)))
    session_data['1'] = 3

    session['data'] = dict(session_data)
    return render_template('maxing_templates/maxing_home.html', sd=session['data']['1'])

