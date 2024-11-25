import random
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, Float, ForeignKey, Enum
from appQLChuyenBay import db, app
from enum import Enum as RoleEnum
import hashlib
# from flask_login import UserMixin

