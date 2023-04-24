
from functools import wraps
from flask import url_for, request, redirect, session


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):

        if "user" not in session:
            return redirect(url_for('auth', redirect=request.url))
        return f(*args, **kwargs)
    return decorated_function
