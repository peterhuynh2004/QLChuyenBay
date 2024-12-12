from models import NguoiDung
from appQLChuyenBay import  db
import hashlib
import cloudinary.uploader
from sqlalchemy.orm import sessionmaker


def auth_user(username, password):
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())

    return NguoiDung.query.filter(NguoiDung.TenDangNhap.__eq__(username.strip()),
                                  NguoiDung.MatKhau.__eq__(password)).first()


def add_user(name, email, password, avatar):
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())

    u = NguoiDung(HoTen=name, TenDangNhap=email, Email=email, MatKhau=password,
                  Avt='u.avatar')

    if avatar:
        res = cloudinary.uploader.upload(avatar)
        u.avatar = res.get('secure_url')

    db.session.add(u)
    db.session.commit()


def get_user_by_id(user_id):
    return NguoiDung.query.get(user_id)  # Trả về None nếu không tìm thấy


def check_email_exists(email):
    Session = sessionmaker(bind=db.engine)
    session = Session()
    try:
        # Tìm người dùng với email đã cho
        user = session.query(NguoiDung).filter_by(Email=email).first()
        return user is not None  # Trả về True nếu email tồn tại
    finally:
        session.close()
