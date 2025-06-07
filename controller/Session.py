# controller/Session.py

# This would be set during login
current_user = {
    "staff_id": None,
    "staff_username": None,
    "staff_firstname": None,
    "staff_lastname": None
}

def set_user(user_data: dict):
    global current_user
    current_user.update(user_data)

def get_user():
    return current_user
