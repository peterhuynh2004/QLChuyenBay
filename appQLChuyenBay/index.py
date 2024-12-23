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


@app.route("/")
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

    return render_template('index.html', flights=flight_info)


@app.route('/api/danhsachchuyenbay', methods=['POST'])
def api_danhsachchuyenbay():
    data = request.get_json()  # Nhận dữ liệu JSON từ yêu cầu POST
    print(data)  # Debug dữ liệu

    # Lấy id sân bay đi và đến
    id_NoiDi = dao.get_id_san_bay(data.get('SanBayDi'))
    id_NoiDen = dao.get_id_san_bay(data.get('SanBayDen'))

    if data and id_NoiDi is not None and id_NoiDen is not None:
        # Gán giá trị cho các biến
        san_bay_di = id_NoiDi
        san_bay_den = id_NoiDen
        thoi_gian = data.get('ThoiGian')
        gh1 = int(data.get('GH1', 0))  # Đảm bảo gh1 là số nguyên
        gh2 = int(data.get('GH2', 0))  # Đảm bảo gh2 là số nguyên
        print(f"Searching flights with: {san_bay_di}, {san_bay_den}, {thoi_gian}, {gh1}, {gh2}")  # Debug

        # Lấy danh sách chuyến bay
        flights = dao.get_flights(san_bay_di, san_bay_den, thoi_gian, gh1, gh2)

        # Trả về kết quả dưới dạng JSON
        return jsonify(flights), 200
    else:
        return jsonify({"error": "Invalid input or unknown airport"}), 400


@app.route('/api/get_tuyenbay', methods=['GET'])
def api_get_tuyenbay():
    try:
        # Lấy danh sách tất cả các tuyến bay từ bảng TuyenBay
        tuyen_bay_list = dao.get_all_tuyen_bay()  # Giả sử dao có phương thức này
        # Trả về danh sách dưới dạng JSON
        return jsonify([{
            'tenTuyen': tb.tenTuyen,
            'id_SanBayDi': tb.id_SanBayDi,
            'id_SanBayDen': tb.id_SanBayDen,
            'id_TuyenBay': tb.id_TuyenBay
        } for tb in tuyen_bay_list])
    except Exception as e:
        app.logger.error(f"Error fetching SanBay: {str(e)}")
        return jsonify({"error": "Internal Server Error"}), 500


@app.route('/api/get_sanbay', methods=['GET'])
def get_sanbay():
    try:
        sanbay_list = dao.get_san_bay()

        # Trả về dữ liệu dưới dạng JSON
        return jsonify([{
            'ten_SanBay': sb.ten_SanBay + ' (' + sb.DiaChi + ')'
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

            # Lấy id người dùng
            user_id = u.ID_User  # Kiểm tra vai trò của người dùng
            user_role = dao.get_user_role(user_id)
            checkrole = dao.checkrole(user_role)
            if checkrole:
                return redirect('/nhan_vien')

            # Nếu không phải nhân viên, chuyển về trang chủ
            return redirect('/')

    return render_template('login.html')


@app.route("/logout")
def logout_process():
    logout_user()
    session["user_role"] = ""
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
    user_id = session.get('_user_id')  # Kiểm tra vai trò của người dùng
    user_role = dao.get_user_role(user_id)
    user_role_change = dao.change_user_role(user_role)
    if 'NhanVien' in user_role_change:
        return render_template('chuc_nang.html', user_role_change=user_role_change)
    else:
        return render_template('/')


@app.route("/lap_lich_chuyen_bay", endpoint="lap_lich_chuyen_bay", methods=["GET", "POST"])
def laplichchuyenbay():
    if request.method == "POST":
        flight_date = request.form['flight_date']
        print(flight_date)
        TuyenBay = request.form['TuyenBay']
        # thoigianbay
        flight_duration = int(request.form['flight_duration'])
        first_class_seats = int(request.form['first_class_seats'])
        economy_class_seats = int(request.form['economy_class_seats'])
        id_TuyenBay = dao.get_id_TuyenBay(TuyenBay)
        flight = dao.save_ChuyenBay(flight_date=flight_date, flight_duration=flight_duration,
                                    first_class_seats=first_class_seats,
                                    economy_class_seats=economy_class_seats, id_TuyenBay=id_TuyenBay)

        # Lấy thông tin sân bay trung gian
        intermediate_airports = []
        for key, value in request.form.items():
            if key.startswith("intermediate_airports"):
                parts = key.split("[")
                index = int(parts[1].split("]")[0])
                field = parts[2].split("]")[0]
                if len(intermediate_airports) <= index:
                    intermediate_airports.append({})
                intermediate_airports[index][field] = value
        luusbaytrunggian = dao.save_sbbaytrunggian(intermediate_airports=intermediate_airports, flight=flight)

        return redirect(url_for('lap_lich_chuyen_bay'))

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
        # Chuyển danh sách các đối tượng Row thành một danh sách các chuỗi
        san_bay_trung_gian_list = [row.ten_SanBay for row in sân_bay_trung_gian]

        # Kết hợp các tên sân bay vào một chuỗi
        sân_bay_trung_gian = ', '.join(san_bay_trung_gian_list)
        if route:
            flight_info.append({
                "id": flight.id_ChuyenBay,
                "hành_trình": route.tenTuyen,
                "thời_gian": flight.gio_Bay.strftime('%d-%m-%Y %H:%M'),
                "ghế_hạng_1_còn_trống": flight.GH1_DD,
                "ghế_hạng_2_còn_trống": flight.GH2_DD,
                "GH1": flight.GH1,
                "GH2": flight.GH2,
                "sân_bay_trung_gian": sân_bay_trung_gian,
            })

    return render_template('danhsachchuyenbay.html', flights=flight_info, pagination=flights)


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
    user_id = session.get('_user_id')  # Kiểm tra vai trò của người dùng
    user_role = dao.get_user_role(user_id)
    user_role_change = dao.change_user_role(user_role)
    return render_template('nhan_vien.html', user_role_change=user_role_change)


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
    airport = dao.load_airport()
    id_SanBayDen = request.args.get('noiDi')
    id_SanBayDi = request.args.get('noiDen')
    ngayDi = request.args.get('ngayDi')
    flight = dao.load_flight(id_SanBayDen=id_SanBayDen, id_SanBayDi=id_SanBayDi, ngayDi=ngayDi)

    return render_template('timkiemchuyenbay.html',
                           airport=airport, flight=flight,
                           id_SanBayDi=id_SanBayDi, id_SanBayDen=id_SanBayDen)


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
            # id_user = session.get('id_user')   # Lấy id_user từ session
            id_user = 2
            # Lưu thông tin thanh toán vào cơ sở dữ liệu

            # Lưu thông tin vé
            if dao.save_ticket_info(id_user, seats_info):
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


@app.route('/thaydoiquydinh')
def thaydoiquydinh():
    return render_template('thaydoiquydinh.html')


@app.route('/quydinhbanve')
def quydinhbanve():
    return render_template('quydinhbanve.html')


@app.route('/quydinhve')
def quydinhve():
    return render_template('quydinhve.html')


@app.route('/quydinhsanbay')
def quydinhsanbay():
    return render_template('quydinhsanbay.html')

@app.route('/api/quydinh/sanbay/<int:id>', methods=['GET'])
def get_quy_dinh_san_bay(id):
    quy_dinh = dao.getquydinhsanbay(id)
    if not quy_dinh:
        return jsonify({'message': 'Quy định không tồn tại'}), 404

    return jsonify({
        'SoLuongSanBay': quy_dinh.SoLuongSanBay,
        'ThoiGianBayToiThieu': quy_dinh.ThoiGianBayToiThieu,
        'SanBayTrungGianToiDa': quy_dinh.SanBayTrungGianToiDa,
        'ThoiGianDungToiThieu': quy_dinh.ThoiGianDungToiThieu,
        'ThoiGianDungToiDa': quy_dinh.ThoiGianDungToiDa,
    }), 200

@app.route('/api/quydinh/sanbay/<int:id>', methods=['PUT'])
def update_quy_dinh_san_bay(id):
    try:
        # Lấy dữ liệu JSON từ yêu cầu
        data = request.json
        if not data:
            return jsonify({"message": "Không có dữ liệu gửi lên"}), 400

        luutru = dao.thaydoiquydinhsanbay(id,data)

        return jsonify({"message": "Cập nhật quy định sân bay thành công"}), 200
    except Exception as e:
        return jsonify({"message": f"Có lỗi xảy ra: {str(e)}"}), 500

# API Lấy thông tin quy định bán vé
@app.route('/api/quydinh/banve/<int:id>', methods=['GET'])
def get_quy_dinh_ban_ve(id):
    quy_dinh = dao.getquydinhbanve(id)
    if quy_dinh:
        return quy_dinh
    else:
        return jsonify({"message": "Quy định không tồn tại"}), 404

# API Cập nhật thông tin quy định bán vé
@app.route('/api/quydinh/banve/<int:id>', methods=['PUT'])
def update_quy_dinh_ban_ve(id):
    data = request.json
    quy_dinh = dao.thaydoiquydinhbanve(id,data)
    try:
        if quy_dinh:
            return jsonify({"message": "Cập nhật quy định bán vé thành công"}), 200
    except Exception as e:
        return jsonify({"message": "Cập nhật thất bại", "error": str(e)}), 400

# API Lấy thông tin quy định vé
@app.route('/api/quydinh/ve/<int:id>', methods=['GET'])
def get_quy_dinh_ve(id):
    quy_dinh = dao.getquydinhve(id)
    if quy_dinh:
        return quy_dinh
    return jsonify({"message": "Quy định không tồn tại"}), 404

# API Cập nhật quy định vé
@app.route('/api/quydinh/ve/<int:id>', methods=['PUT'])
def update_quy_dinh_ve(id):
    data = request.json
    quy_dinh = dao.setquydinhve(id,data)

    try:
        if quy_dinh:
            return jsonify({"message": "Cập nhật thành công"}), 200
    except Exception as e:
        return jsonify({"message": "Cập nhật thất bại", "error": str(e)}), 400



if __name__ == '__main__':
    with app.app_context():
        app.run(port=8000, debug=True)
