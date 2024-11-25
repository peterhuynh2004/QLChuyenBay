import math

from flask import render_template, request, redirect
import dao
from appQLChuyenBay import app
# from flask_login import login_user, logout_user


@app.route("/")
def index():
    return render_template('index.html')


if __name__ == '__main__':
    with app.app_context():
        app.run(debug=True)
