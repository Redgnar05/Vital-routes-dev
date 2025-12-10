from flask import session

def usuario_logueado():
    return "user_id" in session

def requerir_login():
    return usuario_logueado()
