# 蜜罐系统部署和使用指南

## 🚀 快速启动

### 1. 启动数据库服务
```powershell
cd D:\honeypot_project\honeypot
docker compose up -d
```

### 2. 安装依赖
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 3. 初始化数据库
```powershell
# 设置环境变量
$env:MYSQL_HOST="127.0.0.1"
$env:MYSQL_PORT="3306"
$env:MYSQL_USER="root"
$env:MYSQL_PASSWORD="example"
$env:MYSQL_DB="honeypot"
$env:SECRET_KEY="your-secret-key-here"
$env:API_SECRET_KEY="your-api-secret-key-here"

# 初始化数据库和创建管理员
python manage.py all
```

### 4. 启动应用
```powershell
python run.py
```

### 5. 访问系统
- 管理后台: http://localhost:5000/login
- 数据库管理: http://localhost:5000/admin/database
- 可视化地图: http://localhost:5000/admin/map

## 📊 功能特性

### ✅ 已实现功能
- **用户认证**: 登录/注册，CSRF保护，速率限制
- **攻击捕获**: API接口，签名验证，IP追踪
- **数据管理**: MySQL存储，Redis缓存，自动清理
- **可视化**: 仪表盘，攻击列表，攻击者画像，全球地图
- **安全防护**: API签名验证，登录限制，数据加密

### 🔧 管理命令

#### 数据库迁移
```powershell
# 初始化迁移
python migrate.py db init

# 创建迁移
python migrate.py db migrate -m "描述"

# 应用迁移
python migrate.py db upgrade
```

#### 数据清理
```powershell
# 清理30天前的数据
python app/tasks.py cleanup 30

# 生成每日报告
python app/tasks.py report
```

## 🔐 API使用

### 攻击捕获接口
```bash
# 生成签名
timestamp=$(date +%s)
data='{"service":"web","signature":"test","severity":"high"}'
signature=$(echo -n "${timestamp}${data}" | openssl dgst -sha256 -hmac "your-api-secret-key" -binary | base64)

# 发送请求
curl -X POST http://localhost:5000/api/capture \
  -H "Content-Type: application/json" \
  -H "X-API-Signature: $signature" \
  -H "X-API-Timestamp: $timestamp" \
  -d "$data"
```

## 🗺️ 可视化地图

访问 `/admin/map` 查看全球攻击分布：
- 鼠标悬停查看攻击次数
- 不同颜色表示攻击频率
- 支持缩放和拖拽

## 🛠️ 系统架构

```
蜜罐系统
├── 前端界面 (Templates)
│   ├── 登录/注册页面
│   ├── 管理仪表盘
│   ├── 攻击事件列表
│   ├── 攻击者画像
│   └── 可视化地图
├── 后端API (Flask)
│   ├── 认证模块 (auth)
│   ├── 管理模块 (admin)
│   └── 捕获模块 (api)
├── 数据存储
│   ├── MySQL (主数据库)
│   └── Redis (缓存/限流)
└── 任务调度
    ├── 数据清理
    └── 报告生成
```

## 🔒 安全配置

### 环境变量
```bash
SECRET_KEY=your-flask-secret-key
API_SECRET_KEY=your-api-secret-key
MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your-password
MYSQL_DB=honeypot
REDIS_HOST=127.0.0.1
REDIS_PORT=6379
```

### 生产环境建议
1. 修改默认密码和密钥
2. 启用HTTPS
3. 配置防火墙规则
4. 定期备份数据
5. 监控系统日志

## 📈 监控和维护

### 日志查看
```powershell
# 查看容器日志
docker logs honeypot-mysql
docker logs honeypot-redis

# 查看应用日志
# 应用运行时会在控制台显示日志
```

### 数据备份
```powershell
# MySQL备份
docker exec honeypot-mysql mysqldump -u root -pexample honeypot > backup.sql

# Redis备份
docker exec honeypot-redis redis-cli BGSAVE
```

## 🆘 故障排除

### 常见问题
1. **数据库连接失败**: 检查MySQL容器是否启动
2. **模板未找到**: 确认Flask应用配置正确
3. **API签名验证失败**: 检查API_SECRET_KEY配置
4. **地图不显示**: 检查网络连接，可能需要代理

### 重置系统
```powershell
# 停止所有容器
docker compose down

# 删除数据卷
docker volume rm honeypot_mysql_data honeypot_redis_data

# 重新启动
docker compose up -d
python manage.py all
```

## 📞18792307702 技术支持

如有问题，请检查：
1. 所有容器是否正常运行
2. 环境变量是否正确设置
3. 数据库连接是否正常
4. 网络连接是否畅通
