import os
from attrs.converters import to_bool

def allow_db_reset() -> bool:
    """Determines if DB reset is allowed

    Env: ALLOW_DB_RESET (defaults to false)

    Returns:
        bool: Allow database reset?
    """
    return to_bool(os.getenv("ALLOW_DB_RESET", "FALSE"))

def allow_view_board(is_admin: bool) -> bool:
    """Determines if board is visible

    Envs: 
        - BOARD_VISIBLE (defaults to true)
        - ADMINS_CAN_VIEW_BOARD (defaults to true)
    
    Args:
        is_admin (bool): Whether current user is an admin

    Returns:
        bool: Should the board be visible?
    """
    board_visible = to_bool(os.getenv("BOARD_VISIBLE", "TRUE"))
    admins_can_view_board = to_bool(os.getenv("ADMINS_CAN_VIEW_BOARD", "TRUE"))
    return board_visible or (is_admin and admins_can_view_board)

def enable_tracking() -> bool:
    """Determines if tracking is enabled

    Env: TRACKING (defaults to true)

    Returns:
        bool: Should dink tracking be enabled?
    """
    return to_bool(os.getenv("TRACKING", "TRUE"))

def get_server_ip() -> str:
    """Determines the server's domain name ("IP" for compatibility)

    Env: SERVER_IP

    Raises:
        Exception: If env is unset

    Returns:
        str: Server domain name/IP
    """
    server_ip = os.getenv("SERVER_IP", None)
    if not server_ip:
        raise Exception("SERVER_IP must be specified in envs")
    return server_ip

def get_flask_secret_key() -> str:
    """Determines the configured Flask secret key

    Env: FLASK_SECRET_KEY

    Returns:
        str: Flask secret key
    """
    return os.getenv("FLASK_SECRET_KEY", "development secret")

def get_server_port() -> int:
    """Determines the configured server port

    Returns:
        int: Port
    """
    return int(os.getenv("PORT", 80))

def get_discord_bot_token() -> str:
    """Determines configured discord bot token

    Env: DISCORD_BOT_TOKEN

    Returns:
        str: Discord bot token
    """
    return os.getenv("DISCORD_BOT_TOKEN", "unset")