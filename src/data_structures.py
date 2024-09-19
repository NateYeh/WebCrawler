"""Dataclasses for defining API request and response formats."""

import time

VERSION = "1.0.0"
DEFAULT_URL = "https://www.google.com/"


class SolutionResultT:
    """Dataclass for storing solution result."""

    def __init__(self, _dict=None):
        if _dict is None:
            _dict = {}
        self.url: str = None
        self.status: int = None
        self.headers: list = None
        self.response: str = None
        self.cookies: list = None
        self.user_agent: str = None
        self.screenshot_base64: str = None
        self.__dict__.update(_dict)

    def __repr__(self):
        return str(self.__dict__)

    def __str__(self):
        return str(self.__dict__)


class ActionT:
    """Dataclass for storing event information."""

    def __init__(self, _dict=None):
        if _dict is None:
            _dict = {}
        self.trigger: str = ""
        self.xpath: str = ""
        self.find: str = ""
        self.select: str = ""
        self.value: str = ""
        self.timeout: int = 10
        self.__dict__.update(_dict)

    def __repr__(self):
        return str(self.__dict__)

    def __str__(self):
        return str(self.__dict__)


class V1RequestBase:
    """Base class for V1 requests."""

    def __init__(self, _dict):
        self.url: str = DEFAULT_URL
        self.cookies: list = []
        self.retry_count: int = 3
        self.page_size: int = 100
        self.max_timeout: int = 60000
        self.screenshot: bool = False
        self.__dict__.update(_dict)
        self.actions = [ActionT(action) for action in self.actions]

    def __repr__(self):
        return str(self.__dict__)

    def __str__(self):
        return str(self.__dict__)


class V1ResponseBase:
    """Base class for V1 responses."""

    def __init__(self, _dict=None):
        if _dict is None:
            _dict = {}
        self.status: str = "ok"
        self.message: str = None
        self.start_timestamp: int = int(time.time() * 1000)
        self.end_timestamp: int = int(time.time() * 1000)
        self.version: str = VERSION
        self.solution: SolutionResultT = None

        self.__dict__.update(_dict)
        if self.solution is not None:
            self.solution = SolutionResultT(self.solution)

    def update(self, _dict):
        """更新資料"""
        self.status: str = "ok"
        self.message: str = None
        self.start_timestamp: int = int(time.time() * 1000)
        self.end_timestamp: int = int(time.time() * 1000)
        self.version: str = VERSION
        self.solution: SolutionResultT = None

        self.__dict__.update(_dict)
        if self.solution is not None:
            self.solution = SolutionResultT(self.solution)

    def __repr__(self):
        return str(self.__dict__)

    def __str__(self):
        return str(self.__dict__)
