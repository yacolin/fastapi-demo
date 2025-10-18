# FastAPI Demo - 媒体管理 API

一个基于 FastAPI 构建的现代化异步 RESTful API，用于管理专辑、歌曲和媒体项目。具有标准化响应处理、全面的错误管理和异步数据库操作等特性。

## 🚀 特性

- **现代异步架构**：基于 FastAPI 完全支持 async/await
- **RESTful API 设计**：简洁的版本化 API 端点（`/api/v1/`）
- **标准化响应**：统一的响应格式和业务状态码
- **全面的错误处理**：集中式异常处理器和详细日志记录
- **数据库操作**：SQLAlchemy 2.0+ 支持异步 MySQL/SQLite
- **类型安全**：完整的 Pydantic v2 验证和类型提示
- **分页支持**：列表端点包含总数统计
- **任务队列就绪**：集成 Celery 用于后台任务
- **安全特性**：JWT、bcrypt 和加密支持

## 📋 技术栈

### 核心框架

- **FastAPI** (v0.119.0) - 现代 Web 框架
- **Uvicorn** (v0.37.0) - ASGI 服务器
- **Pydantic** (v2.11.7) - 数据验证

### 数据库

- **SQLAlchemy** (v2.0.44) - 支持异步的 ORM
- **aiomysql** (v0.2.0) - 异步 MySQL 驱动
- **aiosqlite** (v0.21.0) - 异步 SQLite 驱动

### 后台任务

- **Celery** (v5.5.3) - 分布式任务队列
- **Redis** (v6.4.0) - 消息代理

### 安全

- **PyJWT** (v2.10.1) - JSON Web Tokens
- **bcrypt** (v5.0.0) - 密码哈希
- **cryptography** (v46.0.3) - 加密操作

### 监控与日志

- **Loguru** (v0.7.3) - 高级日志记录
- **Sentry SDK** (v2.42.0) - 错误追踪

## 📁 项目结构

```
fastapi-demo/
├── configs/              # 配置模块
│   ├── __init__.py      # 配置导出
│   └── db.py            # 数据库配置
├── controllers/         # API 路由处理器
│   ├── __init__.py      # 路由聚合，包含 /api/v1/ 前缀
│   ├── album.py         # 专辑 CRUD 端点
│   ├── song.py          # 歌曲 CRUD 端点
│   ├── item.py          # 项目 CRUD 端点
│   └── team.py          # 球队 CRUD 端点
├── utils/               # 共享工具
│   ├── __init__.py      # 工具导出
│   ├── biz_code.py      # 业务状态码
│   ├── restful.py       # RESTful 响应工具
│   ├── exception_handlers.py  # 全局异常处理器
│   └── USAGE_EXAMPLES.md      # 工具使用指南
├── main.py              # 应用程序入口
├── requirements.txt     # Python 依赖
└── README.md           # 英文文档
```

## 🛠️ 安装

### 前置要求

- Python 3.9+
- MySQL（或用于开发的 SQLite）
- Redis（可选，用于 Celery 任务）

### 安装步骤

1. **克隆仓库**

   ```bash
   git clone <repository-url>
   cd fastapi-demo
   ```

2. **创建虚拟环境**

   ```bash
   python -m venv venv

   # Windows
   venv\Scripts\activate

   # Linux/Mac
   source venv/bin/activate
   ```

3. **安装依赖**

   ```bash
   pip install -r requirements.txt
   ```

4. **配置环境变量**

   在项目根目录创建 `.env` 文件：

   ```env
   # 数据库配置
   MYSQL_HOST=localhost
   MYSQL_PORT=3306
   MYSQL_USER=root
   MYSQL_PASSWORD=your_password
   MYSQL_DB=your_database

   # 应用配置
   LOG_LEVEL=INFO
   APP_DEBUG=false
   ```

5. **运行应用程序**

   ```bash
   uvicorn main:app --reload
   ```

   API 将在 `http://localhost:8000` 上可用

## 📚 API 文档

服务器运行后，访问交互式 API 文档：

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔌 API 端点

所有端点都使用 `/api/v1/` 前缀

### 专辑 (Albums)

| 方法   | 端点                  | 描述                 |
| ------ | --------------------- | -------------------- |
| POST   | `/api/v1/albums`      | 创建新专辑           |
| GET    | `/api/v1/albums`      | 列出所有专辑（分页） |
| GET    | `/api/v1/albums/{id}` | 按 ID 获取专辑       |
| PUT    | `/api/v1/albums/{id}` | 更新专辑             |
| DELETE | `/api/v1/albums/{id}` | 删除专辑             |

### 歌曲 (Songs)

| 方法   | 端点                             | 描述                 |
| ------ | -------------------------------- | -------------------- |
| POST   | `/api/v1/songs`                  | 创建新歌曲           |
| GET    | `/api/v1/songs`                  | 列出所有歌曲（分页） |
| GET    | `/api/v1/songs/{id}`             | 按 ID 获取歌曲       |
| GET    | `/api/v1/songs/album/{album_id}` | 按专辑获取歌曲       |
| PUT    | `/api/v1/songs/{id}`             | 更新歌曲             |
| DELETE | `/api/v1/songs/{id}`             | 删除歌曲             |

### 项目 (Items)

| 方法   | 端点                 | 描述           |
| ------ | -------------------- | -------------- |
| POST   | `/api/v1/items`      | 创建新项目     |
| GET    | `/api/v1/items`      | 列出所有项目   |
| GET    | `/api/v1/items/{id}` | 按 ID 获取项目 |
| PUT    | `/api/v1/items/{id}` | 更新项目       |
| DELETE | `/api/v1/items/{id}` | 删除项目       |

### 球队 (Teams)

| 方法   | 端点                 | 描述                 |
| ------ | -------------------- | -------------------- |
| POST   | `/api/v1/teams`      | 创建新球队           |
| GET    | `/api/v1/teams`      | 列出所有球队（分页） |
| GET    | `/api/v1/teams/{id}` | 按 ID 获取球队       |
| PUT    | `/api/v1/teams/{id}` | 更新球队             |
| DELETE | `/api/v1/teams/{id}` | 删除球队             |

## 📝 响应格式

所有 API 响应都遵循标准化格式：

### 成功响应

```json
{
  "code": 0,
  "message": "请求成功",
  "data": {
    "items": [...],
    "total": 100
  },
  "timestamp": 1729260645
}
```

### 错误响应

```json
{
  "code": 4004,
  "message": "资源不存在",
  "data": null,
  "errors": {
    "message": "详细错误信息"
  },
  "timestamp": 1729260645
}
```

## 🎯 业务状态码

### 成功状态码 (2xxx)

- `2000` - 请求成功
- `2001` - 创建成功
- `2004` - 删除成功
- `2005` - 更新成功

### 客户端错误码 (4xxx)

- `4000` - 错误的请求
- `4001` - 未授权
- `4003` - 禁止访问
- `4004` - 未找到
- `4101` - 无效的分页参数

### 服务器错误码 (5xxx)

- `5000` - 服务器内部错误
- `5100` - 数据库错误
- `5102` - 数据库删除失败
- `5103` - 数据库更新失败
- `5104` - 数据库创建失败

## 🔧 开发

### 运行测试

```bash
# 添加你的测试命令
pytest
```

### 代码质量

```bash
# 类型检查
mypy .

# 代码检查
flake8 .

# 代码格式化
black .
```

### 数据库迁移

```bash
# 创建迁移
alembic revision --autogenerate -m "description"

# 应用迁移
alembic upgrade head
```

## 🐳 Docker 支持

```dockerfile
# Dockerfile 示例
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 📖 其他资源

- [FastAPI 文档](https://fastapi.tiangolo.com/zh/)
- [SQLAlchemy 文档](https://docs.sqlalchemy.org/)
- [Pydantic 文档](https://docs.pydantic.dev/)

## 🤝 贡献

欢迎贡献！请随时提交 Pull Request。

## 📄 许可证

本项目采用 MIT 许可证。

## 👤 作者

你的名字 - [你的 GitHub 主页](https://github.com/yourusername)

## 🙏 致谢

- FastAPI 框架和社区
- SQLAlchemy 异步支持
- 所有贡献者和维护者
