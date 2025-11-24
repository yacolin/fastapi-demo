"""
Business Code Definitions
业务状态码定义
"""
from enum import Enum


class BizCode(Enum):
    """
    业务状态码枚举
    格式: (code, message, http_status)
    """
    
    # ----------------------------
    # 成功状态码 (2000-2999)
    # ----------------------------
    OK = (2000, "请求成功", 200)
    CREATED = (2001, "创建成功", 201)
    NO_CONTENT = (2002, "操作执行成功", 204)
    ACCEPTED = (2003, "请求已被接受", 202)
    DELETED = (2004, "删除成功", 204)
    UPDATED = (2005, "更新成功", 200)

    # ----------------------------
    # 客户端错误 (4000-4999)
    # ----------------------------
    
    # 通用客户端错误
    BAD_REQUEST = (4000, "无效的请求参数", 400)
    UNAUTHORIZED = (4001, "身份验证失败", 401)
    FORBIDDEN = (4003, "没有访问权限", 403)
    NOT_FOUND = (4004, "资源不存在", 404)

    # 参数校验错误
    INVALID_PWD = (4100, "密码错误", 400)
    INVALID_PAGE = (4101, "无效的分页参数", 400)
    INVALID_PRICE = (4102, "无效的价格参数", 400)
    MISSING_ID = (4103, "缺少ID参数", 400)
    MISSING_NAME = (4104, "缺少Name参数", 400)

    # 数据错误
    NO_DATA = (4200, "数据不存在", 404)

    # 令牌错误
    TK_GEN = (4300, "生成token失败", 401)
    ACCESS_TK_GEN = (4301, "生成AccessToken失败", 401)
    REFRESH_TK_GEN = (4302, "生成RefreshToken失败", 401)
    TK_INVALID = (4303, "无效的token", 401)
    TK_EXPIRED = (4304, "token已过期", 401)
    TK_NOT_FOUND = (4305, "token不存在", 401)
    TK_FORMAT = (4306, "token格式错误", 401)
    TK_SIGN = (4307, "token签名错误", 401)
    TK_CLAIMS = (4308, "token解析错误", 401)
    TK_USER_ID = (4309, "token中缺少user_id", 401)
    TK_USER_NAME = (4310, "token中缺少user_name", 401)
    TK_AUDIENCE = (4311, "token受众错误", 401)

    # ----------------------------
    # 服务器错误 (5000-5999)
    # ----------------------------
    
    # 通用服务器错误
    ERR_INTERNAL = (5000, "服务器内部错误", 500)

    # 数据库错误
    DB_QUERY = (5100, "数据查询失败", 500)
    DB_COUNT = (5101, "数据统计失败", 500)
    DB_DELETE = (5102, "数据库删除失败", 500)
    DB_UPDATE = (5103, "数据库更新失败", 500)
    DB_CREATE = (5104, "数据库创建失败", 500)
    DB_DUP = (5105, "数据重复冲突", 500)
    USER_NOT_FOUND = (5106, "用户不存在", 500)

    def __init__(self, code, message, http_status):
        self._value_ = code
        self.message = message
        self.http_status = http_status

    @property
    def code(self):
        return self._value_


def get_message(biz_code: int) -> str:
    """
    获取业务状态码对应的消息
    """
    try:
        return BizCode(biz_code).message
    except ValueError:
        return "未知错误"


def get_http_status(biz_code: int) -> int:
    """
    根据业务状态码获取对应的HTTP状态码
    """
    try:
        return BizCode(biz_code).http_status
    except ValueError:
        return 500
