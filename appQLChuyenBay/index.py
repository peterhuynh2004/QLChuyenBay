import json
import math
from datetime import timedelta, datetime
from flask import render_template, request, redirect, url_for, jsonify, flash, current_app
import dao
from appQLChuyenBay import app, login, mail
from flask_mail import Message
import random
from flask import session
from flask_login import login_user, logout_user



@app.route("/", methods=['get', 'post'])
def index():
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

@app.route('/ban_ve/<int:id_chuyen_bay>', methods=['get', 'post'])
def banve(id_chuyen_bay):
    session['id_chuyen_bay'] = id_chuyen_bay
    flight = dao.get_flight_by_id(id_chuyen_bay)
    print(flight['GH1'])
    print(flight['GH2'])
    print(flight['ghe_dadat'])
    first_class_seats = flight['GH1']  # Số ghế hạng nhất
    economy_class_seats = flight['GH2']  # Số ghế hạng phổ thông
    return render_template(
        'ban_ve.html',
        first_class_seats=first_class_seats,
        economy_class_seats=economy_class_seats,
        flight=flight  # Truyền flight vào template
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
    SanBayDi = request.args.get('NoiDi').split('(')[0].strip()
    SanBayDen = request.args.get('NoiDen').split('(')[0].strip()
    ngayDi = request.args.get('Date')
    veNguoiLon = request.args.get('SLNguoiLon')
    veTreEm = request.args.get('SLTreEm')
    veEmBe = request.args.get('SLEmBe')
    session['veNguoiLon'] = veNguoiLon
    session['veTreEm'] = veTreEm
    session['veEmBe'] = veEmBe
    id_SanBayDi = dao.get_id_San_Bay(SanBayDi)
    id_SanBayDen = dao.get_id_san_bay(SanBayDen)
    flight = dao.load_flight(noiDi=id_SanBayDi, noiDen=id_SanBayDen, ngayDi=ngayDi)
    return render_template('timkiemchuyenbay.html',
                           airport=airport, flight=flight,
                           SanBayDi=SanBayDi, SanBayDen=SanBayDen, id_SanBayDi=id_SanBayDi, id_SanBayDen=id_SanBayDen, ngayDi=ngayDi)


@app.route("/datveonline", methods=['GET', 'POST'])
def datveonline():
    if request.method == 'POST':
        # Lấy giá trị từ form
        hangGhe = request.form.get('hangGhe')
        fullNameNguoiLon = []
        phone = []
        email = []
        ngaySinhNguoiLon = []
        cccd = []
        for i in range(int(session['veNguoiLon'])):
            fullNameNguoiLon.append(request.form.getlist(f'fullNameNguoiLon[{i}]'))
            phone.append(request.form.getlist(f'phone[{i}]'))
            email.append(request.form.getlist(f'email[{i}]'))
            ngaySinhNguoiLon.append(request.form.getlist(f'ngaySinhNguoiLon[{i}]'))
            cccd.append(request.form.getlist(f'cccd[{i}]'))
        # Lưu thông tin vào session
        session['hangGhe'] = hangGhe
        session['fullNameNguoiLon'] = fullNameNguoiLon
        session['phone'] = phone
        session['email'] = email
        session['cccd'] = cccd
        session['ngaySinhNguoiLon'] = ngaySinhNguoiLon
        # Chuyển sang bước tiếp theo
        return redirect('thongtindatve')
    return render_template('datveonline.html', veNguoiLon=int(session['veNguoiLon']), veTreEm=int(session['veTreEm']), veEmBe=int(session['veEmBe']))


@app.route("/thongtindatve", methods=['GET', 'POST'])
def thongtindatve():
    fullNameNguoiLon = session.get('fullNameNguoiLon',[])
    return render_template('thongtindatve.html',
                           veNguoiLon=int(session['veNguoiLon']),
                           veTreEm=int(session['veTreEm']),
                           veEmBe=int(session['veEmBe']),
                           fullNameNguoiLon=fullNameNguoiLon)

@app.route('/thanhtoanbangtienmat', methods=['GET'])
def thanh_toan_bang_tien_mat():
    try:
        # Lấy dữ liệu từ URL
        seats_info = request.args.get('seats')
        total_cost = request.args.get('totalCost')
        passengerinfo = request.args.get('passengerInfo')

        # Kiểm tra và chuyển đổi dữ liệu JSON
        seats_info = json.loads(seats_info) if seats_info else []
        passengerinfo = json.loads(passengerinfo) if passengerinfo else []

        # Kết hợp thông tin ghế và hành khách nếu số lượng khớp nhau
        if len(seats_info) != len(passengerinfo):
            raise ValueError("Số lượng ghế và hành khách không khớp.")

        combined_info = [
            {
                "seat": seat,
                "passenger": passenger
            }
            for seat, passenger in zip(seats_info, passengerinfo)
        ]

        # Trả về template với thông tin đã xử lý
        return render_template(
            'thanhtoantienmat.html',
            total_cost=total_cost,
            combined_info=combined_info
        )
    except (ValueError, json.JSONDecodeError) as e:
        # Xử lý lỗi và hiển thị thông báo
        return f"Lỗi trong quá trình xử lý dữ liệu: {str(e)}", 400

@app.route('/confirm-payment', methods=['POST'])
def confirm_payment():
    if request.method == 'POST':
        try:
            # Nhận chuỗi JSON từ form
            seats_info = request.form['seats-info']
            #id_user = session.get('id_user')   # Lấy id_user từ session
            id_user =2
            # Lưu thông tin thanh toán vào cơ sở dữ liệu

            # Lưu thông tin vé
            if dao.save_ticket_info( id_user, seats_info):
                flash('Thanh toán thành công! Thông tin vé đã được lưu.')
                session['seats_info'] = seats_info  # Lưu dữ liệu vào session
            else:
                flash('Lỗi khi lưu thông tin vé.')

        except Exception as e:
            print("Lỗi trong quá trình xử lý: ", e)
            flash('Đã xảy ra lỗi trong quá trình thanh toán.')

        return redirect(url_for('thanhtoanthanhcong'))  # Trang xác nhận thanh toán thành công

@app.route('/thanhtoanthanhcong', methods=['GET', 'POST'])
def thanhtoanthanhcong():
    seats_info = session.get('seats_info')  # Lấy dữ liệu từ session
    id_ChuyenBay = session.get('id_chuyen_bay')
    if seats_info:
        if isinstance(seats_info, str):
            # Nếu dữ liệu là chuỗi, thử chuyển thành dictionary (nếu có thể)
            # Lưu ý: nếu chuỗi này không phải JSON hợp lệ, bạn cần xử lý trường hợp này.
            seats_info = eval(
                seats_info)  # Chỉ nên dùng eval khi bạn chắc chắn dữ liệu hợp lệ (cẩn thận với lỗi bảo mật)
        tenTuyen = dao.get_TuyenBay(id_ChuyenBay);
        return render_template('thanhtoanthanhcong.html', seats_info=seats_info, tenTuyen=tenTuyen)
    else:
        flash('Không tìm thấy thông tin vé.')
        return redirect(url_for('index'))  # Chuyển hướng về trang chủ hoặc trang khác nếu không có dữ liệu
    return render_template('thanhtoanthanhcong.html')

if __name__ == '__main__':
    with app.app_context():
        app.run(port=8000, debug=True)
