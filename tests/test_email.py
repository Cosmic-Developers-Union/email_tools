# -*- coding: utf-8 -*-
# Copyright (C) 2025 Cosmic-Developers-Union (CDU), All rights reserved.

"""Models Description

"""

import unittest
import datetime
from email_tools.outlook import EMail


class MyTestCase(unittest.TestCase):
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


if __name__ == '__main__':
    unittest.main()
