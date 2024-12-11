from flask_mail import Mail

from appQLChuyenBay import app
from flask_admin import Admin


admin = Admin(app=app, name='QUẢN TRỊ QUẢN LÝ CHUYẾN BAY', template_mode='bootstrap4')
