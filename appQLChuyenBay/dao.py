import sqlite3

from models import NguoiDung, SanBay, NguoiDung_VaiTro, UserRole
from appQLChuyenBay import app, db
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


def get_san_bay():
    # Truy vấn tất cả các sân bay
    return SanBay.query.all()


def check_email_exists(email):
    Session = sessionmaker(bind=db.engine)
    session = Session()
    try:
        # Tìm người dùng với email đã cho
        user = session.query(NguoiDung).filter_by(Email=email).first()
        return user is not None  # Trả về True nếu email tồn tại
    finally:
        session.close()


# Tạo cache enum cho việc đối chiếu
role_map = {role.value: name for name, role in UserRole.__members__.items()}


def get_all_user_roles(user_id):
    user_roles = db.session.query(NguoiDung_VaiTro.ID_VaiTro).filter_by(ID_User=user_id).all()
    role_ids = [role.ID_VaiTro for role in user_roles]
    return [role_map.get(role_id) for role_id in role_ids if role_id in role_map]
