from win32com import client

import os
import random
import requests
import time


username = 'xxx'
password = 'xxx'
api_dev_key = "xxx"
api_user_key = "xxx"


def plain_paste(title, contents):
    # login_url = 'https://pastebin.com/api/api_login.php'
    # login_data = {
    #     'api_dev_key': api_dev_key,
    #     'api_user_name': username,
    #     'api_user_password': password,
    # }
    # r = requests.post(login_url, data=login_data)
    # api_user_key = r.text
    # print(api_user_key)

    #  同一用户只能同时激活一个api_user_key。该密钥不会过期，除非生成新密钥。
    #  我们建议只创建一个，然后在本地缓存该密钥，因为它不会过期
    paste_url = "https://pastebin.com/api/api_post.php"
    paste_data = {
        'api_paste_name': title,
        'api_paste_code': contents.decode(),
        'api_dev_key': api_dev_key,
        'api_user_key': api_user_key,
        'api_option': 'paste',
        'api_paste_private': 0,
    }

    r = requests.post(url=paste_url, data=paste_data)
    print(r.status_code)
    print(r.text)


def wait_for_browser(browser):
    """
    用来等待浏览器完成当前操作
    :param browser:
    :return:
    """
    while browser.ReadyState != 4 and browser.ReadyState != 'complete':
        time.sleep(0.1)


def random_sleep():
    time.sleep(random.randint(5, 10))


def login(ie):
    full_doc = ie.Document.all
    for elem in full_doc:
        if elem.id == 'loginform-username':
            elem.setAttribute('value', username)
        elif elem.id == 'loginform-password':
            elem.setAttribute('value', password)

    random_sleep()
    if ie.Document.forms[0].id == 'w0':
        ie.document.forms[0].submit()
    wait_for_browser(ie)


def submit(ie, title, contents):
    full_doc = ie.Document.all
    for elem in full_doc:
        if elem.id == 'postform-name':
            elem.setAttribute('value', title)
        elif elem.id == 'postform-text':
            elem.setAttribute('value', contents)

    if ie.Document.forms[0].id == 'w0':
        ie.document.forms[0].submit()
    random_sleep()
    wait_for_browser(ie)


def ie_paste(title, contents):
    # 创建IE浏览器COM对象的实例
    ie = client.Dispatch('InternetExplorer.Application')
    ie.Visible = 1  # 是否显示窗口

    ie.Navigate('https://pastebin.com/login')
    wait_for_browser(ie)
    login(ie)

    ie.Navigate('https://pastebin.com')
    wait_for_browser(ie)
    submit(ie, title, contents.decode())

    ie.Quit()


if __name__ == '__main__':
    ie_paste('title', b'contents')
