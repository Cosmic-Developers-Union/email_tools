# -*- coding: utf-8 -*-
# Copyright (C) 2025 Cosmic-Developers-Union (CDU), All rights reserved.

"""Models Description

"""
import dataclasses
import datetime

import dateutil.parser


@dataclasses.dataclass
class EMail:
    folder_name: str
    email_counter: int
    subject: str | None
    date: datetime.datetime | str | None
    body: str

    def __getitem__(self, item):
        if item == "subject":
            return self.subject
        elif item == "date":
            return self.date
        elif item == "body":
            return self.body
        elif item == "email_counter":
            return self.email_counter
        elif item == "folder_name":
            return self.folder_name
        else:
            raise KeyError(f"Invalid key: {item}")

    def _date(self) -> str | None:
        if isinstance(self.date, datetime.datetime):
            return self.date.strftime("%Y-%m-%d %H:%M:%S %z")
        elif isinstance(self.date, str):
            return dateutil.parser.parse(self.date).astimezone(datetime.timezone.utc).strftime(
                "%Y-%m-%d %H:%M:%S %z"
            )
        elif self.date is None:
            return None
        else:
            raise TypeError(f"Invalid date type: {type(self.date)}")

    def __iter__(self):
        yield from {
            "subject": self.subject,
            "date": self._date(),
            "body": self.body,
            "email_counter": self.email_counter,
            "folder_name": self.folder_name
        }.items()