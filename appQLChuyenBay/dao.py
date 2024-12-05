from models import User, SanBay, ChuyenBay
from appQLChuyenBay import app, db
import hashlib
import cloudinary.uploader



def auth_user(username, password):
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())

    return User.query.filter(User.username.__eq__(username.strip()),
                             User.password.__eq__(password)).first()


def get_user_by_id(id):
    return User.query.get(id)


def load_airport():
    query = SanBay.query
    return query.all()


def load_flight(id_SanBayDen=None, id_SanBayDi=None, ngayDi=None):
    query = ChuyenBay.query

    if id_SanBayDen and id_SanBayDi and ngayDi:
        query = query.filter(ChuyenBay.id_SanBayDen == id_SanBayDen and ChuyenBay.id_SanBayDi == id_SanBayDi and ChuyenBay.gio_Bay.date() == ngayDi)
    return query.all()
