import os
import sys
# 解决包导入问题（确保能找到api目录）
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from flask_cors import CORS
# 导入蓝图和数据库初始化
from api.src.controller.auth_controller import auth_bp
from api.src.controller.contact_controller import contact_bp
from api.src.controller.group_controller import group_bp
from api.src.model.db import init_db

# 初始化Flask应用
app = Flask(__name__)

# 修复跨域：允许所有来源（开发环境）
CORS(
    app,
    supports_credentials=True,
    resources=r"/api/*",
    origins="*",  # 允许所有前端地址
    allow_headers=["Content-Type", "X-User-Id", "Authorization"],
    methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"]
)

# 注册所有蓝图
app.register_blueprint(auth_bp)
app.register_blueprint(contact_bp)
app.register_blueprint(group_bp)

# 初始化数据库
init_db()

# 测试接口（用于验证服务是否启动）
@app.route('/api/health', methods=['GET'])
def health_check():
    return {
        "status": "success",
        "message": "后端服务正常运行",
        "port": 5000
    }

if __name__ == '__main__':
    print("🚀 通讯录后端服务启动中...")
    print("🔗 访问地址：http://127.0.0.1:5000")
    print("📝 健康检查：http://127.0.0.1:5000/api/health")
    # 启动服务（0.0.0.0允许所有IP访问）
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        use_reloader=False  # 避免重复初始化数据库
    )
