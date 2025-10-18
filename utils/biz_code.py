"""
Business Code Definitions
业务状态码定义
"""

# ----------------------------
# 成功状态码 (2000-2999)
# ----------------------------
OK = 2000
CREATED = 2001
NO_CONTENT = 2002
ACCEPTED = 2003
DELETED = 2004
UPDATED = 2005

# ----------------------------
# 客户端错误 (4000-4999)
# ----------------------------

# 通用客户端错误 (4000-4009)
BAD_REQUEST = 4000      # 无效的请求参数
UNAUTHORIZED = 4001     # 身份验证失败
FORBIDDEN = 4003        # 没有访问权限
NOT_FOUND = 4004        # 资源不存在

# 参数校验错误 (4100-4199)
INVALID_PWD = 4100      # 密码错误
INVALID_PAGE = 4101     # 无效的分页参数
INVALID_PRICE = 4102    # 无效的价格参数
MISSING_ID = 4103       # 缺少ID参数
MISSING_NAME = 4104     # 缺少Name参数

# 数据错误 (4200-4299)
NO_DATA = 4200          # 数据不存在

# 令牌错误 (4300-4399)
TK_GEN = 4300           # 生成token失败
ACCESS_TK_GEN = 4301    # 生成AccessToken失败
REFRESH_TK_GEN = 4302   # 生成RefreshToken失败
TK_INVALID = 4303       # 无效的token
TK_EXPIRED = 4304       # token已过期
TK_NOT_FOUND = 4305     # token不存在
TK_FORMAT = 4306        # token格式错误
TK_SIGN = 4307          # token签名错误
TK_CLAIMS = 4308        # token解析错误
TK_USER_ID = 4309       # token中缺少user_id
TK_USER_NAME = 4310     # token中缺少user_name
TK_AUDIENCE = 4311      # token受众错误

# ----------------------------
# 服务器错误 (5000-5999)
# ----------------------------

# 通用服务器错误 (5000-5009)
ERR_INTERNAL = 5000     # 服务器内部错误

# 数据库错误 (5100-5199)
DB_QUERY = 5100         # 数据查询失败
DB_COUNT = 5101         # 数据统计失败
DB_DELETE = 5102        # 数据库删除失败
DB_UPDATE = 5103        # 数据库更新失败
DB_CREATE = 5104        # 数据库创建失败
DB_DUP = 5105           # 数据重复冲突
USER_NOT_FOUND = 5106   # 用户不存在

# ----------------------------
# 状态码映射表
# ----------------------------
CODE_MESSAGES = {
    # 成功状态码
    OK: "请求成功",
    CREATED: "创建成功",
    NO_CONTENT: "操作执行成功",
    ACCEPTED: "请求已被接受",
    DELETED: "删除成功",
    UPDATED: "更新成功",
    
    # 客户端错误
    BAD_REQUEST: "无效的请求参数",
    UNAUTHORIZED: "身份验证失败",
    FORBIDDEN: "没有访问权限",
    NOT_FOUND: "资源不存在",
    INVALID_PWD: "密码错误",
    INVALID_PRICE: "无效的价格参数",
    INVALID_PAGE: "无效的分页参数",
    MISSING_ID: "缺少ID参数",
    MISSING_NAME: "缺少Name参数",
    NO_DATA: "数据不存在",
    
    # 令牌错误
    TK_GEN: "生成token失败",
    ACCESS_TK_GEN: "生成AccessToken失败",
    REFRESH_TK_GEN: "生成RefreshToken失败",
    TK_INVALID: "无效的token",
    TK_EXPIRED: "token已过期",
    TK_NOT_FOUND: "token不存在",
    TK_FORMAT: "token格式错误",
    TK_SIGN: "token签名错误",
    TK_CLAIMS: "token解析错误",
    TK_USER_ID: "token中缺少user_id",
    TK_USER_NAME: "token中缺少user_name",
    TK_AUDIENCE: "token受众错误",
    
    # 服务器错误
    ERR_INTERNAL: "服务器内部错误",
    DB_QUERY: "数据查询失败",
    DB_COUNT: "数据统计失败",
    DB_DELETE: "数据库删除失败",
    DB_UPDATE: "数据库更新失败",
    DB_CREATE: "数据库创建失败",
    DB_DUP: "数据重复冲突",
    USER_NOT_FOUND: "用户不存在",
}


def get_message(biz_code: int) -> str:
    """
    获取业务状态码对应的消息
    
    Args:
        biz_code: 业务状态码
        
    Returns:
        对应的消息文本，如果找不到则返回默认消息
    """
    return CODE_MESSAGES.get(biz_code, "未知错误")


def get_http_status(biz_code: int) -> int:
    """
    根据业务状态码获取对应的HTTP状态码
    
    Args:
        biz_code: 业务状态码
        
    Returns:
        HTTP状态码
    """
    if 2000 <= biz_code < 3000:
        # 成功状态码映射
        mapping = {
            OK: 200,
            CREATED: 201,
            NO_CONTENT: 204,
            ACCEPTED: 202,
            DELETED: 204,
            UPDATED: 200,
        }
        return mapping.get(biz_code, 200)
    elif 4000 <= biz_code < 5000:
        # 客户端错误映射
        if biz_code == UNAUTHORIZED or (4300 <= biz_code < 4400):
            return 401
        elif biz_code == FORBIDDEN:
            return 403
        elif biz_code == NOT_FOUND or biz_code == NO_DATA:
            return 404
        else:
            return 400
    elif 5000 <= biz_code < 6000:
        # 服务器错误
        return 500
    else:
        return 500
