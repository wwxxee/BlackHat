#coding=utf-8
from burp import IBurpExtender  # 这是编写插件所必需的类
from burp import IContextMenuFactory

from java.net import URL
from java.util import ArrayList
from javax.swing import JMenuItem
from thread import start_new_thread

import json
import socket
import urllib

API_KEY = ""
API_HOST = "api.cognitive.microsoft.com"


class BurpExtender(IBurpExtender, IContextMenuFactory):
    """
    实现IContextMenuFactory接口，可以在右键单机一条请求时提供相应的右键菜单项
    这个菜单项的文本内容是“Send to Bing”
    """
    def registerExtenderCallbacks(self, callbacks):
        self._callbacks = callbacks
        self._helpers = callbacks.getHelpers()

        self.context = None

        # 设置扩展与注册扩展
        callbacks.setExtensionName("BHP Bing")
        callbacks.registerContextMenuFactory(self)

        return

    def createMenuItems(self, context_menu):
        """
        接收IContextMenuInvocation对象作为参数，用来判断用户选中的是哪个HTTP请求
        :param context_menu:
        :return:
        """
        self.context = context_menu
        menu_list = ArrayList()
        # 使用bing_menu函数响应鼠标单击事件
        menu_list.add(JMenuItem("Send to Bing", actionPerformed=self.bing_menu))
        return menu_list

    def bing_menu(self, event):

        # 抓取用户点击的细节
        http_traffic = self.context.getSelectedMessages()

        print("%d requests highlighted" % len(http_traffic))

        for traffic in http_traffic:
            http_service = traffic.getHttpService()
            host = http_service.getHost()

            print("User selected host: %s" % host)
            self.bing_search(host)

        return

    def bing_search(self, host):
        # 检查是IP还是主机名
        try:
            # inet_aton()函数用于将点分十进制IP地址转换成网络字节序IP地址
            # 如果这个函数成功，函数的返回值非零，如果输入地址不正确则会返回零;
            is_ip = bool(socket.inet_aton(host))
        except socket.error:
            is_ip = False

        if is_ip:
            ip_address = host
            domain = False
        else:
            ip_address = socket.gethostbyname(host)
            domain = True

        start_new_thread(self.bing_query, ('ip:%s' % ip_address,))

        if domain:
            start_new_thread(self.bing_query, ('domain:%s' % host,))

    def bing_query(self, bing_query_string):
        """
        Burp 的HTTP API要求将整个请求拼接成一个完整的字符串再发送
        :param bing_query_string:
        :return:
        """
        print('Performing Bing search: %s' % bing_query_string)
        http_request = 'GET https://%s/bing/v7.0/search?' % API_HOST
        # encode our query
        http_request += 'q=%s HTTP/1.1\r\n' % urllib.quote(bing_query_string)
        http_request += 'Host: %s\r\n' % API_HOST
        http_request += 'Connection:close\r\n'
        http_request += 'Ocp-Apim-Subscription-key: %s\r\n' % API_KEY
        http_request += 'User-Agent: Black Hat Python \r\n\r\n'

        json_body = self._callbacks.makeHttpRequest(API_HOST, 443, True, http_request).tostring()
        # 当数据响应时，把HTTP头分离出去
        json_body = json_body.split('\r\n\r\n', 1)[1]

        try:
            response = json.loads(json_body)
        except (TypeError, ValueError) as err:
            print('No results from bing: %s' % err)
        else:
            sites = list()
            if response.get('webPages'):
                sites = response['webPages']['value']
            if len(sites):
                for site in sites:
                    print('*'*100)
                    print('Name: %s        ' % site['name'])
                    print('URL: %s        ' % site['url'])
                    print('Description: %r        ' % site['snippet'])
                    print('*' * 100)
                    java_url = URL(site['url'])
                    if not self._callbacks.isInScope(java_url):
                        print('Adding %s to Burp scope' % site['url'])
                        self._callbacks.includeInScope(java_url)
                    else:
                        print('Empty response from Bing: %s' % bing_query_string)
        return





