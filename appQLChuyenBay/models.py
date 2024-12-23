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

# Khai báo Enum Python cho vai trò và giới tính
class UserRole(RoleEnum):
    NhanVien = 1
    NguoiQuanTri = 2
    KhachHang = 3
    NguoiKiemDuyet = 4

class GioiTinh(GioiTinhEnum):
    Nam = 1
    Nu = 2

# ----------------------------------------------------------------------
# MODELS
# ----------------------------------------------------------------------

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
    # Dùng Enum của SQLAlchemy, tham chiếu UserRole
    ID_VaiTro = Column(SqlAlchemyEnum(UserRole, native_enum=False), nullable=False)

    __table_args__ = (
        UniqueConstraint('ID_User', 'ID_VaiTro', name='UC_User_VaiTro'),
    )


class NguoiDungQuyDinh(db.Model):
    __tablename__ = 'NguoiDung_QuyDinh'
    ID_ND_QD = Column(Integer, primary_key=True, autoincrement=True)
    ID_NguoiDung = Column(Integer, ForeignKey('NguoiDung.ID_User'), nullable=False)
    ID_QuyDinh = Column(Integer, ForeignKey('QuyDinh.ID_QuyDinh'), nullable=False)
    thoiGianSua = Column(DateTime, nullable=True)
    lyDoSua = Column(String(255), nullable=True)

    nguoi_dung = relationship('NguoiDung', foreign_keys=[ID_NguoiDung])
    quy_dinh = relationship('QuyDinh', foreign_keys=[ID_QuyDinh])

    __table_args__ = (
        UniqueConstraint('ID_NguoiDung', 'ID_QuyDinh', 'thoiGianSua', name='unique_nguoidung_quydinh'),
    )


class BaoCao(db.Model):
    __tablename__ = 'BaoCao'
    id_BaoCao = Column(Integer, primary_key=True, autoincrement=True)
    thoiGian = Column(DateTime, nullable=False)
    thang = Column(DateTime, nullable=False)
    tongDoanhThu = Column(Integer)
    id_TuyenBay = Column(Integer, ForeignKey('TuyenBay.id_TuyenBay'))
    id_NguoiDung = Column(Integer, ForeignKey('NguoiDung.ID_User'))
    __table_args__ = (
        UniqueConstraint('thang', 'id_TuyenBay', name='UC_Thang'),
    )


class TuyenBay(db.Model):
    __tablename__ = 'TuyenBay'
    id_TuyenBay = Column(Integer, primary_key=True, autoincrement=True)
    tenTuyen = Column(String(255), nullable=False)
    id_SanBayDi = Column(Integer, ForeignKey('SanBay.id_SanBay'))
    id_SanBayDen = Column(Integer, ForeignKey('SanBay.id_SanBay'))
    doanhThu = Column(Integer, nullable=True)
    soLuotBay = Column(Integer, nullable=True)
    tyLe = Column(Integer, nullable=True)

    __table_args__ = (
        UniqueConstraint('id_SanBayDi', 'id_SanBayDen', name='UQ_SanBay'),
    )


class ChuyenBay(db.Model):
    __tablename__ = 'ChuyenBay'
    id_ChuyenBay = Column(Integer, primary_key=True, autoincrement=True)
    id_TuyenBay = Column(Integer, ForeignKey('TuyenBay.id_TuyenBay'))
    gio_Bay = Column(DateTime)
    tG_Bay = Column(Integer)
    GH1 = Column(Integer)
    GH2 = Column(Integer)
    GH1_DD = Column(Integer)
    GH2_DD = Column(Integer)
    ghes_dadat = Column(String(255))  # Thêm thuộc tính để lưu các ghế đã đặt

    def them_ghes_dadat(self, list_seats):
        # Cập nhật danh sách ghế đã đặt (danh sách ghế được truyền vào là danh sách các ghế như 'F1', 'E10', ...)
        self.ghes_dadat = ','.join(list_seats)

    def lay_ghes_dadat(self):
        # Lấy danh sách ghế đã đặt dưới dạng một danh sách (ví dụ: ['F1', 'E10'])
        return self.ghes_dadat.split(',')

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


class SanBay(db.Model):
    __tablename__ = 'SanBay'
    id_SanBay = Column(Integer, primary_key=True, autoincrement=True)
    ten_SanBay = Column(String(255), nullable=False, unique=True)
    DiaChi = Column(String(255), nullable=True)


class SBayTrungGian(db.Model):
    __tablename__ = 'SBayTrungGian'
    ID = Column(Integer, primary_key=True, autoincrement=True)
    ID_ChuyenBay = Column(Integer, ForeignKey('ChuyenBay.id_ChuyenBay'), nullable=False)
    ID_SanBay = Column(Integer, ForeignKey('SanBay.id_SanBay'), nullable=False)
    ThoiGianDung = Column(Integer, nullable=False)
    GhiChu = Column(String(255), nullable=True)

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
        ThoiGianKetThucBan = Column(Float,
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
    Gia_Ve = Column(Integer,nullable=False)
    # Quan hệ với bảng SanBay
    san_bay_di = relationship('SanBay', foreign_keys=[ID_SanBayDi])
    san_bay_den = relationship('SanBay', foreign_keys=[ID_SanBayDen])

    # Quan hệ với bảng PhuThuDacBiet
    phu_thu = relationship('PhuThuDacBiet', backref='bang_gia_ve')

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
    TenDipLe = Column(String(255), nullable=False)
    NgayBatDau = Column(Date, nullable=False)
    NgayKetThuc = Column(Date, nullable=False)
    PhanTramTang = Column(Float, default=0.0)
    SoTienTang = Column(Float, default=0.0)


class ThongTinHanhKhach(db.Model):
    __tablename__ = 'ThongTinHanhKhach'
    ID_HanhKhach = Column(Integer, primary_key=True, autoincrement=True)
    HoTen = Column(String(255), nullable=False)
    CCCD = Column(String(20), nullable=False, unique=True)
    SDT = Column(String(15), nullable=False)
    ID_User = Column(Integer, ForeignKey('NguoiDung.ID_User'), nullable=False)



if __name__ == '__main__':
    with app.app_context():

        # Tạo dữ liệu cho QuyDinhBanVe
        new_quy_dinh_ban_ve = QuyDinhBanVe(
            TenQuyDinh="Quy định bán vé",
            MoTa="Quy định về thời gian bắt đầu và kết thúc bán vé trước ngày bay.",
            LoaiQuyDinh="QuyDinhBanVe",  # Phân biệt loại quy định
            ThoiGianBatDauBan=30,  # Thời gian bắt đầu bán vé trước 30 ngày
            ThoiGianKetThucBan=3  # Thời gian kết thúc bán vé trước 3 ngày
        )

        # Thêm dữ liệu vào cơ sở dữ liệu
        db.session.add(new_quy_dinh_ban_ve)
        db.session.commit()

        print("Đã tạo dữ liệu cho QuyDinhBanVe.")
        # # Tạo dữ liệu cho quy định sân bay
        # new_quy_dinh_san_bay = QuyDinhSanBay(
        #     TenQuyDinh="Quy định về sân bay",
        #     MoTa="Quy định liên quan đến số lượng inhSanBaysân bay, thời gian bay và dừng tại sân bay trung gian.",
        #     LoaiQuyDinh="QuyDinhSanBay",  # Phân biệt loại quy định
        #     SoLuongSanBay=10,  # Số lượng sân bay
        #     ThoiGianBayToiThieu=30,  # Thời gian bay tối thiểu (phút)
        #     SanBayTrungGianToiDa=2,  # Số lượng sân bay trung gian tối đa
        #     ThoiGianDungToiThieu=20,  # Thời gian dừng tối thiểu (phút)
        #     ThoiGianDungToiDa=30,  # Thời gian dừng tối đa (phút)
        # )
        #
        # # Thêm dữ liệu vào cơ sở dữ liệu
        # db.session.add(new_quy_dinh_san_bay)
        # db.session.commit()
        #
        # print("Đã tạo dữ liệu cho quy định sân bay.")

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

        #db.create_all()
        # db.drop_all()


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
        # db.session.commit()


        # flights = [
        #     {
        #         "id_TuyenBay": 1,
        #         "gio_Bay": "2024-12-22 08:00:00",
        #         "tG_Bay": "2024-12-22 09:30:00",
        #         "GH1": 100,
        #         "GH2": 120,
        #         "GH1_DD": 50,
        #         "GH2_DD": 70
        #     },
        #     {
        #         "id_TuyenBay": 2,
        #         "gio_Bay": "2024-12-22 10:00:00",
        #         "tG_Bay": "2024-12-22 11:30:00",
        #         "GH1": 90,
        #         "GH2": 110,
        #         "GH1_DD": 40,
        #         "GH2_DD": 60
        #     },
        #     {
        #         "id_TuyenBay": 3,
        #         "gio_Bay": "2024-12-22 12:00:00",
        #         "tG_Bay": "2024-12-22 13:30:00",
        #         "GH1": 80,
        #         "GH2": 100,
        #         "GH1_DD": 30,
        #         "GH2_DD": 50
        #     },
        #     {
        #         "id_TuyenBay": 4,
        #         "gio_Bay": "2024-12-22 14:00:00",
        #         "tG_Bay": "2024-12-22 15:30:00",
        #         "GH1": 60,
        #         "GH2": 80,
        #         "GH1_DD": 20,
        #         "GH2_DD": 40
        #     },
        #     {
        #         "id_TuyenBay": 5,
        #         "gio_Bay": "2024-12-22 16:00:00",
        #         "tG_Bay": "2024-12-22 17:30:00",
        #         "GH1": 120,
        #         "GH2": 140,
        #         "GH1_DD": 60,
        #         "GH2_DD": 80
        #     },
        #     {
        #         "id_TuyenBay": 2,
        #         "gio_Bay": "2024-12-22 16:00:00",
        #         "tG_Bay": "2024-12-22 17:30:00",
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
        # db.session.commit()

        # # địa chỉ
        # diachi1 = DiaChi(ChiTiet="Số 1, Đường A", TenDuong="Đường A", QuanHuyen="Quận 1",
        #                  TinhTP="Thành phố Hồ Chí Minh")
        # diachi2 = DiaChi(ChiTiet="Số 2, Đường B", TenDuong="Đường B", QuanHuyen="Quận 2", TinhTP="Hà Nội")
        # db.session.add_all([diachi1, diachi2])
        # db.session.commit()
        #
        # # data Người Dùng
        # nguoidung1 = NguoiDung(HoTen="Nguyễn Văn A", Email="nguyenvana@example.com", SDT=123456789,
        #                        TenDangNhap="nguyenvana", MatKhau="password123", GioiTinh="Nam", DiaChi=1)
        # nguoidung2 = NguoiDung(HoTen="Trần Thị B", Email="tranthib@example.com", SDT=987654321, TenDangNhap="tranthib",
        #                        MatKhau="password456", GioiTinh="Nữ", DiaChi=2)
        # db.session.add_all([nguoidung1, nguoidung2])
        # db.session.commit()
        #
        # # data Bảng giá vé
        # banggiave1 = BangGiaVe(LoaiHangGhe='GH1', ID_SanBayDi=1, ID_SanBayDen=11, ID_PhuThu=None,
        #                        ID_QuyDinhVe=None)
        # banggiave2 = BangGiaVe(LoaiHangGhe='GH2', ID_SanBayDi=2, ID_SanBayDen=10, ID_PhuThu=None,
        #                        ID_QuyDinhVe=None)
        # db.session.add_all([banggiave1, banggiave2])
        # db.session.commit()

        # data NguoiDung_VaiTro
        # nguoidung_vaitro1 = NguoiDung_VaiTro(ID_User=1, ID_VaiTro=UserRole.NhanVien)
        # nguoidung_vaitro2 = NguoiDung_VaiTro(ID_User=2, ID_VaiTro=UserRole.NguoiQuanTri)
        # db.session.add_all([nguoidung_vaitro1, nguoidung_vaitro2])
        # db.session.commit()

        # data ThongTinHanhKhach
        # thongtinhk1 = ThongTinHanhKhach(HoTen="Nguyễn Văn A", CCCD="123456789012", SDT="123456789", ID_User=2)
        # thongtinhk2 = ThongTinHanhKhach(HoTen="Trần Thị B", CCCD="987654321098", SDT="987654321", ID_User=2)
        # db.session.add_all([thongtinhk1, thongtinhk2])
        # db.session.commit()

        # # data Vé Chuyến bay
        # vechuyenbay1 = VeChuyenBay(giaVe=2000000, maThongTin=1, hangVe=2, soGhe=5, giaHanhLy=500000,
        #                            thoiGianDat=datetime.utcnow(), id_user=1, id_ChuyenBay=1)
        # vechuyenbay2 = VeChuyenBay(giaVe=2500000, maThongTin=2, hangVe=1, soGhe=10, giaHanhLy=600000,
        #                            thoiGianDat=datetime.utcnow(), id_user=2, id_ChuyenBay=2)
        # db.session.add_all([vechuyenbay1, vechuyenbay2])
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
