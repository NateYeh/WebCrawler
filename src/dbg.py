"""一個用於偵錯的輔助函數，它會印出呼叫函數的資訊和傳入的參數。"""

import inspect
import os
import datetime


def dbg(*args):
    """一個用於偵錯的輔助函數，它會印出呼叫函數的資訊和傳入的參數。

    Args:
        *args: 要印出的變數參數。
    """

    # 取得當前的堆疊框架
    frame = inspect.currentframe()
    # 取得呼叫者的堆疊框架
    caller_frame = frame.f_back
    # 取得檔名和行號
    file_name = caller_frame.f_code.co_filename
    file_name = os.path.basename(file_name)
    line_number = caller_frame.f_lineno
    # 取得呼叫者函數名稱
    function_name = caller_frame.f_code.co_name

    # 取得當前的日期時間
    current_datetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 建構偵錯訊息
    debug_info = f"[+][{current_datetime}][{file_name}:{line_number} - {function_name}] " + " ".join(map(str, args)) + "\n"

    # 印出偵錯訊息
    print(debug_info, end='')
