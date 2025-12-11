from functools import wraps
from flask import request, jsonify


def login_required(f):
    """登录验证装饰器：从请求头获取X-User-Id"""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = request.headers.get('X-User-Id')
        if not user_id:
            return jsonify({
                'success': False,
                'message': '登录已过期，请重新登录'
            }), 401

        try:
            user_id = int(user_id)
        except ValueError:
            return jsonify({
                'success': False,
                'message': '用户ID格式错误'
            }), 400

        # 将user_id传入被装饰的函数
        return f(user_id, *args, **kwargs)

    return decorated_function
