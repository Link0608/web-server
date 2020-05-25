# 1.
# 主要功能 ：
# 【1】 接收客户端（浏览器）请求
# 【2】 解析客户端发送的请求
# 【3】 根据请求组织数据内容
# 【4】 将数据内容形成http响应格式返回给浏览器
# 2.
# 特点 ：
# 【1】 采用IO并发，可以满足多个客户端同时发起请求情况
# 【2】 通过类接口形式进行功能封装
# 【3】 做基本的请求解析，根据具体请求返回具体内容，同时处理客户端的非网页请求行为
"""
    select IO并发
"""
import re
from select import select
from socket import *


class WebServer:
    """
        网页服务器
    """

    def __init__(self, host="0.0.0.0", port=8000, dir=None):
        self.host = host
        self.port = port
        self.dir = dir
        self.rlist = []
        self.wlist = []
        self.xlist = []
        self.__create_sock()
        self.__bind_addr()

    def __create_sock(self):
        """
            创建TCP套接字
        """
        self.sock_tcp = socket(AF_INET, SOCK_STREAM)
        self.sock_tcp.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.sock_tcp.setblocking(False)

    def __bind_addr(self):
        """
            绑定地址
        """
        self.sock_tcp.bind((self.host, self.port))

    def send_to(self, info, connfd):
        """
            发送响应信息
        :param info: 请求内容
        :param connfd: 连接套接字
        """
        if info == "/":
            html = self.dir + "/index.html"
        else:
            html = self.dir + info
        try:
            f = open(html, "rb")
        except:
            response = "HTTP/1.1 404 Not Found\r\n"
            response += "Content-Type:text/html\r\n"
            response += "\r\n"
            response += "<h1>Sorry...</h1>"
            connfd.send(response.encode())
        else:
            data = f.read()
            response = "HTTP/1.1 200 OK\r\n"
            response += "Content-Type:text/html\r\n"
            response += f"Content-Length:{len(data)}\r\n"
            response += "\r\n"
            response = response.encode() + data
            connfd.send(response)

    def set_connect(self, sock_tcp):
        """
            建立网络连接
        :param sock_tcp: 监听套接字
        """
        connfd, addr = sock_tcp.accept()
        print(f"Connect From:{addr}")
        self.rlist.append(connfd)

    def dispose(self, connfd):
        """
            处理客户端请求信息
        :param connfd:连接套接字
        """
        data = connfd.recv(1024 * 10).decode()
        try:
            info = re.match(r"[A-Z]+\s+(?P<info>/\S*)", data).group("info")
            print(info)
        except:
            connfd.close()
            self.rlist.remove(connfd)
            return
        else:
            self.send_to(info, connfd)

    def start(self):
        """
            使用IO多路复用 select方法
        """
        self.sock_tcp.listen(5)
        self.rlist.append(self.sock_tcp)
        while True:
            rs, ws, xs = select(self.rlist, self.wlist, self.xlist)
            for r in rs:
                if r is self.sock_tcp:
                    self.set_connect(r)
                else:
                    self.dispose(r)


if __name__ == '__main__':
    host = "0.0.0.0"
    port = 9999
    dir = "./static"
    httpd = WebServer(host=host, port=port, dir=dir)
    httpd.start()
