# -*- coding: utf-8 -*-
# Copyright (C) 2025 Cosmic-Developers-Union (CDU), All rights reserved.

"""Models Description

"""
import dataclasses
import imaplib
import re
from typing import Optional
from typing import Union

from loguru import logger

from .error import EmailConnectionError
from .error import FetchMailError
from .error import NoSuchMailBoxError
from .mail import IMAP4Client
from .mail import IMAP4SSLClient
from .mail import SocketParams
from .utils import parse_msg


@dataclasses.dataclass
class MailBoxMap:
    INBOX: str = "INBOX"
    Sent: str = "Sent"
    Trash: str = "Trash"
    Junk: str = "Junk"
    Drafts: str = "Drafts"
    Archive: str = "Archive"

    @property
    def send(self):
        return "发件箱"

    @property
    def trash(self):
        return "回收站"

    @property
    def junk(self):
        return "垃圾箱"

    @property
    def drafts(self):
        return "草稿箱"

    @property
    def archive(self):
        return "归档箱"


class CommonClient:
    INBOX = "INBOX"
    JUNK = "Junk", "Spam"

    def __init__(
            self,
            address: str,
            password: str,
            host: str = None,
            ssl: bool = True,
    ):
        self.address = address
        self.password = password
        self._host = host
        self.ssl = ssl
        self.client: Optional[Union[IMAP4Client, IMAP4SSLClient]] = None
        self.mbox_map = MailBoxMap()

    def mailboxes(self) -> MailBoxMap:
        status, mailboxes = self.client.list(pattern="%")
        if status == "OK":
            for mbox in mailboxes:
                mbox: bytes
                try:
                    mbox: str = mbox.decode(encoding="utf-8")
                except UnicodeDecodeError:
                    logger.warning("邮箱名称解码失败，尝试使用 IMAP UTF-7 解码。")
                    continue
                mbox_ = re.search(r"\((.*)\) \"(.+)\" \"?([^\"]*)", mbox)
                flags = mbox_.group(1).strip(" ")
                nane = mbox_.group(3)
                for flag in ["\Sent", "\Trash", "\Junk", "\Drafts", "\Archive"]:
                    if flag in flags:
                        if flag == "\Sent":
                            self.mbox_map.Sent = nane
                        elif flag == "\Trash":
                            self.mbox_map.Trash = nane
                        elif flag == "\Junk":
                            self.mbox_map.Junk = nane
                        elif flag == "\Drafts":
                            self.mbox_map.Drafts = nane
                        elif flag == "\Archive":
                            self.mbox_map.Archive = nane
                        else:
                            logger.warning("未知邮箱标志: {flag}")
        return self.mbox_map

    def ids(self, mbox: str, *criteria) -> list[bytes]:
        self.select(mbox)
        return self.search(*criteria)

    def search(self, *criteria):
        status, messages = self.client.uid('search', None, *criteria)
        if status != 'OK':
            return []
        return messages[0].split()

    @property
    def host(self):
        if self._host is None:
            return self._get_host(self.address.split("@")[-1])
        return self._host

    @staticmethod
    def _get_host(qname: str) -> str:
        from dns.resolver import resolve
        from dns.exception import DNSException
        try:
            mx_records = resolve(qname, 'MX')
            return str(mx_records[0].exchange).rstrip('.')
        except DNSException as e:
            raise ValueError(f"DNS resolution failed for {qname}: {e}")

    def login(self, socket_params: SocketParams = None):
        if self.ssl:
            self.client = IMAP4SSLClient(
                host=self.host,
                socket_params=socket_params,
            )
        else:
            self.client = IMAP4Client(
                host=self.host,
                socket_params=socket_params,
            )
        self.client.login(self.address, self.password)

    def logout(self):
        try:
            if self.client:
                self.client.logout()
                self.client = None
        except (imaplib.IMAP4.abort, imaplib.IMAP4.error) as e:
            raise EmailConnectionError(f"{e}")

    def _query(self, folder: str, x='ALL'):
        status, message = self.client.select(folder)
        if status != 'OK':
            message = message[0]
            if message == b"No such mailbox":
                raise NoSuchMailBoxError(f"邮箱 {folder} 不存在或无法访问。请检查邮箱名称是否正确。")
            logger.warning(message)
            return []
        status, messages = self.client.uid('search', None, x)
        if status != 'OK':
            print(message)
            return []
        return messages[0].split()

    def select(self, folder: str):
        logger.info(f"select {folder}")
        status, msg = self.client.select(folder)
        if status != "OK":
            raise NoSuchMailBoxError(f"选择邮箱失败: {status}, {msg}")

    def fetch(self, mid: bytes):
        status, msg_data = self.client.uid('fetch', mid, '(RFC822)')
        if status != "OK":
            raise FetchMailError(f"获取邮件失败: {status}")
        return parse_msg(msg_data)
