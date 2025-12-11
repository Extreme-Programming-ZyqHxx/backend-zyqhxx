from sqlite3 import Row
from api.src.model.db import get_db_connection
import sqlite3


class Group:
    @staticmethod
    def get_all(user_id: int) -> list[Row]:
        """获取当前用户的所有分组"""
        conn = get_db_connection()
        groups = conn.execute(
            'SELECT * FROM groups WHERE user_id = ?',
            (user_id,)
        ).fetchall()
        conn.close()
        return groups

    @staticmethod
    def add(group_name: str, user_id: int) -> int:
        """添加分组（关联当前用户）"""
        conn = get_db_connection()
        try:
            cursor = conn.execute(
                'INSERT INTO groups (group_name, user_id) VALUES (?, ?)',
                (group_name, user_id)
            )
            conn.commit()
            group_id = cursor.lastrowid
        except sqlite3.IntegrityError:
            group_id = -1  # 分组名称重复
        finally:
            conn.close()
        return group_id

    @staticmethod
    def get_by_id(group_id: int, user_id: int) -> Row:
        """获取当前用户的指定分组"""
        conn = get_db_connection()
        group = conn.execute(
            'SELECT * FROM groups WHERE id = ? AND user_id = ?',
            (group_id, user_id)
        ).fetchone()
        conn.close()
        return group
