#!/usr/bin/env python3
"""蜜罐系统启动脚本"""
import os
from app import create_app

app = create_app()

if __name__ == '__main__':
    # ===== 仅调试：打印实时连接信息 =====
    user = os.getenv('MYSQL_USER')
    pwd  = os.getenv('MYSQL_PASSWORD')
    host = os.getenv('MYSQL_HOST')
    port = os.getenv('MYSQL_PORT')
    db   = os.getenv('MYSQL_DB')
    print(f'>>> DEBUG 环境变量：'
          f'USER={user}  PWD={pwd}  HOST={host}:{port}  DB={db}')
    # ===== 调试结束 =====

    os.environ.setdefault('FLASK_APP', 'app')
    os.environ.setdefault('FLASK_ENV', 'development')
    app.run(host='0.0.0.0', port=5000, debug=True)