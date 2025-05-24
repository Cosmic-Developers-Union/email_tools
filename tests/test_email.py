# -*- coding: utf-8 -*-
# Copyright (C) 2025 Cosmic-Developers-Union (CDU), All rights reserved.

"""Models Description

"""
import datetime
import os
import socket
import unittest

import dotenv
from loguru import logger

import email_tools_quick as etq
from email_tools_quick.outlook import EMail


class MyTestCase(unittest.TestCase):
    def setUp(self):
        dotenv.load_dotenv()
        address, passwd, client_id, refresh_token = os.environ["TEST_EMAIL"].split("----")
        self.address = address
        self.passwd = passwd
        self.client_id = client_id
        self.refresh_token = refresh_token

    def test_something(self):
        email_ = EMail(
            folder_name="INBOX",
            email_counter=1,
            subject="Test Subject",
            date=datetime.datetime.now(tz=datetime.timezone.utc),
            body="This is a test email body."
        )
        print(email_['subject'])
        print(dict(email_))

    def test_least_5_minutes_ago(self):
        access_token = etq.outlook.gen_access_token(self.refresh_token, self.client_id)
        logger.info(f"{access_token=}")
        with etq.outlook.OutlookIMAP(self.address, access_token, self.client_id) as outlook:
            for em in outlook.latest_minutes(15):
                print(em)

    def test_connect(self):
        socket.create_connection = print
        with self.assertRaises(AttributeError):
            self.test_least_5_minutes_ago()

    def test_proxy(self):
        from email_tools_quick.mail import SocketParams
        access_token = etq.outlook.gen_access_token(self.refresh_token, self.client_id)
        logger.info(f"{access_token=}")
        oi = etq.outlook.OutlookIMAP(self.address, access_token, self.client_id)
        oi.socket_params = SocketParams.socks5h(os.environ['TEST_S5_HOST'], int(
            os.environ['TEST_S5_PORT']
        ))
        with oi as outlook:
            while True:
                for em in outlook.latest(5):
                    print(em)
                if input("...").strip() == "q":
                    break


if __name__ == '__main__':
    unittest.main()
