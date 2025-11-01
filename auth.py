import streamlit as st
import streamlit_authenticator as stauth
from database import session, User
import bcrypt

def register_user(username, password):
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    new_user = User(username=username, password=hashed.decode())
    session.add(new_user)
    session.commit()

def get_authenticator():
    users = session.query(User).all()
    credentials = {
        "usernames": {u.username: {"name": u.username, "password": u.password} for u in users}
    }
    authenticator = stauth.Authenticate(
        credentials,
        "csv_explorer",
        "abcdef",
        cookie_expiry_days=0
    )
    return authenticator
