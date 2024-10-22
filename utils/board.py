import teampassword
import config
import db_entities
import database
import os
import random
from flask import render_template

def is_board_globally_visible(current_user: object) -> bool:
    """Determines if the board info is globally visible 

    Args:
        current_user (object): current user data

    Returns:
        bool: Whether the board should be shown
    """
    return config.allow_view_board(current_user.is_authenticated and current_user.is_admin)

def is_team_authenticated(provided_pw: str, team_name: str) -> bool:
    """Determines if the provided password is valid for a particular team ID

    Args:
        provided_pw (str): Password from URL
        team_name (str): Team name

    Returns:
        bool: Whether this user is authorized to see this team's board
    """
    try:
        team_entry = db_entities.Team(database.get_team_by_name(team_name)) 

        return teampassword.calculate_team_password(team_entry.team_webhook) == provided_pw
    except:
        return False

def select_random_file(directory):
    # Get a list of all files in the directory
    files = os.listdir(directory)

    # Filter out directories, only keep files
    files = [f for f in files if os.path.isfile(os.path.join(directory, f))]

    # Select a random file
    random_file = random.choice(files)

    return random_file

def hidden_board():

    random_file = select_random_file("static/hidden_board_memes")
    random_file = "hidden_board_memes/" + random_file
    return render_template('board_templates/hidden_board.html', PageTitle="Board is hidden :)", FileName=random_file)