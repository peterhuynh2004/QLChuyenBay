import math

from flask import render_template, request, redirect, url_for, Flask, session
import dao
from appQLChuyenBay import app, login


# from flask_login import login_user, logout_user
app.secret_key = '123456'

@app.route("/")
def index():
    return render_template('index.html')


@app.route("/trangchu")
def trangchudangnhap():
    name = request.args.get('user_name')
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


@app.route("/timkiemchuyenbay")
def timkiemchuyenbay():
    airport = dao.load_airport()
    id_SanBayDen = request.args.get('id_SanBayDen')
    id_SanBayDi = request.args.get('id_SanBayDi')
    ngayDi = request.args.get('ngayDi')
    flight = dao.load_flight(id_SanBayDen=id_SanBayDen, id_SanBayDi=id_SanBayDi, ngayDi=ngayDi)

    return render_template('timkiemchuyenbay.html',
                           airport = airport, flight = flight,
                           id_SanBayDi=id_SanBayDi, id_SanBayDen=id_SanBayDen)



@app.route("/datveonline", methods=['GET', 'POST'])
def datveonline():
    if request.method.__eq__('POST'):
        session['fullName'] = request.form['fullName']
        session['phone'] = request.form['phone']
        session['email'] = request.form['email']
        session['cccd'] = request.form['cccd']
        return redirect(url_for('thongtindatve'))
    return render_template('datveonline.html')
# return render_template('datveonline.html')



@app.route("/thongtindatve", methods=['GET', 'POST'])
def thongtindatve():
    return render_template('thongtindatve.html',
                           fullName=session['fullName'],
                           email=session['email'],
                           cccd=session['cccd'])



@login.user_loader
def load_user(user_id):
    return dao.get_user_by_id(user_id)


if __name__ == '__main__':
    with app.app_context():
        app.run(debug=True)
