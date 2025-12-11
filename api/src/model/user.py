from sqlite3 import Row
from api.src.model.db import get_db_connection
import sqlite3


class User:
    @staticmethod
    def register(username: str, password: str, email: str = '') -> int:
        """注册用户，返回user_id（-1表示用户名重复）"""
        conn = get_db_connection()
        try:
            cursor = conn.execute(
                'INSERT INTO users (username, password, email) VALUES (?, ?, ?)',
                (username, password, email)
            )
            conn.commit()
            user_id = cursor.lastrowid
        except sqlite3.IntegrityError:
            user_id = -1  # 用户名/邮箱重复
        finally:
            conn.close()
        return user_id

    @staticmethod
    def login(username: str, password: str) -> Row:
        """登录验证，返回用户信息（None表示失败）"""
        conn = get_db_connection()
        user = conn.execute(
            'SELECT * FROM users WHERE username = ? AND password = ?',
            (username, password)
        ).fetchone()
        conn.close()
        return user
