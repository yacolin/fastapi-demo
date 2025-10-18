# RESTful API Response Usage Examples

## 导入模块

```python
from utils.restful import (
    success, created, updated, deleted, no_content,
    bad_request, unauthorized, forbidden, not_found,
    internal_error, db_error,
    BusinessError, new_business_error
)
from utils.biz_code import (
    OK, CREATED, UPDATED, DELETED,
    BAD_REQUEST, NOT_FOUND, INVALID_PAGE,
    DB_CREATE, DB_UPDATE, DB_DELETE
)
```

## 基础用法

### 1. 成功响应

```python
from fastapi import APIRouter
from utils.restful import success, created, updated, deleted

router = APIRouter()

# 标准成功响应
@router.get("/items")
async def get_items():
    items = [{"id": 1, "name": "Item 1"}]
    return success(data=items)
    # 返回: {"code": 0, "message": "请求成功", "data": [...], "timestamp": "..."}

# 创建成功 (201)
@router.post("/items")
async def create_item(item: dict):
    new_item = {"id": 1, **item}
    return created(data=new_item)
    # 返回: {"code": 0, "message": "创建成功", "data": {...}, "timestamp": "..."}

# 更新成功 (200)
@router.put("/items/{id}")
async def update_item(id: int, item: dict):
    updated_item = {"id": id, **item}
    return updated(data=updated_item)

# 删除成功 (204)
@router.delete("/items/{id}")
async def delete_item(id: int):
    return deleted()
```

### 2. 错误响应

```python
from utils.restful import bad_request, not_found, unauthorized
from utils.biz_code import INVALID_PAGE, NOT_FOUND as BIZ_NOT_FOUND

# 400 Bad Request
@router.get("/items")
async def get_items(page: int = 1):
    if page < 1:
        return bad_request(
            biz_code=INVALID_PAGE,
            errors={"field": "page", "message": "页码必须大于0"}
        )
    return success(data=[])

# 404 Not Found
@router.get("/items/{id}")
async def get_item(id: int):
    item = None  # 假设未找到
    if not item:
        return not_found(
            biz_code=BIZ_NOT_FOUND,
            errors={"message": f"ID为{id}的项目不存在"}
        )
    return success(data=item)

# 401 Unauthorized
@router.get("/protected")
async def protected_route(token: str = None):
    if not token:
        return unauthorized(
            biz_code=4001,
            errors={"message": "请提供认证令牌"}
        )
    return success(data={"message": "访问成功"})
```

### 3. 数据库错误处理

```python
from utils.restful import db_error, BusinessError
from utils.biz_code import DB_CREATE, DB_UPDATE, DB_DELETE
from sqlalchemy.exc import SQLAlchemyError

@router.post("/albums")
async def create_album(album: dict, session: AsyncSession = Depends(get_session)):
    try:
        new_album = Album(**album)
        session.add(new_album)
        await session.commit()
        return created(data={"id": new_album.id})
    except SQLAlchemyError as e:
        await session.rollback()
        return db_error(
            biz_code=DB_CREATE,
            errors={"message": "创建专辑失败", "detail": str(e)}
        )

@router.put("/albums/{id}")
async def update_album(id: int, album: dict, session: AsyncSession = Depends(get_session)):
    try:
        result = await session.execute(...)
        await session.commit()
        return updated(data={"id": id})
    except SQLAlchemyError as e:
        await session.rollback()
        return db_error(
            biz_code=DB_UPDATE,
            errors={"message": "更新专辑失败"}
        )
```

## 高级用法

### 1. 使用 BusinessError 异常

```python
from utils.restful import BusinessError, new_business_error
from utils.biz_code import INVALID_PWD, USER_NOT_FOUND

@router.post("/login")
async def login(username: str, password: str):
    # 方式1: 直接抛出异常
    user = get_user(username)
    if not user:
        raise BusinessError(
            biz_code=USER_NOT_FOUND,
            details={"username": username}
        )

    if not verify_password(password, user.password):
        raise BusinessError(
            biz_code=INVALID_PWD,
            details={"message": "密码错误"}
        )

    return success(data={"token": "..."})

# 方式2: 使用工厂函数
def validate_user(username: str, password: str):
    user = get_user(username)
    if not user:
        raise new_business_error(
            biz_code=USER_NOT_FOUND,
            details={"username": username}
        )
    return user
```

### 2. 全局异常处理器

在 `main.py` 中添加 BusinessError 处理器：

```python
from fastapi import FastAPI, Request
from utils.restful import BusinessError

app = FastAPI()

@app.exception_handler(BusinessError)
async def business_error_handler(request: Request, exc: BusinessError):
    """处理业务错误"""
    return exc.to_response()

# 现在任何抛出的 BusinessError 都会被自动转换为正确的响应
```

### 3. 自定义业务状态码

```python
# 在 biz_code.py 中添加新的状态码
ITEM_OUT_OF_STOCK = 4210  # 商品缺货

# 在 CODE_MESSAGES 中添加消息
CODE_MESSAGES[ITEM_OUT_OF_STOCK] = "商品库存不足"

# 使用
from utils.restful import bad_request
from utils.biz_code import ITEM_OUT_OF_STOCK

@router.post("/orders")
async def create_order(item_id: int, quantity: int):
    stock = get_stock(item_id)
    if stock < quantity:
        return bad_request(
            biz_code=ITEM_OUT_OF_STOCK,
            errors={
                "item_id": item_id,
                "requested": quantity,
                "available": stock
            }
        )
    return created(data={"order_id": "..."})
```

### 4. 与 ResponseModel 结合使用

```python
from utils.response import ResponseModel
from utils.restful import success
from typing import List

class ItemOut(BaseModel):
    id: int
    name: str

# 旧方式（仍然可用）
@router.get("/items/old", response_model=ResponseModel[List[ItemOut]])
async def get_items_old():
    items = [ItemOut(id=1, name="Item 1")]
    return ResponseModel[List[ItemOut]](data=items)

# 新方式（使用 restful.success）
@router.get("/items/new")
async def get_items_new():
    items = [{"id": 1, "name": "Item 1"}]
    return success(data=items)
```

## 响应格式对比

### 使用 restful.py (新方式)

```json
{
  "code": 0,              // 0表示成功，其他表示业务错误码
  "message": "请求成功",
  "data": {...},
  "errors": null,
  "timestamp": "2025-10-18T10:00:00+00:00"
}
```

### 使用 response.py (旧方式)

```json
{
  "code": 200,
  "message": "success",
  "data": {...}
}
```

### 错误响应 (restful.py)

```json
{
  "code": 4004, // 业务状态码
  "message": "资源不存在",
  "data": null,
  "errors": {
    "id": 999,
    "message": "找不到ID为999的资源"
  },
  "timestamp": "2025-10-18T10:00:00+00:00"
}
```

## 最佳实践

1. **成功响应使用 `success()` 系列函数**

   - `success()` - 通用成功 (200)
   - `created()` - 创建成功 (201)
   - `updated()` - 更新成功 (200)
   - `deleted()` - 删除成功 (204)

2. **错误响应使用对应的错误函数**

   - `bad_request()` - 客户端错误 (400)
   - `unauthorized()` - 未授权 (401)
   - `forbidden()` - 禁止访问 (403)
   - `not_found()` - 未找到 (404)
   - `internal_error()` - 服务器错误 (500)

3. **复杂业务逻辑使用 BusinessError 异常**

   - 可以在任何地方抛出
   - 由全局异常处理器统一处理
   - 自动转换为正确的响应格式

4. **保持业务状态码一致**
   - 使用 biz_code.py 中定义的常量
   - 不要硬编码状态码
   - 添加新状态码时更新 CODE_MESSAGES

## 迁移指南

从现有的错误处理迁移到新的 restful 工具：

```python
# 旧方式
from fastapi import HTTPException
raise HTTPException(status_code=404, detail="Song not found")

# 新方式1: 返回响应
from utils.restful import not_found
from utils.biz_code import NOT_FOUND
return not_found(biz_code=NOT_FOUND, errors={"message": "Song not found"})

# 新方式2: 抛出异常
from utils.restful import BusinessError
from utils.biz_code import NOT_FOUND
raise BusinessError(biz_code=NOT_FOUND, details={"message": "Song not found"})
```
