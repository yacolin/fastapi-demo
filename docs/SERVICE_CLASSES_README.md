# Service Classes Refactoring

## 概述

为了减少导入语句的数量并提高代码的可维护性，我们将工具函数封装成了服务类。

## 新增服务类

### 1. **AuthService** ([`utils/auth_service.py`](utils/auth_service.py))

封装所有认证相关的功能：

```python
from utils import AuthService

# 密码哈希
hashed = AuthService.hash_password("password123")

# 验证密码
is_valid = AuthService.verify_password("password123", hashed)

# 生成访问令牌
access_token = AuthService.create_access_token(user_id=1)

# 生成刷新令牌
refresh_token = AuthService.create_refresh_token(user_id=1)

# 生成令牌对（访问令牌 + 刷新令牌）
tokens = AuthService.create_token_pair(user_id=1)
# 返回: {"access_token": "...", "refresh_token": "..."}

# 验证令牌
claims = AuthService.validate_token(token)
```

**方法列表：**

- `hash_password(password: str) -> str` - 哈希密码
- `verify_password(password: str, hashed: str) -> bool` - 验证密码
- `create_access_token(user_id: int) -> str` - 生成访问令牌（15 分钟）
- `create_refresh_token(user_id: int) -> str` - 生成刷新令牌（7 天）
- `create_token_pair(user_id: int) -> dict` - 生成令牌对
- `validate_token(token: str) -> Optional[dict]` - 验证并解码令牌

### 2. **ResponseService** ([`utils/response_service.py`](utils/response_service.py))

封装所有响应相关的功能：

```python
from utils import ResponseService

# 成功响应
return ResponseService.success(data={"user": "张三"})

# 创建成功响应 (201)
return ResponseService.created(data={"id": 1})

# 更新成功响应 (200)
return ResponseService.updated(data={"id": 1})

# 删除成功响应 (204)
return ResponseService.deleted()

# 错误响应
return ResponseService.bad_request("参数错误")
return ResponseService.unauthorized("未授权")
return ResponseService.not_found("资源不存在")
return ResponseService.internal_error("服务器错误")

# 抛出业务异常
raise ResponseService.Error(biz_code=4000, details={"message": "错误详情"})
```

**方法列表：**

- `success(data, biz_code=2000)` - 成功响应
- `created(data)` - 创建成功 (201)
- `updated(data)` - 更新成功 (200)
- `deleted()` - 删除成功 (204)
- `bad_request(message, biz_code=4000)` - 错误请求 (400)
- `unauthorized(message, biz_code=4001)` - 未授权 (401)
- `not_found(message, biz_code=4004)` - 未找到 (404)
- `internal_error(message, biz_code=5000)` - 服务器错误 (500)
- `Error` - BusinessError 类的别名

## 重构对比

### 重构前 ([`controllers/user.py`](controllers/user.py))

```python
# 导入太多
from utils import (
    success, unauthorized, bad_request, internal_error, BusinessError,
    hash_password, check_password_hash, generate_access_token,
    generate_refresh_token, decode_token,
    OK, BAD_REQUEST as BIZ_BAD_REQUEST, UNAUTHORIZED,
    INVALID_PWD, USER_NOT_FOUND, DB_CREATE,
    ACCESS_TK_GEN, REFRESH_TK_GEN, TK_INVALID, TK_USER_ID, ERR_INTERNAL
)

# 使用函数
hashed = hash_password(payload.password)
if not check_password_hash(payload.password, user.password):
    return unauthorized(biz_code=INVALID_PWD, errors={"message": "密码错误"})

access_token = generate_access_token(user.id)
refresh_token = generate_refresh_token(user.id)
return success(biz_code=OK, data={"access_token": access_token, "refresh_token": refresh_token})
```

### 重构后

```python
# 简洁的导入
from utils import AuthService, ResponseService
from utils.biz_code import (
    OK, BAD_REQUEST as BIZ_BAD_REQUEST,
    INVALID_PWD, USER_NOT_FOUND, DB_CREATE,
    ACCESS_TK_GEN, TK_INVALID, TK_USER_ID, ERR_INTERNAL
)

# 使用服务类 - 更清晰的语义
hashed = AuthService.hash_password(payload.password)
if not AuthService.verify_password(payload.password, user.password):
    return ResponseService.unauthorized("密码错误", INVALID_PWD)

# 一次性生成令牌对
tokens = AuthService.create_token_pair(user.id)
return ResponseService.success(data=tokens, biz_code=OK)
```

## 优势

### 1. **代码更简洁**

- ✅ 导入语句从 15+ 行减少到 2-3 行
- ✅ 功能更易于组织和查找

### 2. **语义更清晰**

- ✅ `AuthService.verify_password()` 比 `check_password_hash()` 更直观
- ✅ `ResponseService.unauthorized()` 清楚表明这是一个响应
- ✅ `create_token_pair()` 一次性返回两个令牌，避免重复代码

### 3. **更易维护**

- ✅ 所有认证相关功能集中在 `AuthService`
- ✅ 所有响应相关功能集中在 `ResponseService`
- ✅ 修改实现时只需修改服务类

### 4. **更好的可扩展性**

- ✅ 可以轻松添加新方法到服务类
- ✅ 可以添加类级别的配置和状态管理
- ✅ 支持继承和多态

### 5. **向后兼容**

- ✅ 原有的函数式 API 仍然可用
- ✅ 可以逐步迁移到服务类

## 使用示例

### 完整登录流程

```python
@router.post("/login")
async def login(payload: LoginInput, session: AsyncSession = Depends(get_session)):
    # 查询用户
    stmt = select(User).where(User.username == payload.username)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        return ResponseService.unauthorized("用户不存在", USER_NOT_FOUND)

    # 验证密码
    if not AuthService.verify_password(payload.password, user.password):
        return ResponseService.unauthorized("密码错误", INVALID_PWD)

    # 生成令牌对
    try:
        tokens = AuthService.create_token_pair(user.id)
        return ResponseService.success(data=tokens, biz_code=OK)
    except Exception as e:
        return ResponseService.internal_error("生成token失败", ACCESS_TK_GEN)
```

### 完整注册流程

```python
@router.post("/register")
async def register(payload: RegisterInput, session: AsyncSession = Depends(get_session)):
    # 检查用户是否存在
    if await user_exists(payload.username, session):
        return ResponseService.bad_request("用户名已存在", BIZ_BAD_REQUEST)

    # 创建用户
    try:
        hashed_password = AuthService.hash_password(payload.password)
        user = User(username=payload.username, password=hashed_password)

        session.add(user)
        await session.commit()

        return ResponseService.success(biz_code=OK, data=None)
    except Exception as e:
        await session.rollback()
        return ResponseService.internal_error("注册失败", DB_CREATE)
```

## 迁移指南

如果你有现有代码使用函数式 API，可以按以下步骤迁移：

1. **更新导入**

   ```python
   # 旧
   from utils import hash_password, check_password_hash, success, unauthorized

   # 新
   from utils import AuthService, ResponseService
   ```

2. **替换认证函数调用**

   ```python
   # 旧
   hashed = hash_password(password)
   is_valid = check_password_hash(password, hashed)
   token = generate_access_token(user_id)

   # 新
   hashed = AuthService.hash_password(password)
   is_valid = AuthService.verify_password(password, hashed)
   token = AuthService.create_access_token(user_id)
   ```

3. **替换响应函数调用**

   ```python
   # 旧
   return success(biz_code=OK, data=data)
   return unauthorized(biz_code=UNAUTHORIZED, errors={"message": "错误"})

   # 新
   return ResponseService.success(data=data, biz_code=OK)
   return ResponseService.unauthorized("错误", UNAUTHORIZED)
   ```

## 注意事项

1. **服务类使用静态方法** - 无需实例化，直接通过类调用
2. **原函数仍可用** - 为了向后兼容，原有的函数式 API 仍然导出
3. **参数顺序** - `ResponseService` 的错误方法将消息作为第一个参数，更符合直觉

## 总结

通过使用服务类封装，我们实现了：

- ✅ **更清晰的代码组织**
- ✅ **更少的导入语句**
- ✅ **更好的语义表达**
- ✅ **更易于维护和扩展**

推荐在新代码中使用服务类，现有代码可以逐步迁移。
