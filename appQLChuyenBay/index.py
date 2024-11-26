import math

from flask import render_template, request, redirect
import dao
from appQLChuyenBay import app


# from flask_login import login_user, logout_user


@app.route("/")
def index():
    return render_template('index.html')


@app.route("/login")
def dangnhap():
    return render_template('login.html')

@app.route("/huong_dan_dat_cho")
def huongdandatcho():
    return render_template('huong_dan_dat_cho.html')


@app.route("/kiem_tra_ma")
def kiemtrama():
    return render_template('kiem_tra_ma.html')


if __name__ == '__main__':
    with app.app_context():
        app.run(debug=True)
