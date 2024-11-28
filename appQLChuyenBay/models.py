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
    ID_ChuyenBay = Column(Integer, ForeignKey('ChuyenBay.ID_ChuyenBay'), nullable=False)
    ID_SanBay = Column(Integer, ForeignKey('SanBay.ID_SanBay'), nullable=False)
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


if __name__ == '__main__':
    with app.app_context():
        airports = [
            {"Sanbay": "Côn Đảo", "Tinh": "Bà Rịa – Vũng Tàu"},
            {"Sanbay": "Phù Cát", "Tinh": "Bình Định"},
            {"Sanbay": "Cà Mau", "Tinh": "Cà Mau"},
            {"Sanbay": "Cần Thơ", "Tinh": "Cần Thơ"},
            {"Sanbay": "Buôn Ma Thuột", "Tinh": "Đắk Lắk"},
            {"Sanbay": "Đà Nẵng", "Tinh": "Đà Nẵng"},
            {"Sanbay": "Điện Biên Phủ", "Tinh": "Điện Biên"},
            {"Sanbay": "Pleiku", "Tinh": "Gia Lai"},
            {"Sanbay": "Cát Bi", "Tinh": "Hải Phòng"},
            {"Sanbay": "Nội Bài", "Tinh": "Hà Nội"},
            {"Sanbay": "Tân Sơn Nhất", "Tinh": "Thành phố Hồ Chí Minh"},
            {"Sanbay": "Cam Ranh", "Tinh": "Khánh Hòa"},
            {"Sanbay": "Rạch Giá", "Tinh": "Kiên Giang"},
            {"Sanbay": "Phú Quốc", "Tinh": "Kiên Giang"},
            {"Sanbay": "Liên Khương", "Tinh": "Lâm Đồng"},
            {"Sanbay": "Vinh", "Tinh": "Nghệ An"},
            {"Sanbay": "Tuy Hòa", "Tinh": "Phú Yên"},
            {"Sanbay": "Đồng Hới", "Tinh": "Quảng Bình"},
            {"Sanbay": "Chu Lai", "Tinh": "Quảng Nam"},
            {"Sanbay": "Phú Bài", "Tinh": "Thừa Thiên Huế"},
            {"Sanbay": "Thọ Xuân", "Tinh": "Thanh Hóa"},
            {"Sanbay": "Vân Đồn", "Tinh": "Quảng Ninh"},
        ]

        for p in airports:
            prod = SanBay(ten_SanBay=p['Sanbay'],
                          DiaChi=p['Tinh'])
            db.session.add(prod)
        db.session.commit()
