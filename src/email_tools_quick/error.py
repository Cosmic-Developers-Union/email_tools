# -*- coding: utf-8 -*-
# Copyright (C) 2025 Cosmic-Developers-Union (CDU), All rights reserved.

"""Models Description

"""


class BaseEmailError(Exception):
    pass


class NoSuchMailBoxError(Exception):
    """Exception raised when the specified mailbox does not exist."""

    def __init__(self, message: str = "Mailbox does not exist."):
        self.message = message
        super().__init__(self.message)


class FetchMailError(BaseEmailError):
    pass


class BadEmailError(Exception):
    """Exception raised for errors in the email format."""

    def __init__(self, message: str = "Invalid email format."):
        self.message = message
        super().__init__(self.message)


class EmailConnectionError(Exception):
    """Exception raised for errors in the email connection."""

    def __init__(self, message: str = "Failed to connect to the email server."):
        self.message = message
        super().__init__(self.message)
