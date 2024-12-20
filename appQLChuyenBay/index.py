import math
from datetime import timedelta, datetime
from flask import render_template, request, redirect, url_for, jsonify
import dao
from appQLChuyenBay import app, login, mail
from flask_mail import Message
import random
from flask import session
from flask_login import login_user, logout_user


@app.route("/", methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        noiDi = request.form.get('idNoiDi')
        noiDen = request.form.get('idNoiDen')
        ngayDi = request.form.get('Date')
        return redirect(url_for('timkiemchuyenbay', noiDi = noiDi, noiDen=noiDen, ngayDi=ngayDi ))

    # Lấy danh sách chuyến bay sắp cất cánh
    flights = dao.get_upcoming_flights()

    flight_info = []
    for flight in flights:
        # Lấy tên tuyến bay từ ID_TuyenBay
        route = dao.get_route_name_by_id(flight.id_TuyenBay)

        if route:
            # Lưu thông tin chuyến bay vào danh sách flight_info
            flight_info.append({
                "hành_trình": route.tenTuyen,
                "thời_gian": flight.gio_Bay.strftime('%d-%m-%Y %H:%M'),  # Giả sử gioBay là kiểu datetime
            })

    return render_template('index.html',flights=flight_info)

@app.route('/api/get_sanbay', methods=['GET'])
def get_sanbay():
    try:
        sanbay_list = dao.get_san_bay()

        # Trả về dữ liệu dưới dạng JSON
        return jsonify([{
            'ten_SanBay': sb.ten_SanBay +' ('+ sb.DiaChi +')'
        } for sb in sanbay_list])
    except Exception as e:
        app.logger.error(f"Error fetching SanBay: {str(e)}")
        return jsonify({"error": "Internal Server Error"}), 500

@app.route("/trangchu")
def trangchudangnhap():
    name = request.args.get('user_name')
    return render_template('index.html')


@app.route("/login", methods=['get', 'post'])
def login_process():
    if request.method.__eq__('POST'):
        username = request.form.get('email')
        password = request.form.get('password')

        u = dao.auth_user(username=username, password=password)
        if u:
            login_user(u)

            #Lấy id người dùng
            user_id = u.id# Kiểm tra vai trò của người dùng
            user_role = dao.get_user_role(user_id)
            from appQLChuyenBay import models
            if user_role == models.UserRole.NhanVien or user_role == models.UserRole.NguoiKiemDuyet or user_role == models.UserRole.NguoiQuanTri:  # So sánh với Enum  # Nếu vai trò là "Nhân Viên"
                return redirect('/nhan_vien')

            # Nếu không phải nhân viên, chuyển về trang chủ
            return redirect('/')

    return render_template('login.html')


@app.route("/logout")
def logout_process():
    logout_user()
    return redirect('/login')


@app.route('/register', methods=['get', 'post'])
def register_process():
    err_msg = ''
    if request.method.__eq__('POST'):
        email = request.form.get('email')
        password = request.form.get('password')
        confirm = request.form.get('confirm')

        # Kiểm tra nếu email đã tồn tại
        if dao.check_email_exists(email):
            err_msg = 'Email đã tồn tại!'
        elif not password.__eq__(confirm):
            err_msg = 'Mật khẩu không khớp!'
        else:
            # Tạo OTP ngẫu nhiên
            otp = random.randint(100000, 999999)
            session['otp'] = otp  # Lưu OTP vào session
            session['user_data'] = request.form  # Lưu tạm dữ liệu người dùng

            # Gửi email OTP
            msg = Message('Xác thực OTP', recipients=[email])
            msg.body = f'Chào bạn, mã OTP để hoàn tất đăng ký của bạn là: {otp}'
            mail.send(msg)

            return redirect('/xacthucotp')

    return render_template('register.html', err_msg=err_msg)


@app.route('/xacthucotp', methods=['get', 'post'])
def verify_otp():
    err_msg = ''
    if request.method.__eq__('POST'):
        entered_otp = request.form.get('otp')
        if str(session.get('otp')) == entered_otp:  # So sánh OTP nhập vào
            # Lấy dữ liệu người dùng từ session và thêm vào DB
            data = session.get('user_data')
            del data['confirm']
            data.pop('dangky', None)  # Loại bỏ trường 'dangky' nếu tồn tại
            avatar = request.files.get('avatar')
            dao.add_user(avatar=avatar, **data)
            session.pop('otp', None)  # Xóa OTP khỏi session
            session.pop('user_data', None)  # Xóa dữ liệu người dùng khỏi session

            return redirect('/login')
        else:
            err_msg = 'Mã OTP không chính xác!'

    return render_template('xacthucotp.html', err_msg=err_msg)

# @app.route("/ket_qua_tim_kiem")
# def huongdandatcho():
#     return render_template('huong_dan_dat_cho.html')

@app.route("/huong_dan_dat_cho")
def huongdandatcho():
    return render_template('huong_dan_dat_cho.html')

@app.route("/chuc_nang")
def chucnang():
    return render_template('chuc_nang.html')

@app.route("/lap_lich_chuyen_bay")
def laplichchuyenbay():
    return render_template('lap_lich_chuyen_bay.html')

from dao import get_filtered_flights

@app.route("/danhsachchuyenbay")
def danhsachchuyenbay():
    # Lấy tham số từ yêu cầu GET
    san_bay_di = request.args.get('SanBayDi', None)
    san_bay_den = request.args.get('SanBayDen', None)
    thoi_gian = request.args.get('ThoiGian', None)
    gh1 = request.args.get('GH1', None)
    gh2 = request.args.get('GH2', None)

    # Gọi hàm từ dao để lấy danh sách chuyến bay
    page = request.args.get('page', 1, type=int)
    flights = get_filtered_flights(san_bay_di, san_bay_den, thoi_gian, gh1, gh2, page=page, per_page=10)

    flight_info = []
    for flight in flights.items:
        route = dao.get_route_name_by_id(flight.id_TuyenBay)
        sân_bay_trung_gian = dao.get_route_sanbaytrunggian_by_id(flight.id_ChuyenBay)

        if route:
            flight_info.append({
                "id": flight.id_ChuyenBay,
                "hành_trình": route.tenTuyen,
                "thời_gian": flight.gio_Bay.strftime('%d-%m-%Y %H:%M'),
                "ghế_hạng_1_còn_trống": flight.GH1_DD,
                "ghế_hạng_2_còn_trống": flight.GH2_DD,
                "GH1": flight.GH1,
                "GH2": flight.GH2,
                "sân_bay_trung_gian": ', '.join(sân_bay_trung_gian),
            })

    return render_template('danhsachchuyenbay.html', flights=flight_info, pagination=flights)

@app.route("/api/danhsachchuyenbay", methods=["POST"])
def api_danhsachchuyenbay():
    data = request.json
    noi_di = data.get('SanBayDi', None)
    noi_den = data.get('SanBayDen', None)
    thoi_gian = data.get('ThoiGian', None)
    gh1 = data.get('GH1', None)
    gh2 = data.get('GH2', None)

    # Gọi hàm DAO để lọc chuyến bay
    flights = dao.get_filtered_flights(noi_di, noi_den, thoi_gian, gh1, gh2, page=1, per_page=10)

    # Chuyển dữ liệu chuyến bay thành JSON
    result = []
    for flight in flights.items:
        route = dao.get_route_name_by_id(flight.id_TuyenBay)
        sân_bay_trung_gian = dao.get_route_sanbaytrunggian_by_id(flight.id)

        if route:
            result.append({
                "id": flight.id,
                "hành_trình": route.tenTuyen,
                "thời_gian": flight.gio_Bay.strftime('%d-%m-%Y %H:%M'),
                "ghế_hạng_1_còn_trống": flight.GH1_con,
                "ghế_hạng_2_còn_trống": flight.GH2_con,
                "GH1": flight.GH1,
                "GH2": flight.GH2,
                "sân_bay_trung_gian": ', '.join(sân_bay_trung_gian),
            })

    return jsonify(result)

@app.route("/ban_ve", methods=['get', 'post'])
def banve():
    first_class_seats = 8  # Số ghế hạng nhất
    economy_class_seats = 12  # Số ghế hạng phổ thông
    return render_template(
        'ban_ve.html',
        first_class_seats=first_class_seats,
        economy_class_seats=economy_class_seats
    )

@app.route("/nhan_vien")
def nhanvien():
    return render_template('nhan_vien.html')

@app.route("/kiem_tra_ma")
def kiemtrama():
    return render_template('kiem_tra_ma.html')


@login.user_loader
def load_user(user_id):
    try:
        # Chuyển user_id sang dạng số nguyên nếu cần
        user_id = int(user_id)

        # Lấy thông tin người dùng từ DAO
        user = dao.get_user_by_id(user_id)

        # Kiểm tra xem user có tồn tại hay không
        if user:
            return user  # Trả về đối tượng người dùng
        return None  # Không tìm thấy người dùng
    except (ValueError, TypeError):
        # Xử lý trường hợp user_id không hợp lệ
        print("Invalid user_id:", user_id)
        return None
    except Exception as e:
        # Xử lý các lỗi khác
        print("Error loading user:", e)
        return None


@app.route("/timkiemchuyenbay")
def timkiemchuyenbay():
    airport = dao.get_san_bay()
    id_SanBayDi = request.args.get('noiDi')
    id_SanBayDen = request.args.get('noiDen')
    ngayDi = request.args.get('ngayDi')
    flight = dao.load_flight(noiDi=id_SanBayDi, noiDen=id_SanBayDen, ngayDi=ngayDi)
    if len(flight) > 0:
        tuyenBay = dao.load_TuyenBay(flight[0].id_TuyenBay)
    else:
        tuyenBay = 0
    return render_template('timkiemchuyenbay.html',airport=airport, flight=flight,
                           id_SanBayDi=id_SanBayDi, id_SanBayDen=id_SanBayDen, tuyenBay = tuyenBay)


@app.route("/datveonline", methods=['GET', 'POST'])
def datveonline():
    if request.method == 'POST':
        # Lấy giá trị từ form
        hangGhe = request.form.get('hangGhe')
        fullName = request.form.get('fullName')
        phone = request.form.get('phone')
        email = request.form.get('email')
        cccd = request.form.get('cccd')

        # Lưu thông tin vào session
        session['hangGhe'] = hangGhe
        session['fullName'] = fullName
        session['phone'] = phone
        session['email'] = email
        session['cccd'] = cccd

        # Chuyển sang bước tiếp theo
        return redirect('thongtindatve')
    # Lấy thông tin từ session nếu đã được lưu
    hangGhe = session.get('hangGhe', '')
    fullName = session.get('fullName', '')
    phone = session.get('phone', '')
    email = session.get('email', '')
    cccd = session.get('cccd', '')
    return render_template('datveonline.html', hangGhe=hangGhe, fullName=fullName, phone=phone, email=email, cccd=cccd)


@app.route("/thongtindatve", methods=['GET', 'POST'])
def thongtindatve():
    return render_template('thongtindatve.html',
                           fullName=session['fullName'],
                           email=session['email'],
                           cccd=session['cccd'])


if __name__ == '__main__':
    with app.app_context():
        app.run(port=8000, debug=True)
