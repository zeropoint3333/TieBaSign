# config.py
class Config:
    API_URLS = {
        "LIKE_URL": "http://c.tieba.baidu.com/c/f/forum/like",
        "TBS_URL": "http://tieba.baidu.com/dc/common/tbs",
        "SIGN_URL": "http://c.tieba.baidu.com/c/c/forum/sign",
    }

    HEADERS = {
        "Host": "tieba.baidu.com",
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36",
    }

    SIGN_DATA = {
        "_client_type": "2",
        "_client_version": "9.7.8.0",
        "_phone_imei": "000000000000000",
        "model": "MI+5",
        "net_type": "1",
    }

    HTTP_SETTINGS = {
        "TIMEOUT": 5,
        "RETRY_TIMES": 3,
        "RETRY_DELAY": 1,
        "POOL_CONNECTIONS": 10,
        "POOL_MAXSIZE": 20,
    }

    THREAD_SETTINGS = {
        "MAX_WORKERS": 20,
        "MIN_DELAY": 1,
        "MAX_DELAY": 3,
    }

    ERROR_CODES = {
        "160002": "已签到",
        "0": "签到成功",
        "1102": "签到失败(贴吧未开通签到或签到过快)",
        "1107": "今天已签满100个贴吧",
        "4010": "账号异常需绑定手机",
        "340011": "重复签到",
        "340008": "在黑名单中",
        "340006": "贴吧目录出问题",
        "340005": "贴吧不存在",
        "110001": "未登录",
        "1": "用户未登录",
        "unknown": "未知错误",
    }

    CRITICAL_ERRORS = ["1107", "4010"]

    SUCCESS_CODES = ["160002", "0"]
