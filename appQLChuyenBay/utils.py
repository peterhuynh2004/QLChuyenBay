import os.path

from flask import Flask
from appQLChuyenBay import app
import json

#Tạo hàm đọc chung  json qua đường dẫn tương đối (path)
def read_json(path):
   with open(path, "r") as f:
       return json.load(f)
#Hàm tự động đóng

def load_index():
    return read_json(os.path.join(app.root_path, 'data/index.json'))

