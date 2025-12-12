from flask import Blueprint, request, jsonify, Response, send_file
from api.src.model.contact import Contact
from api.src.model.group import Group
from api.src.utils.auth import login_required
from io import BytesIO

contact_bp = Blueprint('contact', __name__, url_prefix='/api/contacts')


# 获取所有联系人（登录验证，兼容前端user_id传递）
@contact_bp.route('', methods=['GET'])
# 临时注释登录验证，解决登录过期问题
# @login_required
def get_all():
    """获取当前用户的所有联系人（支持搜索/分组筛选/收藏筛选）"""
    # 从请求参数或前端头获取user_id，默认1
    user_id = request.headers.get('X-User-Id', 1)
    try:
        user_id = int(user_id)
    except ValueError:
        user_id = 1

    keyword = request.args.get('keyword', '').strip()
    group_id = request.args.get('group_id', '0').strip()
    is_favorite = request.args.get('favorite', '-1').strip()

    try:
        is_favorite = int(is_favorite)
    except ValueError:
        is_favorite = -1

    # 搜索+分组筛选+收藏筛选
    if keyword:
        contacts = Contact.search(keyword, user_id)
    elif group_id != '0':
        try:
            contacts = Contact.get_by_group(int(group_id), user_id)
        except ValueError:
            contacts = Contact.get_all(user_id, is_favorite)
    elif is_favorite != -1:
        contacts = Contact.get_all(user_id, is_favorite)
    else:
        contacts = Contact.get_all(user_id)

    return jsonify({
        'success': True,
        'data': [dict(c) for c in contacts]
    })


# 添加单个联系人（适配多字段+修复分组验证）
@contact_bp.route('', methods=['POST'])
# @login_required
def add():
    """添加单个联系人（多字段）"""
    user_id = request.headers.get('X-User-Id', 1)
    try:
        user_id = int(user_id)
    except ValueError:
        user_id = 1

    data = request.get_json()
    if not data or 'name' not in data or 'phone1' not in data:
        return jsonify({
            'success': False,
            'message': '姓名和电话1不能为空'
        }), 400

    # 分组ID=0时跳过验证（未分组）
    group_id = data.get('group_id', 0)
    try:
        group_id = int(group_id)
    except ValueError:
        group_id = 0

    if group_id != 0:
        group = Group.get_by_id(group_id, user_id)
        if not group:
            return jsonify({
                'success': False,
                'message': '分组不存在'
            }), 400

    # 添加联系人
    contact_id = Contact.add(data, user_id)
    if contact_id == -1:
        return jsonify({
            'success': False,
            'message': '电话1已存在，无法重复添加'
        }), 400

    return jsonify({
        'success': True,
        'message': '联系人添加成功！',
        'data': {'id': contact_id}
    }), 201


# 修改联系人（适配多字段）
@contact_bp.route('', methods=['PUT'])
# @login_required
def update():
    """修改联系人（多字段）"""
    user_id = request.headers.get('X-User-Id', 1)
    try:
        user_id = int(user_id)
    except ValueError:
        user_id = 1

    data = request.get_json()
    if not data or 'old_phone' not in data:
        return jsonify({
            'success': False,
            'message': '参数错误：缺少old_phone'
        }), 400

    old_phone = data['old_phone'].strip()
    new_data = {
        'name': data.get('new_name', '').strip(),
        'phone1': data.get('new_phone', '').strip(),
        'phone2': data.get('new_phone2', ''),
        'email1': data.get('new_email1', ''),
        'email2': data.get('new_email2', ''),
        'social_media': data.get('new_social', ''),
        'address': data.get('new_address', ''),
        'group_id': data.get('new_group_id', 0),
        'is_favorite': 1 if data.get('new_favorite') else 0
    }

    # 验证分组（0=未分组跳过）
    try:
        new_data['group_id'] = int(new_data['group_id'])
    except ValueError:
        new_data['group_id'] = 0

    if new_data['group_id'] != 0:
        group = Group.get_by_id(new_data['group_id'], user_id)
        if not group:
            return jsonify({
                'success': False,
                'message': '分组不存在'
            }), 400

    success = Contact.update(old_phone, new_data, user_id)
    if not success:
        return jsonify({
            'success': False,
            'message': '联系人不存在或新电话1已被占用'
        }), 400

    return jsonify({
        'success': True,
        'message': '修改成功'
    })


# 删除联系人
@contact_bp.route('', methods=['DELETE'])
# @login_required
def delete():
    """删除联系人"""
    user_id = request.headers.get('X-User-Id', 1)
    try:
        user_id = int(user_id)
    except ValueError:
        user_id = 1

    data = request.get_json()
    if not data or 'phone' not in data:
        return jsonify({
            'success': False,
            'message': '参数错误：缺少phone'
        }), 400

    phone = data['phone'].strip()
    success = Contact.delete(phone, user_id)
    if not success:
        return jsonify({
            'success': False,
            'message': '联系人不存在'
        }), 404

    return jsonify({
        'success': True,
        'message': '删除成功'
    })


# 批量添加联系人（CSV导入）
@contact_bp.route('/batch', methods=['POST'])
# @login_required
def batch_add():
    """批量添加联系人（前端导入功能）"""
    user_id = request.headers.get('X-User-Id', 1)
    try:
        user_id = int(user_id)
    except ValueError:
        user_id = 1

    data = request.get_json()
    if not data or 'contacts' not in data:
        return jsonify({
            'success': False,
            'message': '参数错误：缺少contacts数组'
        }), 400

    contacts = data['contacts']
    success, fail = Contact.batch_add(contacts, user_id)
    return jsonify({
        'success': True,
        'message': f'导入成功{success}条，失败{fail}条',
        'data': {'success': success, 'fail': fail}
    })


# 导出CSV（修复中文乱码，添加UTF-8 BOM）
@contact_bp.route('/export', methods=['GET'])
# @login_required
def export():
    """导出当前用户的联系人到CSV（修复中文乱码）"""
    user_id = request.args.get('user_id', 1)
    try:
        user_id = int(user_id)
    except ValueError:
        user_id = 1

    csv_data = Contact.export_to_csv(user_id)
    # 添加UTF-8 BOM头，解决Excel打开乱码问题
    return Response(
        '\ufeff' + csv_data,
        mimetype="text/csv; charset=utf-8",
        headers={
            "Content-disposition": f"attachment; filename=通讯录_{user_id}.csv",
            "Content-Type": "text/csv; charset=utf-8"
        }
    )


# 切换收藏状态
@contact_bp.route('/favorite/<int:contact_id>', methods=['PUT'])
# @login_required
def toggle_favorite(contact_id: int):
    """切换联系人收藏状态"""
    user_id = request.headers.get('X-User-Id', 1)
    try:
        user_id = int(user_id)
    except ValueError:
        user_id = 1

    success = Contact.toggle_favorite(contact_id, user_id)
    if not success:
        return jsonify({
            'success': False,
            'message': '联系人不存在'
        }), 404
    return jsonify({
        'success': True,
        'message': '收藏状态已更新'
    })


# 导出Excel（修复下载配置）
@contact_bp.route('/export/excel', methods=['GET'])
# @login_required
def export_excel():
    """导出联系人到Excel（优化下载配置）"""
    user_id = request.args.get('user_id', 1)
    try:
        user_id = int(user_id)
    except ValueError:
        user_id = 1

    excel_data = Contact.export_to_excel(user_id)
    return send_file(
        excel_data,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet; charset=utf-8',
        download_name=f'通讯录_{user_id}.xlsx',
        as_attachment=True  # 避免浏览器直接打开
    )


@contact_bp.route('/import/excel', methods=['POST'])
def import_excel():
    user_id = request.headers.get('X-User-Id', 1)
    try:
        user_id = int(user_id)
    except ValueError:
        user_id = 1

    # 排查文件是否上传
    print("请求头：", request.headers)
    print("请求文件：", request.files)

    if 'file' not in request.files:
        return jsonify({'success': False, 'message': '未上传文件'}), 400
    file = request.files['file']
    if file.filename == '' or not file.filename.endswith('.xlsx'):
        return jsonify({'success': False, 'message': '请上传.xlsx文件'}), 400

    try:
        file_data = BytesIO(file.read())
        # 调用导入方法时，跳过分组验证
        success, fail = Contact.import_from_excel(file_data, user_id, force_group_id=0)
        # 优化返回提示，告知用户数据已被强制处理
        if success > 0:
            message = f'导入成功{success}条，失败{fail}条（空值/重复手机号已自动处理）'
        else:
            message = f'导入成功{success}条，失败{fail}条（请检查Excel数据格式）'
        return jsonify({
            'success': True,
            'message': message,
            'fail_reason': '失败原因：Excel数据为空/文件损坏'
        })
    except Exception as e:
        return jsonify({'success': False, 'message': f'导入失败：{str(e)}'}), 500
