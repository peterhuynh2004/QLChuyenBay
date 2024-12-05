import random
from sqlalchemy.orm import relationship
from sqlalchemy import (
    create_engine, Column, Integer, String, DateTime, ForeignKey, Enum, UniqueConstraint, CheckConstraint
)
from appQLChuyenBay import db, app
from enum import Enum as RoleEnum
from enum import Enum as GioiTinhEnum
import hashlib
from flask_login import UserMixin
from sqlalchemy import DateTime


class UserRole(RoleEnum):
    NhanVien = 1
    NguoiQuanTri = 2
    KhachHang = 3
    NguoiKiemDuyet = 4


class GioiTinh(GioiTinhEnum):
    Nam = 1
    Nu = 2


class TuyenBay(db.Model):
    __tablename__ = 'TuyenBay'
    id_TuyenBay = Column(Integer, primary_key=True, autoincrement=True)
    tenTuyen = Column(String(50), nullable=False)
    doanhThu = Column(Integer)
    soLuotBay = Column(Integer)
    tiLe = Column(Integer)
    baocao = relationship('BaoCao', backref='TuyenBay', lazy=True)


class BaoCao(db.Model):
    __tablename__ = 'BaoCao'
    id_BaoCao = Column(Integer, primary_key=True, autoincrement=True)
    thoiGian = Column(DateTime, nullable=False)
    thang = Column(DateTime, nullable=False)
    tongDoanhThu = Column(Integer)
    id_TuyenBay = Column(Integer, ForeignKey('TuyenBay.id_TuyenBay'))
    id_NguoiDung = Column(Integer, ForeignKey('NguoiDung.ID_User'))
    __table_args__ = (
        UniqueConstraint('thang', 'id_BaoCao', 'id_TuyenBay', name='UC_Thang'),
    )




class ChuyenBay(db.Model):
    __tablename__ = 'ChuyenBay'
    id_ChuyenBay = Column(Integer, primary_key=True, autoincrement=True)
    id_SanBayDi = Column(Integer, ForeignKey('SanBay.id_SanBay'))
    id_SanBayDen = Column(Integer, ForeignKey('SanBay.id_SanBay'))
    id_TuyenBay = Column(Integer, ForeignKey('TuyenBay.id_TuyenBay'))
    gio_Bay = Column(DateTime)
    tG_Bay = Column(DateTime)
    GH1 = Column(Integer)
    GH2 = Column(Integer)
    GH1_DD = Column(Integer)
    GH2_DD = Column(Integer)
    __table_args__ = (
        UniqueConstraint('id_SanBayDi', 'id_SanBayDen', name='UQ_SanBay'),
    )


class DiaChi(db.Model):
    __tablename__ = 'DiaChi'
    ID_DC = Column(Integer, primary_key=True, autoincrement=True)
    ChiTiet = Column(String(255), nullable=False)
    TenDuong = Column(String(255), nullable=False)
    QuanHuyen = Column(String(255), nullable=False)
    TinhTP = Column(String(255), nullable=False)


class User(db.Model, UserMixin):
    __tablename__ = 'NguoiDung'
    ID_User = Column(Integer, primary_key=True, autoincrement=True)
    HoTen = Column(String(255), nullable=False)
    Email = Column(String(255), nullable=False)
    SDT = Column(Integer, primary_key=False)
    TenDangNhap = Column(String(255), nullable=False)
    MatKhau = Column(String(255), nullable=False)
    NgaySinh = Column(DateTime, nullable=True)
    GioiTinh = Column(Enum(GioiTinh), nullable=False)
    DiaChi = Column(Integer, ForeignKey('DiaChi.ID_DC', ondelete='CASCADE'))


class NguoiDung_VaiTro(db.Model):
    __tablename__ = 'NguoiDung_VaiTro'
    ID_ND_VT = Column(Integer, primary_key=True, autoincrement=True)
    ID_User = Column(Integer, ForeignKey('NguoiDung.ID_User', ondelete='CASCADE'))
    ID_VaiTro = Column(Enum(UserRole, native_enum=False), nullable=False)
    __table_args__ = (
        UniqueConstraint('ID_User', 'ID_VaiTro', name='UC_User_VaiTro'),
    )


class SanBay(db.Model):
    __tablename__ = 'SanBay'
    id_SanBay = Column(Integer, primary_key=True, autoincrement=True)
    ten_SanBay = Column(String(255), nullable=False, unique=True)
    DiaChi = Column(String(255), nullable=True)  # Thông tin địa chỉ Sanbay


class SBayTrungGian(db.Model):
    __tablename__ = 'SBayTrungGian'
    ID = Column(Integer, primary_key=True, autoincrement=True)
    ID_ChuyenBay = Column(Integer, ForeignKey('ChuyenBay.id_ChuyenBay'), nullable=False)
    ID_SanBay = Column(Integer, ForeignKey('SanBay.id_SanBay'), nullable=False)
    ThoiGianDung = Column(Integer, nullable=False)  # Thời gian dừng (phút)
    GhiChu = Column(String(255), nullable=True)  # Ghi chú


class QuyDinh(db.Model):
    __tablename__ = 'QuyDinh'
    ID_QuyDinh = Column(Integer, primary_key=True, autoincrement=True)
    TenQuyDinh = Column(String(255), nullable=False, unique=True)
    ID_QuyDinhBanVe = Column(Integer, ForeignKey('QuyDinhBanVe.ID'), nullable=False)
    ID_QuyDinhVe = Column(Integer, ForeignKey('QuyDinhVe.ID'), nullable=False)
    ID_QuyDinhSanBay = Column(Integer, ForeignKey('QuyDinhSanBay.ID'), nullable=False)
    MoTa = Column(String(500), nullable=True)  # Mô tả quy định


class QuyDinhBanVe(db.Model):
    __tablename__ = 'QuyDinhBanVe'
    ID = Column(Integer, primary_key=True, autoincrement=True)
    ThoiGianBatDauBan = Column(Integer, nullable=False)  # Thời gian bắt đầu bán vé (ngày trước chuyến bay)
    ThoiGianKetThucBan = Column(Integer, nullable=False)  # Thời gian kết thúc bán vé (ngày trước chuyến bay)


class QuyDinhVe(db.Model):
    __tablename__ = 'QuyDinhVe'
    ID = Column(Integer, primary_key=True, autoincrement=True)
    SoLuongGheToiDa = Column(Integer, nullable=False)  # Số lượng ghế tối đa trên chuyến bay
    BangGia = Column(String(500), nullable=True)  # Dữ liệu bảng giá (JSON hoặc chuỗi mô tả)


class QuyDinhSanBay(db.Model):
    __tablename__ = 'QuyDinhSanBay'
    ID = Column(Integer, primary_key=True, autoincrement=True)
    SoLuongSanBayToiDa = Column(Integer, nullable=False)  # Số lượng Sanbay tối đa
    ThoiGianBayToiThieu = Column(Integer, nullable=False)  # Thời gian bay tối thiểu (phút)


class ThongTinHanhKhach(db.Model):
    __tablename__ = 'ThongTinHanhKhach'
    ID_HanhKhach = Column(Integer, primary_key=True, autoincrement=True)
    HoTen = Column(String(255), nullable=False)  # Họ và tên
    CCCD = Column(String(20), nullable=False, unique=True)  # Căn cước công dân
    SDT = Column(String(15), nullable=False)  # Số điện thoại
    ID_User = Column(Integer, ForeignKey('NguoiDung.ID_User'), nullable=False)  # Liên kết với người dùng


# if __name__ == '__main__':
#     with app.app_context():
        # db.create_all()
        # airports = [
        #     {"Sanbay": "Côn Đảo", "Tinh": "Bà Rịa – Vũng Tàu"},
        #     {"Sanbay": "Phù Cát", "Tinh": "Bình Định"},
        #     {"Sanbay": "Cà Mau", "Tinh": "Cà Mau"},
        #     {"Sanbay": "Cần Thơ", "Tinh": "Cần Thơ"},
        #     {"Sanbay": "Buôn Ma Thuột", "Tinh": "Đắk Lắk"},
        #     {"Sanbay": "Đà Nẵng", "Tinh": "Đà Nẵng"},
        #     {"Sanbay": "Điện Biên Phủ", "Tinh": "Điện Biên"},
        #     {"Sanbay": "Pleiku", "Tinh": "Gia Lai"},
        #     {"Sanbay": "Cát Bi", "Tinh": "Hải Phòng"},
        #     {"Sanbay": "Nội Bài", "Tinh": "Hà Nội"},
        #     {"Sanbay": "Tân Sơn Nhất", "Tinh": "Thành phố Hồ Chí Minh"},
        #     {"Sanbay": "Cam Ranh", "Tinh": "Khánh Hòa"},
        #     {"Sanbay": "Rạch Giá", "Tinh": "Kiên Giang"},
        #     {"Sanbay": "Phú Quốc", "Tinh": "Kiên Giang"},
        #     {"Sanbay": "Liên Khương", "Tinh": "Lâm Đồng"},
        #     {"Sanbay": "Vinh", "Tinh": "Nghệ An"},
        #     {"Sanbay": "Tuy Hòa", "Tinh": "Phú Yên"},
        #     {"Sanbay": "Đồng Hới", "Tinh": "Quảng Bình"},
        #     {"Sanbay": "Chu Lai", "Tinh": "Quảng Nam"},
        #     {"Sanbay": "Phú Bài", "Tinh": "Thừa Thiên Huế"},
        #     {"Sanbay": "Thọ Xuân", "Tinh": "Thanh Hóa"},
        #     {"Sanbay": "Vân Đồn", "Tinh": "Quảng Ninh"},
        # ]
        #
        # for p in airports:
        #     prod = SanBay(ten_SanBay=p['Sanbay'],
        #                   DiaChi=p['Tinh'])
        #     db.session.add(prod)
        # db.session.commit()
        #
        # flights = [
        #     {   "id_SanBayDi": 1,
        #         "id_SanBayDen": 2,
        #         # "id_TuyenBay": 1,
        #         "gio_Bay": "2024-12-05 08:00:00",
        #         "tG_Bay": "2024-12-05 09:30:00",
        #         "GH1": 100,
        #         "GH2": 120,
        #         "GH1_DD": 50,
        #         "GH2_DD": 70
        #     },
        #     {   "id_SanBayDi": 2,
        #         "id_SanBayDen": 3,
        #         # "id_TuyenBay": 2,
        #         "gio_Bay": "2024-12-05 10:00:00",
        #         "tG_Bay": "2024-12-05 11:30:00",
        #         "GH1": 90,
        #         "GH2": 110,
        #         "GH1_DD": 40,
        #         "GH2_DD": 60
        #     },
        #     {   "id_SanBayDi": 3,
        #         "id_SanBayDen": 4,
        #         # "id_TuyenBay": 3,
        #         "gio_Bay": "2024-12-05 12:00:00",
        #         "tG_Bay": "2024-12-05 13:30:00",
        #         "GH1": 80,
        #         "GH2": 100,
        #         "GH1_DD": 30,
        #         "GH2_DD": 50
        #     },
        #     {   "id_SanBayDi": 6,
        #         "id_SanBayDen": 7,
        #         # "id_TuyenBay": 4,
        #         "gio_Bay": "2024-12-05 14:00:00",
        #         "tG_Bay": "2024-12-05 15:30:00",
        #         "GH1": 60,
        #         "GH2": 80,
        #         "GH1_DD": 20,
        #         "GH2_DD": 40
        #     },
        #     {   "id_SanBayDi": 10,
        #         "id_SanBayDen": 12,
        #         # "id_TuyenBay": 5,
        #         "gio_Bay": "2024-12-05 16:00:00",
        #         "tG_Bay": "2024-12-05 17:30:00",
        #         "GH1": 120,
        #         "GH2": 140,
        #         "GH1_DD": 60,
        #         "GH2_DD": 80
        #     }
        # ]
        #
        # for f in flights:
        #     flight = ChuyenBay(**f)
        #     db.session.add(flight)
        #
        # db.session.commit()


