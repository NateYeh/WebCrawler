"""使用 NodriverCrawler 來抓取網頁數據"""

import asyncio
import platform
import time

import nodriver as uc
from data_structures import ActionT, SolutionResultT, V1RequestBase
from dbg import dbg

if platform.system() == "Windows":
    COOKIES_FILE = "X:\\windows\\cookies.dat"
else:
    COOKIES_FILE = "/app/cookies.dat"


class NodriverCrawler:
    """
    提供網頁操作相關功能的類別。
    """

    def __init__(self):
        self.browser = None
        self.solution = None

    async def get(self, req: V1RequestBase):
        """載入指定網址並取得網頁資訊。
        Args:
            req (V1RequestBase): 包含請求資訊的物件。
        Returns:
            SolutionResultT: 包含網頁資訊的結果物件。
        """
        dbg(f"get: {req.url}")

        if self.browser is None:
            browser = self.browser = await uc.start()
        else:
            browser = self.browser

        await browser.cookies.load(COOKIES_FILE)
        for attempt in range(req.retry_count + 1):
            if attempt > 1:
                dbg(f"嘗試次數: {attempt}/{req.retry_count - 1}")
            try:
                page = await browser.get(req.url)
            except Exception as e:
                msg = f"get url error: {req.url}\n{e}\n"
                dbg(msg)
                return SolutionResultT({"response": msg, "status": 500, "url": req.url})

            # 用page_size判斷頁面載入情況
            page_loaded = False
            timeout = int(req.max_timeout / 1000)
            for i in range(timeout):
                page_size = len(await page.get_content())
                dbg(f"[{i}]page size: {page_size}")
                if page_size == 39:
                    break
                if page_size > req.page_size:
                    page_loaded = True
                    break
                time.sleep(1)
            if not page_loaded:
                continue

            await self.__handle_actions(page, req.actions)

            # 取得截圖
            screenshot_base64 = ""

            # 取得網頁資訊
            solution = {
                "cookies": [],
                "headers": "",
                "response": await page.get_content(),
                "status": 200,
                "url": req.url,
                "userAgent": "",
                "screenshot_base64": screenshot_base64,
            }

            await browser.cookies.save(COOKIES_FILE)
            # 回傳網頁資訊
            return SolutionResultT(solution)

    async def __handle_actions(self, tab: uc.Tab, actions: list[ActionT]):
        """處理 actions 事件。
        Args:
            actions (list): actions 列表。
        Returns:
            str: 發生錯誤時的錯誤訊息，否則為空字串。
        """
        for action in actions:
            if action.trigger == "clickable":
                try:
                    if action.select:
                        enter_button = await tab.select(action.select, timeout=action.timeout)
                    elif action.find:
                        enter_button = await tab.find(action.find, timeout=action.timeout)
                    else:
                        return "action path is empty"
                    # 點擊連結
                    await enter_button.click()
                    dbg(f"成功點擊{action.xpath}連結")
                except asyncio.TimeoutError:
                    dbg(f"找不到{action.xpath}連結")
                except Exception as e:
                    msg = f"點擊{action.xpath}，連結失敗: {e}"
                    dbg(msg)
                    return msg
            elif action.trigger == "input":
                try:
                    if action.select:
                        enter_button = await tab.select(action.select, timeout=action.timeout)
                    elif action.find:
                        enter_button = await tab.find(action.find, timeout=action.timeout)
                    else:
                        return "action path is empty"
                    await enter_button.send_keys(action.value)
                except asyncio.TimeoutError:
                    pass
                    # dbg(f"等不到{event.xpath}連結")
                except Exception as e:
                    msg = f"等待{action.xpath}連結失敗: {e}"
                    dbg(msg)
                    return msg
            elif action.trigger == "located":
                try:
                    if action.select:
                        enter_button = await tab.select(action.select, timeout=action.timeout)
                    elif action.find:
                        enter_button = await tab.find(action.find, timeout=action.timeout)
                    else:
                        return "action path is empty"
                    # dbg(f"等到{event.xpath}連結")
                except asyncio.TimeoutError:
                    pass
                    # dbg(f"等不到{event.xpath}連結")
                except Exception as e:
                    msg = f"等待{action.xpath}連結失敗: {e}"
                    dbg(msg)
                    return msg

        return ""

    def is_subdomain(self, subdomain, domain):
        """
        檢查 subdomain 是否為 domain 的子域名
        """
        return subdomain == domain or subdomain.endswith(f".{domain}")


async def main_test():
    """測試函數"""
    url = "https://www.uaa.com/api/novel/app/novel/catalog/11302895"
    # browser = await uc.start(browser_executable_path='/usr/bin/google-chrome')
    # browser = await uc.start(browser_executable_path='/home/nate/.cache/selenium/chrome/linux64/129.0.6668.58/chrome', headless=True, sandbox=False)
    browser = await uc.start()
    print(f"get {url}")
    page = await browser.get(url)

    print(await page.get_content())


if __name__ == "__main__":
    uc.loop().run_until_complete(main_test())
