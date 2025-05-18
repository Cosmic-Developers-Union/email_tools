# -*- coding: utf-8 -*-
# Copyright (C) 2025 Cosmic-Developers-Union (CDU), All rights reserved.

"""Models Description

"""
import email
import email.header
import imaplib

from bs4 import BeautifulSoup
from curl_cffi import requests
from loguru import logger


# region 获取邮箱相关代码
def decode_mime_words(s):
    decoded_fragments = email.header.decode_header(s)
    return ''.join([str(t[0], t[1] or 'utf-8') if isinstance(t[0], bytes) else t[0] for t in decoded_fragments])


def strip_html(content):
    soup = BeautifulSoup(content, "html.parser")
    return soup.get_text()


def safe_decode(byte_content):
    # result = chardet.detect(byte_content)
    # encoding = result['encoding']
    # if encoding is not None:
    #     return byte_content.decode(encoding)
    # else:
    return byte_content.decode('utf-8', errors='ignore')


def remove_extra_blank_lines(text):
    lines = text.splitlines()
    # 使用 filter 删除空行，保留非空行
    return "\n".join(filter(lambda line: line.strip(), lines))


def get_folder_emails(mail, folder_name):
    status, messages = mail.select(folder_name)
    if status != "OK":
        logger.error(f"选择 {folder_name} 失败: {status}")
        return

    status, message_ids = mail.search(None, 'ALL')
    if status != "OK":
        logger.error(f"邮件搜索失败: {status}")
        return
    email_counter = 1

    # 获取每封邮件
    for message_id in message_ids[0].split():
        status, msg_data = mail.fetch(message_id, '(RFC822)')
        if status != "OK":
            logger.error(f"获取邮件失败: {status}")
            continue

        for response_part in msg_data:
            if isinstance(response_part, tuple):
                msg = email.message_from_bytes(response_part[1])
                subject = decode_mime_words(msg["subject"])
                date = msg["date"]
                body = ""
                if msg.is_multipart():
                    for part in msg.walk():
                        content_type = part.get_content_type()
                        content_disposition = str(
                            part.get("Content-Disposition"))

                        if "attachment" not in content_disposition:
                            if content_type == "text/plain":
                                body += safe_decode(part.get_payload(decode=True))
                            elif content_type == "text/html":
                                html_content = safe_decode(
                                    part.get_payload(decode=True))
                                body += strip_html(html_content)  # 去除 HTML 元素
                else:
                    if msg.get_content_type() == "text/plain":
                        body = safe_decode(msg.get_payload(decode=True))
                    elif msg.get_content_type() == "text/html":
                        html_content = safe_decode(
                            msg.get_payload(decode=True))
                        body = strip_html(html_content)  # 去除 HTML 元素

                body = remove_extra_blank_lines(body)
                yield {
                    "folder_name": folder_name,
                    "email_counter": email_counter,
                    "subject": subject,
                    "date": date,
                    "body": body
                }
                email_counter += 1


class MSEmailClient:
    """微软邮箱客户端"""

    @staticmethod
    def gen_access_token(refresh_token: str, client_id: str):
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

    @staticmethod
    def monkey(a):
        return a

    def generate_auth_string(self, x):
        return f"user={self.address}\1auth=Bearer {self.access_token}\1\1"

    def __init__(self, address: str, access_token: str, client_id: str):
        self.address = address
        self.access_token = access_token
        self.client_id = client_id
        self.mail = None

    def login(self):
        self.mail = imaplib.IMAP4_SSL('outlook.office365.com')
        self.mail.authenticate('XOAUTH2', self.generate_auth_string)  # noqa

    def logout(self):
        try:
            self.mail.logout()
        except (imaplib.IMAP4.abort, imaplib.IMAP4.error) as e:
            raise RuntimeError(f"退出失败: {e}")

    def __iter__(self):
        for i in get_folder_emails(self.mail, "INBOX"):
            yield i
        for i in get_folder_emails(self.mail, "Junk"):
            yield i

# endregion
