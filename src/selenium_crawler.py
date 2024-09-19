"""使用 SeleniumCrawler 來抓取網頁數據"""

import base64
import time
from urllib.parse import urlparse

from data_structures import ActionT, SolutionResultT, V1RequestBase
from dbg import dbg
from selenium import webdriver as uc
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class SeleniumCrawler:
    """
    提供網頁操作相關功能的類別。
    """

    def __init__(self):
        self.driver = None
        self.__start_driver()
        self.show_chrome_versions()

    def get(self, req: V1RequestBase):
        """載入指定網址並取得網頁資訊。
        Args:
            req (V1RequestBase): 包含請求資訊的物件。
        Returns:
            SolutionResultT: 包含網頁資訊的結果物件。
        """
        timeout = int(req.max_timeout / 1000)
        dbg(f"get: {req.url}")
        for attempt in range(req.retry_count + 1):
            if attempt > 1:
                dbg(f"嘗試次數: {attempt}/{req.retry_count - 1}")
            try:
                # 載入目標URL
                self.driver.get(req.url)
            except Exception as e:
                self.__start_driver()
                msg = f"get url error: {req.url}\n{e}\n"
                dbg(msg)
                return SolutionResultT({"response": msg, "status": 500, "url": req.url})

            # 等待頁面載入完成
            WebDriverWait(self.driver, timeout).until(EC.presence_of_element_located((By.TAG_NAME, "html")))

            self.__handle_cookies(req.cookies)

            # 用page_size判斷頁面載入情況
            page_loaded = False
            for i in range(timeout):
                page_size = len(self.driver.page_source)
                dbg(f"[{i}]page size: {page_size}")
                if page_size == 39:
                    break
                if page_size > req.page_size:
                    page_loaded = True
                    break
                time.sleep(1)
            if not page_loaded:
                continue
            msg = self.__handle_actions(req.actions)
            if msg:
                return SolutionResultT({"response": msg, "status": 500, "url": req.url})

            # 取得截圖
            screenshot_base64 = ""
            if req.screenshot:
                screenshot = self.driver.get_screenshot_as_png()
                screenshot_base64 = base64.b64encode(screenshot).decode("utf-8")

            # 取得網頁資訊
            solution = {
                "cookies": self.driver.get_cookies(),
                "headers": "",
                "response": self.driver.page_source,
                "status": 200,
                "url": req.url,
                "userAgent": self.driver.execute_script("return navigator.userAgent"),
                "screenshot_base64": screenshot_base64,
            }

            # 回傳網頁資訊
            return SolutionResultT(solution)
        msg = "達到最大重試次數，放棄操作"
        dbg(msg)
        return SolutionResultT({"response": msg, "status": 500, "url": req.url})

    def __start_driver(self):
        """重新啟動瀏覽器。"""
        if self.driver:
            self.driver.quit()
        options = uc.ChromeOptions()
        options.add_argument("--headless")  # 設定無頭模式
        options.add_argument("--no-sandbox")  # 禁用沙箱模式
        options.add_argument("--window-size=1920,1080")  # 設置窗口大小，避免部分網站因窗口過小導致元素加載異常
        options.add_argument("--disable-setuid-sandbox")  # 禁用沙箱，提升容器環境下的穩定性
        options.add_argument("--disable-dev-shm-usage")  # 禁用共享內存，提升容器環境下的穩定性
        options.add_argument("--ignore-certificate-errors")  # 忽略證書錯誤，避免因證書問題導致爬蟲中斷
        options.add_argument("--ignore-ssl-errors")  # 忽略證書錯誤，避免因證書問題導致爬蟲中斷
        # options.add_argument("--auto-open-devtools-for-tabs")  # 自動打開開發者工具，方便調試
        self.driver = uc.Chrome(options=options)

    def __handle_actions(self, actions: list[ActionT]):
        """處理 actions 事件。
        Args:
            actions (list): actions 列表。
        Returns:
            str: 發生錯誤時的錯誤訊息，否則為空字串。
        """
        for action in actions:
            if action.trigger == "clickable":
                try:
                    # 尋找XPATH的連結
                    enter_button = WebDriverWait(self.driver, action.timeout).until(EC.element_to_be_clickable((By.XPATH, action.xpath)))
                    # dbg(f"enter_button type: {type(enter_button)}")
                    # 點擊連結
                    enter_button.click()
                    dbg(f"成功點擊{action.xpath}連結")
                except TimeoutException:
                    dbg(f"找不到{action.xpath}連結")
                except Exception as e:
                    msg = f"點擊{action.xpath}，連結失敗: {e}"
                    dbg(msg)
                    self.__start_driver()
                    return msg
            elif action.trigger == "located":
                try:
                    # 尋找XPATH的連結
                    enter_button = WebDriverWait(self.driver, action.timeout).until(EC.presence_of_element_located((By.XPATH, action.xpath)))
                    # dbg(f"等到{event.xpath}連結")
                except TimeoutException:
                    pass
                    # dbg(f"等不到{event.xpath}連結")
                except Exception as e:
                    msg = f"等待{action.xpath}連結失敗: {e}"
                    dbg(msg)
                    self.__start_driver()
                    return msg
        return ""

    def __handle_cookies(self, cookies):
        """處理 cookies 設定。
        Args:
            cookies (list): cookies 列表。
        """
        # 載入cookies
        for cookie in cookies:
            # 獲取 cookie 的 domain 屬性
            cookie_domain = cookie.get("domain")
            # 獲取當前網站域名
            current_domain = urlparse(self.driver.current_url).netloc
            # 檢查 cookie domain 是否與當前域名匹配
            if cookie_domain:
                if not self.is_subdomain(cookie_domain, current_domain):
                    # dbg(f"跳過域名不匹配的 cookie: {cookie}")
                    continue

            # 獲取 SameSite 屬性，如果不存在則默認為 None
            same_site = cookie.get("sameSite", None)
            # 調整 SameSite 值以匹配允許的選項
            if same_site is not None and same_site.lower() not in ["Strict", "Lax", "None"]:
                if same_site.lower() == "strict" or same_site.lower() == "no_restriction":
                    cookie["sameSite"] = "Strict"
                elif same_site.lower() == "lax":
                    cookie["sameSite"] = "Lax"
                elif same_site.lower() == "none" or same_site.lower() == "unspecified":
                    cookie["sameSite"] = "None"
                else:
                    dbg(f"跳過 SameSite 值不被支持的 cookie: {same_site}")
                    continue  # 跳過到下一個 cookie
            # dbg(f"add_cookie: {cookie.get('name')}: {cookie.get('value')}")
            self.driver.add_cookie(cookie)
        self.driver.refresh()
        WebDriverWait(self.driver, 60).until(EC.presence_of_element_located((By.TAG_NAME, "html")))

    def show_chrome_versions(self):
        """顯示 Chrome 瀏覽器和 ChromeDriver 的版本信息。"""
        chrome_version = self.driver.capabilities["browserVersion"]
        chromedriver_version = self.driver.capabilities["chrome"]["chromedriverVersion"].split(" ")[0]
        dbg(f"chrome_version:{chrome_version} chromedriver_version:{chromedriver_version}")

    def is_subdomain(self, subdomain, domain):
        """
        檢查 subdomain 是否為 domain 的子域名
        """
        return subdomain == domain or subdomain.endswith(f".{domain}")


def main_test():
    """測試函數"""
    url = "https://nate.idv.tw:8443/"

    options = uc.ChromeOptions()
    options.add_argument("--headless")  # 設定無頭模式
    options.add_argument("--no-sandbox")  # 禁用沙箱模式
    options.add_argument("--window-size=1920,1080")  # 設置窗口大小，避免部分網站因窗口過小導致元素加載異常
    options.add_argument("--disable-setuid-sandbox")  # 禁用沙箱，提升容器環境下的穩定性
    options.add_argument("--disable-dev-shm-usage")  # 禁用共享內存，提升容器環境下的穩定性
    options.add_argument("--ignore-certificate-errors")  # 忽略證書錯誤，避免因證書問題導致爬蟲中斷
    options.add_argument("--ignore-ssl-errors")  # 忽略證書錯誤，避免因證書問題導致爬蟲中斷
    # options.add_argument("--auto-open-devtools-for-tabs")  # 自動打開開發者工具，方便調試
    driver = uc.Chrome(options=options)

    chrome_version = driver.capabilities["browserVersion"]
    chromedriver_version = driver.capabilities["chrome"]["chromedriverVersion"].split(" ")[0]
    dbg(f"chrome_version:{chrome_version} chromedriver_version:{chromedriver_version}")


if __name__ == "__main__":
    main_test()
