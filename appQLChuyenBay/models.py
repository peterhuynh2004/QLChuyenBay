import random
from sqlalchemy import Date, text  # Correct import
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
    maThongTin = Column(Integer, ForeignKey('ThongTinHanhKhach.ID_HanhKhach'),
                        nullable=False)  # Mã thông tin hành khách
    hangVe = Column(Integer, nullable=False)  # Hạng vé (ví dụ: 1: hạng nhất, 2: hạng phổ thông)
    soGhe = Column(Integer, nullable=False)  # Số ghế
    giaHanhLy = Column(Integer, nullable=False)  # Giá hành lý
    thoiGianDat = Column(DateTime, nullable=False, default=datetime.utcnow)  # Thời gian đặt vé
    id_user = Column(Integer, ForeignKey('NguoiDung.ID_User'), nullable=False)  # Khoá ngoại đến bảng User
    id_ChuyenBay = Column(Integer, ForeignKey('ChuyenBay.id_ChuyenBay'),
                          nullable=False)  # Khoá ngoại đến bảng ChuyenBay


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
        TenQuyDinh = Column(String(255), nullable=False)
        MoTa = Column(String(1000), nullable=True)
        LoaiQuyDinh = Column(String(50), nullable=False)  # Sử dụng để phân biệt loại quy định
        __mapper_args__ = {
            'polymorphic_identity': 'QuyDinh',
            'polymorphic_on': LoaiQuyDinh,
        }

class QuyDinhBanVe(QuyDinh):
        __tablename__ = 'QuyDinhBanVe'
        ID_QuyDinh = Column(Integer, ForeignKey('QuyDinh.ID_QuyDinh'), primary_key=True)
        ThoiGianBatDauBan = Column(Integer, nullable=False)  # Thời gian bắt đầu bán vé (ngày trước chuyến bay)
        ThoiGianKetThucBan = Column(Integer,
                                    nullable=False)  # Thời gian kết thúc bán vé (ngày trước chuyến bay)
        __mapper_args__ = {
            'polymorphic_identity': 'QuyDinhBanVe'
    }

class QuyDinhVe(QuyDinh):
        __tablename__ = 'QuyDinhVe'
        # Khóa chính tự động tăng
        ID_QuyDinh = Column(Integer, ForeignKey('QuyDinh.ID_QuyDinh'), primary_key=True)

        # Các cột dữ liệu
        SoLuongHangGhe1 = Column(Integer, nullable=False)  # Số lượng hạng ghế 1
        SoLuongHangGhe2 = Column(Integer, nullable=False)  # Số lượng hạng ghế 2

        # Các điều kiện kiểm tra (Check Constraints)
        __table_args__ = (
            CheckConstraint('SoLuongHangGhe1 > 0', name='quydinhve_chk_1'),
            CheckConstraint('SoLuongHangGhe2 > 0', name='quydinhve_chk_2'),
        )

        __mapper_args__ = {
            'polymorphic_identity': 'QuyDinhVe'
        }

class BangGiaVe(db.Model):
    __tablename__ = 'BangGiaVe'
    ID = Column(Integer, primary_key=True, autoincrement=True)
    LoaiHangGhe = Column(Enum('GH1', 'GH2', name='loai_hang_ghe'), nullable=False)
    ID_SanBayDi = Column(Integer, ForeignKey('SanBay.id_SanBay'), nullable=False)  # Khóa ngoại đến bảng SanBay
    ID_SanBayDen = Column(Integer, ForeignKey('SanBay.id_SanBay'), nullable=False)  # Khóa ngoại đến bảng SanBay
    ID_PhuThu = Column(Integer, ForeignKey('PhuThuDacBiet.ID'), nullable=True)  # Khóa ngoại đến bảng PhuThuDacBiet
    ID_QuyDinhVe = Column(Integer, ForeignKey('QuyDinhVe.ID_QuyDinh'), nullable=True)  # Khóa ngoại đến bảng QuyDinhVe

    # Quan hệ với bảng SanBay
    san_bay_di = relationship('SanBay', foreign_keys=[ID_SanBayDi])
    san_bay_den = relationship('SanBay', foreign_keys=[ID_SanBayDen])

    # Quan hệ với bảng PhuThuDacBiet
    phu_thu = relationship('PhuThuDacBiet', backref='bang_gia_ve')

    # Quan hệ với bảng QuyDinhVe
    quy_dinh_ve = relationship('QuyDinhVe', backref='bang_gia_ve')

    # Đảm bảo không có sự kết hợp trùng lặp giữa SanBayDi, SanBayDen và LoaiHangGhe
    __table_args__ = (
        UniqueConstraint('ID_SanBayDi', 'ID_SanBayDen', 'LoaiHangGhe', name='unique_sanbay_hangghe'),
    )

class QuyDinhSanBay(QuyDinh):
        __tablename__ = 'QuyDinhSanBay'
        # Khóa chính tự động tăng
        ID_QuyDinh = Column(Integer, ForeignKey('QuyDinh.ID_QuyDinh'), primary_key=True)

        # Các cột dữ liệu
        SoLuongSanBay = Column(Integer, nullable=False)  # Số lượng sân bay
        ThoiGianBayToiThieu = Column(Integer, nullable=False)  # Thời gian bay tối thiểu (phút)
        SanBayTrungGianToiDa = Column(Integer, nullable=False)  # Số lượng sân bay trung gian tối đa
        ThoiGianDungToiThieu = Column(Integer, nullable=False)  # Thời gian dừng tối thiểu (phút)
        ThoiGianDungToiDa = Column(Integer, nullable=False)  # Thời gian dừng tối đa (phút)

        __mapper_args__ = {
            'polymorphic_identity': 'QuyDinhSanBay'
        }


class PhuThuDacBiet(db.Model):
    __tablename__ = 'PhuThuDacBiet'
    ID = Column(Integer, primary_key=True, autoincrement=True)
    TenDipLe = Column(String(255), nullable=False)  # Tên dịp lễ
    NgayBatDau = Column(Date, nullable=False)  # Ngày bắt đầu phụ thu
    NgayKetThuc = Column(Date, nullable=False)  # Ngày kết thúc phụ thu
    PhanTramTang = Column(Float, default=0.0)  # Tăng giá theo phần trăm
    SoTienTang = Column(Float, default=0.0)  # Tăng giá cố định


class ThongTinHanhKhach(db.Model):
    __tablename__ = 'ThongTinHanhKhach'
    ID_HanhKhach = Column(Integer, primary_key=True, autoincrement=True)
    HoTen = Column(String(255), nullable=False)  # Họ và tên
    CCCD = Column(String(20), nullable=False, unique=True)  # Căn cước công dân
    SDT = Column(String(15), nullable=False)  # Số điện thoại
    ID_User = Column(Integer, ForeignKey('NguoiDung.ID_User'), nullable=False)  # Liên kết với người dùng


if __name__ == '__main__':
    with app.app_context():

        # data Bảng giá vé
        banggiave1 = BangGiaVe(LoaiHangGhe='GH1', ID_SanBayDi=1, ID_SanBayDen=11, ID_PhuThu=None,
                               ID_QuyDinhVe=None)
        banggiave2 = BangGiaVe(LoaiHangGhe='GH2', ID_SanBayDi=2, ID_SanBayDen=10, ID_PhuThu=None,
                               ID_QuyDinhVe=None)
        db.session.add_all([banggiave1, banggiave2])
        db.session.commit()

        # data Vé Chuyến bay
        # vechuyenbay1 = VeChuyenBay(giaVe=2000000, maThongTin=1, hangVe=2, soGhe=5, giaHanhLy=500000,
        #                            thoiGianDat=datetime.utcnow(), id_user=1, id_ChuyenBay=1)
        # vechuyenbay2 = VeChuyenBay(giaVe=2500000, maThongTin=2, hangVe=1, soGhe=10, giaHanhLy=600000,
        #                            thoiGianDat=datetime.utcnow(), id_user=2, id_ChuyenBay=2)
        # db.session.add_all([vechuyenbay1, vechuyenbay2])
        # db.session.commit()

        # data ThongTinHanhKhach
        # thongtinhk1 = ThongTinHanhKhach(HoTen="Nguyễn Văn A", CCCD="123456789012", SDT="123456789", ID_User=2)
        # thongtinhk2 = ThongTinHanhKhach(HoTen="Trần Thị B", CCCD="987654321098", SDT="987654321", ID_User=2)
        # db.session.add_all([thongtinhk1, thongtinhk2])
        # db.session.commit()

        # data NguoiDung_VaiTro
        # nguoidung_vaitro1 = NguoiDung_VaiTro(ID_User=1, ID_VaiTro=UserRole.NhanVien)
        # nguoidung_vaitro2 = NguoiDung_VaiTro(ID_User=2, ID_VaiTro=UserRole.NguoiQuanTri)
        # db.session.add_all([nguoidung_vaitro1, nguoidung_vaitro2])
        # db.session.commit()

        # data Người Dùng
        # nguoidung1 = NguoiDung(HoTen="Nguyễn Văn A", Email="nguyenvana@example.com", SDT=123456789,
        #                        TenDangNhap="nguyenvana", MatKhau="password123", GioiTinh="Nam", DiaChi=1)
        # nguoidung2 = NguoiDung(HoTen="Trần Thị B", Email="tranthib@example.com", SDT=987654321, TenDangNhap="tranthib",
        #                        MatKhau="password456", GioiTinh="Nữ", DiaChi=2)
        # db.session.add_all([nguoidung1, nguoidung2])
        # db.session.commit()

        # địa chỉ
        # diachi1 = DiaChi(ChiTiet="Số 1, Đường A", TenDuong="Đường A", QuanHuyen="Quận 1",
        #                  TinhTP="Thành phố Hồ Chí Minh")
        # diachi2 = DiaChi(ChiTiet="Số 2, Đường B", TenDuong="Đường B", QuanHuyen="Quận 2", TinhTP="Hà Nội")
        # db.session.add_all([diachi1, diachi2])
        # db.session.commit()

        # data chuyen bay
        # chuyenbay1 = ChuyenBay(id_TuyenBay=1, gio_Bay=datetime(2024, 12, 15, 9, 0),
        #                        tG_Bay=datetime(2024, 12, 15, 9, 30), GH1=50, GH2=100, GH1_DD=10, GH2_DD=20)
        # chuyenbay2 = ChuyenBay(id_TuyenBay=2, gio_Bay=datetime(2024, 12, 16, 12, 0),
        #                        tG_Bay=datetime(2024, 12, 16, 12, 30), GH1=40, GH2=90, GH1_DD=5, GH2_DD=15)
        # chuyenbay3 = ChuyenBay(id_TuyenBay=3, gio_Bay=datetime(2024, 12, 17, 7, 30),
        #                        tG_Bay=datetime(2024, 12, 17, 8, 0), GH1=60, GH2=110, GH1_DD=12, GH2_DD=18)
        # db.session.add_all([chuyenbay1, chuyenbay2, chuyenbay3])
        # db.session.commit()

        # themdatatuyenbay
        # tuyenbay1 = TuyenBay(tenTuyen="Côn Đảo - Tân Sơn Nhất", id_SanBayDi=1, id_SanBayDen=11, doanhThu=50000000,
        #                      soLuotBay=150, tyLe=90)
        # tuyenbay2 = TuyenBay(tenTuyen="Phù Cát - Nội Bài", id_SanBayDi=2, id_SanBayDen=10, doanhThu=30000000,
        #                      soLuotBay=100, tyLe=85)
        # tuyenbay3 = TuyenBay(tenTuyen="Cà Mau - Đà Nẵng", id_SanBayDi=3, id_SanBayDen=6, doanhThu=45000000,
        #                      soLuotBay=120, tyLe=75)
        # tuyenbay4 = TuyenBay(tenTuyen="Cần Thơ - Phú Quốc", id_SanBayDi=4, id_SanBayDen=14, doanhThu=35000000,
        #                      soLuotBay=80, tyLe=80)
        # db.session.add_all([tuyenbay1, tuyenbay2, tuyenbay3, tuyenbay4])
        # db.session.commit()

        # data sân bay
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
