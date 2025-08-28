# -*- coding: utf-8 -*-
# Copyright (C) 2025 Cosmic-Developers-Union (CDU), All rights reserved.

"""Models Description

"""
from typing import Callable

from curl_cffi import requests
from loguru import logger

from email_tools_quick.common import CommonClient
from email_tools_quick.mail import IMAP4SSLClient
from email_tools_quick.mail import IMAP4_SSL_PORT
from email_tools_quick.mail import SocketParams


class MSClient(CommonClient):
    HOST: str = "outlook.office365.com"
    PORT: int = IMAP4_SSL_PORT

    @staticmethod
    def generate_auth_string(address: str, access_token: str) -> Callable[[bytes], str]:
        return lambda _: f"user={address}\1auth=Bearer {access_token}\1\1"

    @staticmethod
    def gen_access_token(refresh_token: str, client_id: str):
        """

        :param refresh_token:
        :param client_id:
        :return:
        """
        # 刷新新的access_token
        tenant_id = 'common'
        refresh_token_data = {
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token,
            'client_id': client_id,
        }

        token_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
        response = requests.post(token_url, data=refresh_token_data)
        if response.status_code == 200:
            new_access_token = response.json().get('access_token')
            logger.info(f"获取 Access Token: {new_access_token}")
            return new_access_token
        else:
            raise RuntimeError(f"获取 Access Token 失败: {response.status_code} - {response.status_code}")

    @classmethod
    def login(
            cls,
            address: str,
            password: str,
            host: str = None,
            port: int = None,
            use_ssl: bool = True,
            socket_params: SocketParams = None
    ):
        """

        :param address:
        :param password: access_token
        :param host:
        :param port:
        :param use_ssl:
        :param socket_params:
        :return:
        """
        host = host or cls.HOST
        port = port or cls.PORT
        client = IMAP4SSLClient(host, port, socket_params=socket_params)
        authobject = cls.generate_auth_string(address, password)
        client.authenticate('XOAUTH2', authobject)  # noqa
        return cls(client)
