import random
from sqlalchemy import Date  # Correct import
from datetime import datetime
from sqlalchemy.orm import relationship
from sqlalchemy import (
    create_engine, Column, Integer, String, DateTime, ForeignKey, Enum, UniqueConstraint, CheckConstraint, Float
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


class TuyenBay(db.Model):
    __tablename__ = 'TuyenBay'

    # Khóa chính tự động tăng
    id_TuyenBay = Column(Integer, primary_key=True, autoincrement=True)

    # Các cột dữ liệu
    tenTuyen = Column(String(255), nullable=False)  # Tên tuyến bay
    id_SanBayDi = Column(Integer, ForeignKey('SanBay.id_SanBay'))
    id_SanBayDen = Column(Integer, ForeignKey('SanBay.id_SanBay'))
    doanhThu = Column(Integer, nullable=True)  # Doanh thu (có thể NULL)
    soLuotBay = Column(Integer, nullable=True)  # Số lượt bay (có thể NULL)
    tyLe = Column(Integer, nullable=True)  # Tỷ lệ (có thể NULL)
    __table_args__ = (
        UniqueConstraint('id_SanBayDi', 'id_SanBayDen', name='UQ_SanBay'),
    )

class ChuyenBay(db.Model):
    __tablename__ = 'ChuyenBay'
    id_ChuyenBay = Column(Integer, primary_key=True, autoincrement=True)
    id_TuyenBay = Column(Integer, ForeignKey('TuyenBay.id_TuyenBay'))
    gio_Bay = Column(DateTime)
    tG_Bay = Column(DateTime)
    GH1 = Column(Integer)
    GH2 = Column(Integer)
    GH1_DD = Column(Integer)
    GH2_DD = Column(Integer)


class VeChuyenBay(db.Model):
    __tablename__ = 'VeChuyenBay'

    # Các cột
    maVe = Column(Integer, primary_key=True, autoincrement=True)  # Mã vé
    giaVe = Column(Integer, nullable=False)  # Giá vé
    maThongTin = Column(Integer, ForeignKey('ThongTinHanhKhach.ID_HanhKhach'), nullable=False)  # Mã thông tin hành khách
    hangVe = Column(Integer, nullable=False)  # Hạng vé (ví dụ: 1: hạng nhất, 2: hạng phổ thông)
    soGhe = Column(Integer, nullable=False)  # Số ghế
    giaHanhLy = Column(Integer, nullable=False)  # Giá hành lý
    thoiGianDat = Column(DateTime, nullable=False, default=datetime.utcnow)  # Thời gian đặt vé
    id_user = Column(Integer, ForeignKey('NguoiDung.ID_User'), nullable=False)  # Khoá ngoại đến bảng User
    id_ChuyenBay = Column(Integer, ForeignKey('ChuyenBay.id_ChuyenBay'),
                          nullable=False)  # Khoá ngoại đến bảng ChuyenBay

    # Quan hệ (relationship) với bảng khác
    user = relationship('NguoiDung', backref='ve_chuyen_bay')
    chuyen_bay = relationship('ChuyenBay', backref='ve_chuyen_bay')

class DiaChi(db.Model):
    __tablename__ = 'DiaChi'
    ID_DC = Column(Integer, primary_key=True, autoincrement=True)
    ChiTiet = Column(String(255), nullable=False)
    TenDuong = Column(String(255), nullable=False)
    QuanHuyen = Column(String(255), nullable=False)
    TinhTP = Column(String(255), nullable=False)


class NguoiDung(db.Model, UserMixin):
    __tablename__ = 'NguoiDung'
    ID_User = Column(Integer, primary_key=True, autoincrement=True)
    HoTen = Column(String(255), nullable=False)
    Email = Column(String(255), nullable=False)
    SDT = Column(Integer, nullable=False)
    TenDangNhap = Column(String(255), nullable=False)
    MatKhau = Column(String(255), nullable=False)
    NgaySinh = Column(DateTime, nullable=True)
    GioiTinh = Column(Enum(GioiTinh), nullable=False)
    DiaChi = Column(Integer, ForeignKey('DiaChi.ID_DC', ondelete='CASCADE'))
    Avt = Column(String(255),
                 default="https://res.cloudinary.com/ddgxultsd/image/upload/v1732958968/tu5tpwmkwetp4ico5liv.png")

    def get_id(self):
        return str(self.ID_User)


class NguoiDung_VaiTro(db.Model):
    __tablename__ = 'NguoiDung_VaiTro'
    ID_ND_VT = Column(Integer, primary_key=True, autoincrement=True)
    ID_User = Column(Integer, ForeignKey('NguoiDung.ID_User', ondelete='CASCADE'))
    ID_VaiTro = Column(Enum(UserRole, native_enum=False), nullable=False)
    __table_args__ = (
        UniqueConstraint('ID_User', 'ID_VaiTro', name='UC_User_VaiTro'),
    )


class NguoiDungQuyDinh(db.Model):
    __tablename__ = 'NguoiDung_QuyDinh'

    # Khóa chính
    ID_ND_QD = Column(Integer, primary_key=True, autoincrement=True)  # Khóa chính tự động tăng
    ID_NguoiDung = Column(Integer, ForeignKey('NguoiDung.ID_User'),
                          nullable=False)  # Khóa ngoại đến bảng NguoiDung (ID_User)
    ID_QuyDinh = Column(Integer, ForeignKey('QuyDinh.ID_QuyDinh'),
                        nullable=False)  # Khóa ngoại đến bảng QuyDinh (ID_QuyDinh)
    thoiGianSua = Column(DateTime, nullable=True)  # Thời gian sửa (có thể NULL)
    lyDoSua = Column(String(255), nullable=True)  # Lý do sửa (có thể NULL)

    # Quan hệ (relationship) với bảng NguoiDung
    nguoi_dung = relationship('NguoiDung', foreign_keys=[ID_NguoiDung])

    # Quan hệ (relationship) với bảng QuyDinh
    quy_dinh = relationship('QuyDinh', foreign_keys=[ID_QuyDinh])

    # Đảm bảo không có sự kết hợp trùng lặp giữa NguoiDung và QuyDinh
    __table_args__ = (
        UniqueConstraint('ID_NguoiDung', 'ID_QuyDinh', 'thoiGianSua', name='unique_nguoidung_quydinh'),
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
    ID_QuyDinhVe = Column(Integer, ForeignKey('QuyDinhVe.ID_QuyDinhVe'), nullable=False)
    ID_QuyDinhSanBay = Column(Integer, ForeignKey('QuyDinhSanBay.ID_QuyDinhSanBay'), nullable=False)
    MoTa = Column(String(500), nullable=True)  # Mô tả quy định


class QuyDinhBanVe(db.Model):
    __tablename__ = 'QuyDinhBanVe'
    ID = Column(Integer, primary_key=True, autoincrement=True)
    ThoiGianBatDauBan = Column(Integer, nullable=False)  # Thời gian bắt đầu bán vé (ngày trước chuyến bay)
    ThoiGianKetThucBan = Column(Integer, nullable=False)  # Thời gian kết thúc bán vé (ngày trước chuyến bay)


class QuyDinhVe(db.Model):
    __tablename__ = 'QuyDinhVe'
    # Khóa chính tự động tăng
    ID_QuyDinhVe = Column(Integer, primary_key=True, autoincrement=True)

    # Các cột dữ liệu
    SoLuongHangGhe1 = Column(Integer, nullable=False)  # Số lượng hạng ghế 1
    SoLuongHangGhe2 = Column(Integer, nullable=False)  # Số lượng hạng ghế 2

    # Các điều kiện kiểm tra (Check Constraints)
    __table_args__ = (
        CheckConstraint('SoLuongHangGhe1 > 0', name='quydinhve_chk_1'),
        CheckConstraint('SoLuongHangGhe2 > 0', name='quydinhve_chk_2'),
    )


class BangGiaVe(db.Model):
    __tablename__ = 'BangGiaVe'
    ID = Column(Integer, primary_key=True, autoincrement=True)
    LoaiHangGhe = Column(Enum('GH1', 'GH2', name='loai_hang_ghe'), nullable=False)
    ThoiGian = Column(Integer, nullable=False)  # Giờ trong ngày (từ 0h đến 23h)
    ID_SanBayDi = Column(Integer, ForeignKey('SanBay.id_SanBay'), nullable=False)  # Khóa ngoại đến bảng SanBay
    ID_SanBayDen = Column(Integer, ForeignKey('SanBay.id_SanBay'), nullable=False)  # Khóa ngoại đến bảng SanBay
    ID_PhuThu = Column(Integer, ForeignKey('PhuThuDacBiet.ID'), nullable=True)  # Khóa ngoại đến bảng PhuThuDacBiet
    ID_QuyDinhVe = Column(Integer, ForeignKey('QuyDinhVe.ID_QuyDinhVe'), nullable=True)
    # Quan hệ (relationship) với bảng SanBay
    san_bay_di = relationship('SanBay', foreign_keys=[ID_SanBayDi])
    san_bay_den = relationship('SanBay', foreign_keys=[ID_SanBayDen])

    # Quan hệ (relationship) với bảng PhuThuDacBiet
    phu_thu = relationship('PhuThuDacBiet', backref='bang_gia_ve')

    # Đảm bảo không có sự kết hợp trùng lặp giữa SanBayDi, SanBayDen và LoaiHangGhe
    __table_args__ = (
        UniqueConstraint('ID_SanBayDi', 'ID_SanBayDen', 'LoaiHangGhe', name='unique_sanbay_hangghe'),
    )


class PhuThuDacBiet(db.Model):
    __tablename__ = 'PhuThuDacBiet'
    ID = Column(Integer, primary_key=True, autoincrement=True)
    TenDipLe = Column(String(255), nullable=False)  # Tên dịp lễ
    NgayBatDau = Column(Date, nullable=False)  # Ngày bắt đầu phụ thu
    NgayKetThuc = Column(Date, nullable=False)  # Ngày kết thúc phụ thu
    PhanTramTang = Column(Float, default=0.0)  # Tăng giá theo phần trăm
    SoTienTang = Column(Float, default=0.0)  # Tăng giá cố định


class QuyDinhSanBay(db.Model):
    __tablename__ = 'QuyDinhSanBay'

    # Khóa chính tự động tăng
    ID_QuyDinhSanBay = Column(Integer, primary_key=True, autoincrement=True)

    # Các cột dữ liệu
    SoLuongSanBay = Column(Integer, nullable=False)  # Số lượng sân bay
    ThoiGianBayToiThieu = Column(Integer, nullable=False)  # Thời gian bay tối thiểu (phút)
    SanBayTrungGianToiDa = Column(Integer, nullable=False)  # Số lượng sân bay trung gian tối đa
    ThoiGianDungToiThieu = Column(Integer, nullable=False)  # Thời gian dừng tối thiểu (phút)
    ThoiGianDungToiDa = Column(Integer, nullable=False)  # Thời gian dừng tối đa (phút)


class ThongTinHanhKhach(db.Model):
    __tablename__ = 'ThongTinHanhKhach'
    ID_HanhKhach = Column(Integer, primary_key=True, autoincrement=True)
    HoTen = Column(String(255), nullable=False)  # Họ và tên
    CCCD = Column(String(20), nullable=False, unique=True)  # Căn cước công dân
    SDT = Column(String(15), nullable=False)  # Số điện thoại
    ID_User = Column(Integer, ForeignKey('NguoiDung.ID_User'), nullable=False)  # Liên kết với người dùng


if __name__ == '__main__':
    with app.app_context():
        # db.create_all()
        # db.drop_all()

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

        # for p in airports:
        #     prod = SanBay(ten_SanBay=p['Sanbay'],
        #                   DiaChi=p['Tinh'])
        #     db.session.add(prod)
        # db.session.commit()
        #
        # tuyenbay_data = [
        #     {
        #         "tenTuyen": "Côn Đảo - Phù Cát",
        #         "id_SanBayDi": 1,
        #         "id_SanBayDen": 2,
        #         "doanhThu": 50000000,
        #         "soLuotBay": 50,
        #         "tyLe": 90
        #     },
        #     {
        #         "tenTuyen": "Côn Đảo - Cà Mau",
        #         "id_SanBayDi": 1,
        #         "id_SanBayDen": 3,
        #         "doanhThu": 20000000,
        #         "soLuotBay": 30,
        #         "tyLe": 85
        #     },
        #     {
        #         "tenTuyen": "Phù Cát - Cần Thơ",
        #         "id_SanBayDi": 2,
        #         "id_SanBayDen": 4,
        #         "doanhThu": 15000000,
        #         "soLuotBay": 20,
        #         "tyLe": 80
        #     },
        #     {
        #         "tenTuyen": "Cà Mau - Buôn Ma Thuộc",
        #         "id_SanBayDi": 3,
        #         "id_SanBayDen": 5,
        #         "doanhThu": 12000000,
        #         "soLuotBay": 15,
        #         "tyLe": 75
        #     },
        #     {
        #         "tenTuyen": "Cần Thơ - Côn Đảo",
        #         "id_SanBayDi": 4,
        #         "id_SanBayDen": 1,
        #         "doanhThu": 25000000,
        #         "soLuotBay": 25,
        #         "tyLe": 88
        #     }
        # ]
        #
        # for t in tuyenbay_data:
        #     tuyenbay = TuyenBay(**t)
        #     db.session.add(tuyenbay)
        #
        # db.session.commit()



        flights = [
            {
                "id_TuyenBay": 1,
                "gio_Bay": "2024-12-22 08:00:00",
                "tG_Bay": "2024-12-22 09:30:00",
                "GH1": 100,
                "GH2": 120,
                "GH1_DD": 50,
                "GH2_DD": 70
            },
            {
                "id_TuyenBay": 2,
                "gio_Bay": "2024-12-22 10:00:00",
                "tG_Bay": "2024-12-22 11:30:00",
                "GH1": 90,
                "GH2": 110,
                "GH1_DD": 40,
                "GH2_DD": 60
            },
            {
                "id_TuyenBay": 3,
                "gio_Bay": "2024-12-22 12:00:00",
                "tG_Bay": "2024-12-22 13:30:00",
                "GH1": 80,
                "GH2": 100,
                "GH1_DD": 30,
                "GH2_DD": 50
            },
            {
                "id_TuyenBay": 4,
                "gio_Bay": "2024-12-22 14:00:00",
                "tG_Bay": "2024-12-22 15:30:00",
                "GH1": 60,
                "GH2": 80,
                "GH1_DD": 20,
                "GH2_DD": 40
            },
            {
                "id_TuyenBay": 5,
                "gio_Bay": "2024-12-22 16:00:00",
                "tG_Bay": "2024-12-22 17:30:00",
                "GH1": 120,
                "GH2": 140,
                "GH1_DD": 60,
                "GH2_DD": 80
            },
            {
                "id_TuyenBay": 2,
                "gio_Bay": "2024-12-22 16:00:00",
                "tG_Bay": "2024-12-22 17:30:00",
                "GH1": 120,
                "GH2": 140,
                "GH1_DD": 60,
                "GH2_DD": 80
            }
        ]

        for f in flights:
            flight = ChuyenBay(**f)
            db.session.add(flight)

        db.session.commit()
