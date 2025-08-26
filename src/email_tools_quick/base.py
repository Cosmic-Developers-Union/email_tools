# -*- coding: utf-8 -*-
# Copyright (C) 2025 Cosmic-Developers-Union (CDU), All rights reserved.

"""Models Description

"""
from abc import ABC
from abc import abstractmethod
from typing import Generator

from email_tools_quick.mail import SocketParams


class BaseEmailClient(ABC):
    """Abstract base class for email clients."""

    @abstractmethod
    def login(self, socket_params: SocketParams = None):
        pass

    @abstractmethod
    def logout(self):
        pass

    @abstractmethod
    def latest(self, count: int = 3):
        pass

    def __enter__(self):
        self.login()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.logout()
        return False

    @abstractmethod
    def inbox(self, start: int = 0, end: int = -1) -> Generator:
        pass

    @abstractmethod
    def junk(self, start: int = 0, end: int = -1) -> Generator:
        pass
