import sqlite3
from datetime import datetime
from flask_sqlalchemy import pagination
from sqlalchemy import func

from models import NguoiDung, SanBay, NguoiDung_VaiTro, UserRole, ChuyenBay, TuyenBay, SBayTrungGian
from appQLChuyenBay import app, db
import hashlib
import cloudinary.uploader
from sqlalchemy.orm import sessionmaker
from sqlalchemy import and_


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


def load_flight(noiDi=None, noiDen=None, ngayDi=None):
    query = ChuyenBay.query
    if noiDi and noiDen and ngayDi:
        query = query.join(TuyenBay).filter(
            and_(
                TuyenBay.id_SanBayDi == noiDi,
                TuyenBay.id_SanBayDen == noiDen,
                db.func.date(ChuyenBay.gio_Bay) == ngayDi  # Sử dụng `db.func.date` để lấy phần ngày
            )
        )
    return query.all()


def load_TuyenBay(flight=None):
    query = TuyenBay.query
    if flight:
        query = query.filter(TuyenBay.id_TuyenBay == flight)
    return query.all()


def load_flights_paginated(page=1, per_page=10):
    query = ChuyenBay.query
    return query.paginate(page=page, per_page=per_page, error_out=False)

def get_route_sanbaytrunggian_by_id(route_id):
    route = db.session.query(SBayTrungGian.ID_SanBay).filter(SBayTrungGian.ID_ChuyenBay == route_id).all()

    for r in route:
        rou = db.session.query(SanBay.ten_SanBay).filter(SanBay.id_SanBay == r).first()
    return route

# Hàm lấy các chuyến bay sắp cất cánh
def get_upcoming_flights():
    # Truy vấn các chuyến bay có thời gian bay lớn hơn thời gian hiện tại
    flights = db.session.query(ChuyenBay).filter(ChuyenBay.gio_Bay > datetime.now()).order_by(ChuyenBay.gio_Bay).limit(
        10).all()
    return flights


# Hàm lấy tên tuyến bay từ id_TuyenBay
def get_route_name_by_id(route_id):
    # Truy vấn tên tuyến bay từ bảng TuyenBay
    route = db.session.query(TuyenBay.tenTuyen).filter(TuyenBay.id_TuyenBay == route_id).first()
    return route


def get_SanBayTrungGian_name_by_id(id_ChuyenBay):
    results = (
        db.session.query(SanBay.ten_SanBay)
        .join(SBayTrungGian, SBayTrungGian.ID_SanBay == SanBay.id_SanBay)
        .filter(SBayTrungGian.ID_SanBay == id_ChuyenBay)
        .all()
    )
    # Trả về danh sách tên sân bay
    return [result.ten_SanBay for result in results]

def get_filtered_flights(san_bay_di=None, san_bay_den=None, thoi_gian=None, gh1=None, gh2=None, page=1, per_page=10):
    query = ChuyenBay.query.join(TuyenBay)

    if san_bay_di:
        query = query.filter(TuyenBay.id_SanBayDi == san_bay_di)
    if san_bay_den:
        query = query.filter(TuyenBay.id_SanBayDen == san_bay_den)
    if thoi_gian:
        query = query.filter(db.func.date(ChuyenBay.gio_Bay) == thoi_gian)  # Sử dụng db.func.date để lọc theo ngày
    if gh1:
        query = query.filter(ChuyenBay.GH1 >= int(gh1))
    if gh2:
        query = query.filter(ChuyenBay.GH2 >= int(gh2))

    # Trả về kết quả với phân trang
    return query.paginate(page=page, per_page=per_page)