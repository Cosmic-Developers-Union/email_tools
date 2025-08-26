# -*- coding: utf-8 -*-
# Copyright (C) 2025 Cosmic-Developers-Union (CDU), All rights reserved.

"""Models Description

"""
from abc import ABC, abstractmethod

from email_tools_quick.mail import SocketParams


class BaseEmailClient(ABC):
    """Abstract base class for email clients."""

    @abstractmethod
    def login(self, socket_params: SocketParams = None):
        pass
