import re
from flask import Blueprint, request, jsonify
from api.src.model.user import User  # 导入User模型
from api.src.model.db import get_db_connection  # 导入数据库连接

auth_bp = Blueprint('auth', __name__, url_prefix='/api')


@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({
            'success': False,
            'message': '用户名和密码不能为空'
        }), 400

    # 邮箱格式验证
    email = data.get('email', '').strip()
    if email and not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', email):
        return jsonify({
            'success': False,
            'message': '请输入有效的邮箱地址'
        }), 400

    username = data['username'].strip()
    password = data['password'].strip()

    # 调用User模型的注册方法
    user_id = User.register(username, password, email)
    if user_id == -1:
        return jsonify({
            'success': False,
            'message': '用户名或邮箱已存在'
        }), 400

    return jsonify({
        'success': True,
        'message': '注册成功',
        'data': {'user_id': user_id, 'username': username}
    }), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({
            'success': False,
            'message': '用户名和密码不能为空'
        }), 400

    username = data['username'].strip()
    password = data['password'].strip()
    user = User.login(username, password)

    if not user:
        return jsonify({
            'success': False,
            'message': '用户名或密码错误'
        }), 401

    return jsonify({
        'success': True,
        'message': '登录成功',
        'data': {
            'user_id': user['id'],
            'username': user['username']
        }
    })
