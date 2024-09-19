"""
這個 Python 腳本使用 FastAPI 建立了一個 Web API，用來抓取網頁數據。

API 提供一個 `/v1` 端點，接受 POST 請求，請求體需包含抓取目標網頁的相關資訊。
伺服器會使用 Crawler 抓取指定網頁的數據，並將結果以 JSON 格式返回。

程式碼使用了線程鎖，確保多線程環境下對 Crawler 的安全訪問。
"""

import json
import threading
import time

from data_structures import V1RequestBase, V1ResponseBase
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from selenium_crawler import SeleniumCrawler
from nodriver_crawler import NodriverCrawler

# 建立 FastAPI 應用程式實例
app = FastAPI()
nodcrawl = NodriverCrawler()
selcrawl = SeleniumCrawler()
crawl_lock = threading.Lock()


# 定義根路由
@app.api_route("/", methods=["GET", "POST"])
async def root():
    """
    根路由處理函式，回應預設的 V1ResponseBase 物件。
    """
    return V1ResponseBase()

@app.post("/v1")
async def api_v1(request: Request):
    """
    處理 `/v1` 路由的 POST 請求，使用 SeleniumCrawler 抓取網頁。

    Args:
        request (Request): FastAPI 請求物件。

    Returns:
        V1ResponseBase: 包含抓取結果的回應物件。
    """
    try:
        # 從請求體中讀取 JSON 資料
        data_str = await request.body()
        data = json.loads(data_str.decode())

        # 建立請求物件
        req = V1RequestBase(data)

        # 建立回應物件
        res = V1ResponseBase()

        with crawl_lock:  # 獲取鎖
            # 使用 SeleniumCrawler 抓取網頁
            res.solution = selcrawl.get(req)

        # 設定回應時間戳
        res.end_timestamp = int(time.time() * 1000)

        # 回傳回應物件
        return res
    except json.JSONDecodeError:
        # 如果請求體不是有效的 JSON 資料，則回傳錯誤訊息
        return JSONResponse({"error": "無效的 JSON 資料"}, status_code=400)


@app.post("/v2")
async def api_v2(request: Request):
    """
    處理 `/v2` 路由的 POST 請求，使用 NodriverCrawler 抓取網頁。

    Args:
        request (Request): FastAPI 請求物件。

    Returns:
        V1ResponseBase: 包含抓取結果的回應物件。
    """
    try:
        # 從請求體中讀取 JSON 資料
        data_str = await request.body()
        data = json.loads(data_str.decode())

        # 建立請求物件
        req = V1RequestBase(data)

        # 建立回應物件
        res = V1ResponseBase()

        with crawl_lock:  # 獲取鎖
            # 使用 NodriverCrawler 抓取網頁
            res.solution = await nodcrawl.get(req)

        # 設定回應時間戳
        res.end_timestamp = int(time.time() * 1000)

        # 回傳回應物件
        return res
    except json.JSONDecodeError:
        # 如果請求體不是有效的 JSON 資料，則回傳錯誤訊息
        return JSONResponse({"error": "無效的 JSON 資料"}, status_code=400)


# 運行 FastAPI 開發伺服器
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
