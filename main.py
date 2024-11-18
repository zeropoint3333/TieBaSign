# -*- coding:utf-8 -*-
import os
import requests
import hashlib
import time
import copy
import logging
import random
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# API_URL
LIKIE_URL = "http://c.tieba.baidu.com/c/f/forum/like"
TBS_URL = "http://tieba.baidu.com/dc/common/tbs"
SIGN_URL = "http://c.tieba.baidu.com/c/c/forum/sign"

ENV = os.environ

HEADERS = {
    "Host": "tieba.baidu.com",
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.71 Safari/537.36",
}
SIGN_DATA = {
    "_client_type": "2",
    "_client_version": "9.7.8.0",
    "_phone_imei": "000000000000000",
    "model": "MI+5",
    "net_type": "1",
}

# VARIABLE NAME
COOKIE = "Cookie"
BDUSS = "BDUSS"
EQUAL = "="
EMPTY_STR = ""
TBS = "tbs"
PAGE_NO = "page_no"
ONE = "1"
TIMESTAMP = "timestamp"
DATA = "data"
FID = "fid"
SIGN_KEY = "tiebaclient!!!"
UTF8 = "utf-8"
SIGN = "sign"
KW = "kw"

s = requests.Session()
adapter = requests.adapters.HTTPAdapter(
    pool_connections=20,  # 连接池的连接数
    pool_maxsize=20,  # 连接池的最大数量
    max_retries=3,  # 最大重试次数
    pool_block=False,  # 连接池满时不阻塞
)
s.mount("http://", adapter)
s.mount("https://", adapter)


def get_tbs(bduss):
    logger.info("获取tbs开始")
    headers = copy.copy(HEADERS)
    headers.update({COOKIE: EMPTY_STR.join([BDUSS, EQUAL, bduss])})
    try:
        tbs = s.get(url=TBS_URL, headers=headers, timeout=5).json()[TBS]
    except Exception as e:
        logger.error("获取tbs出错: %s", e)
        logger.info("重新获取tbs开始")
        tbs = s.get(url=TBS_URL, headers=headers, timeout=5).json()[TBS]
    logger.info("获取tbs结束")
    return tbs


def get_favorite(bduss):
    logger.info("获取关注的贴吧开始")
    returnData = {}
    i = 1
    data = {
        "BDUSS": bduss,
        "_client_type": "2",
        "_client_id": "wappc_1534235498291_488",
        "_client_version": "9.7.8.0",
        "_phone_imei": "000000000000000",
        "from": "1008621y",
        "page_no": "1",
        "page_size": "200",
        "model": "MI+5",
        "net_type": "1",
        "timestamp": str(int(time.time())),
        "vcode_tag": "11",
    }
    data = encodeData(data)
    try:
        res = s.post(url=LIKIE_URL, data=data, timeout=5).json()
    except Exception as e:
        logger.error("获取关注的贴吧出错: %s", e)
        return []
    returnData = res
    if "forum_list" not in returnData:
        returnData["forum_list"] = []
    if res["forum_list"] == []:
        return {"gconforum": [], "non-gconforum": []}
    if "non-gconforum" not in returnData["forum_list"]:
        returnData["forum_list"]["non-gconforum"] = []
    if "gconforum" not in returnData["forum_list"]:
        returnData["forum_list"]["gconforum"] = []
    while "has_more" in res and res["has_more"] == "1":
        i += 1
        data = {
            "BDUSS": bduss,
            "_client_type": "2",
            "_client_id": "wappc_1534235498291_488",
            "_client_version": "9.7.8.0",
            "_phone_imei": "000000000000000",
            "from": "1008621y",
            "page_no": str(i),
            "page_size": "200",
            "model": "MI+5",
            "net_type": "1",
            "timestamp": str(int(time.time())),
            "vcode_tag": "11",
        }
        data = encodeData(data)
        try:
            res = s.post(url=LIKIE_URL, data=data, timeout=5).json()
        except Exception as e:
            logger.error("获取关注的贴吧出错: %s", e)
            continue
        if "forum_list" not in res:
            continue
        if "non-gconforum" in res["forum_list"]:
            returnData["forum_list"]["non-gconforum"].append(
                res["forum_list"]["non-gconforum"]
            )
        if "gconforum" in res["forum_list"]:
            returnData["forum_list"]["gconforum"].append(res["forum_list"]["gconforum"])

    t = []
    for i in returnData["forum_list"]["non-gconforum"]:
        if isinstance(i, list):
            t.extend(i)
        else:
            t.append(i)
    for i in returnData["forum_list"]["gconforum"]:
        if isinstance(i, list):
            t.extend(i)
        else:
            t.append(i)
    logger.info("获取关注的贴吧结束")
    return t


def encodeData(data):
    s = EMPTY_STR
    keys = data.keys()
    for i in sorted(keys):
        s += i + EQUAL + str(data[i])
    sign = hashlib.md5((s + SIGN_KEY).encode(UTF8)).hexdigest().upper()
    data.update({SIGN: str(sign)})
    return data


def client_sign(bduss, tbs, fid, kw):
    logger.info("开始签到贴吧：" + kw)
    data = copy.copy(SIGN_DATA)
    data.update(
        {BDUSS: bduss, FID: fid, KW: kw, TBS: tbs, TIMESTAMP: str(int(time.time()))}
    )
    data = encodeData(data)
    res = s.post(url=SIGN_URL, data=data, timeout=5).json()
    return res


def sign_one_bar(args):
    """单个贴吧签到函数"""
    bduss, tbs, bar = args
    try:
        time.sleep(random.randint(1, 3))  # 稍微降低延迟，因为开启了多线程
        res = client_sign(bduss, tbs, bar["id"], bar["name"])
        status = "已签到" if res.get("error_code") == "160002" else "未知"
        logger.info(f'贴吧：{bar["name"]} 签到状态：{status}')
        return res
    except Exception as e:
        logger.error(f'贴吧：{bar["name"]} 签到异常：{str(e)}')
        return None


def main():
    if "BDUSS" not in ENV:
        logger.error("未配置BDUSS")
        return

    b = ENV["BDUSS"].split("#")
    # 设置线程池最大线程数
    max_workers = min(20, os.cpu_count() * 5)  # 根据CPU核心数设置，最大20个线程

    for n, bduss in enumerate(b):
        logger.info("开始签到第%s个用户%s", n, bduss)
        tbs = get_tbs(bduss)
        favorites = get_favorite(bduss)

        # 使用线程池进行签到
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # 准备签到参数
            sign_args = [(bduss, tbs, bar) for bar in favorites]
            # 提交所有任务
            futures = [executor.submit(sign_one_bar, args) for args in sign_args]
            # 等待所有任务完成
            concurrent.futures.wait(futures)

        logger.info("完成第%s个用户签到", n)

    logger.info("所有用户签到结束")


if __name__ == "__main__":
    main()
