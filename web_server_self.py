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
    epoll IO并发
"""
import re
from select import *
from socket import *


class WebServer:
    """
        HTTP网络服务
    """
    def __init__(self, host="0.0.0.0", port=8800, dir=None):
        self.host = host
        self.port = port
        self.dir = dir
        self.__create_sock_tcp()
        self.__bind_address()

    def __create_sock_tcp(self):
        """
            创建tcp套接字
        """
        self.sock_tcp = socket()
        self.sock_tcp.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.sock_tcp.setblocking(False)

    def __bind_address(self):
        """
            绑定地址
        """
        self.sock_tcp.bind((self.host, self.port))

    def set_connect(self, fd):
        """
            建立与客户端链接,将链接套接字登记到epoll监控
        :param fd: 文件描述符
        """
        connfd, addr = self.fdmap[fd].accept()
        print(f"Connect From {addr}")
        connfd.setblocking(False)
        self.ep.register(connfd, EPOLLIN)
        self.fdmap[connfd.fileno()] = connfd

    def dispose(self, fd):
        """
            处理客户端请求
        :param fd: 文件描述符
        """
        data = self.fdmap[fd].recv(1024 * 10).decode()
        # print(data)
        try:
            msg = re.match(r"[A-Z]+\s+(?P<info>/\S*)", data).group("info")
            print(f"请求内容:{msg}")
        except:
            self.ep.unregister(fd)
            self.fdmap[fd].close()
            del self.fdmap[fd]
            return
        else:
            self.send_to(msg, fd)

    def send_to(self, msg, fd):
        """
            给客户端回复消息
        :param msg: 客户端请求字段
        :param fd: 文件描述符
        """
        if msg == "/":
            html = self.dir + "/index.html"
        else:
            html = self.dir + msg
        try:
            f = open(html, "rb")
        except:
            response = "HTTP/1.1 404 Not Found\r\n"
            response += "Connect-Type:text/html\r\n"
            response += "\r\n"
            response += "<h1>Sorry...</h1>"
            response = response.encode()
        else:
            data = f.read()
            response = "HTTP/1.1 200 OK\r\n"
            response += "Content-Type:text/html\r\n"
            response += f"Content-Length:{len(data)}\r\n"
            response += "\r\n"
            response = response.encode() + data
        finally:
            self.fdmap[fd].send(response)

    def start(self):
        """
            IO多路复用 epoll
        """
        self.sock_tcp.listen(5)
        self.ep = epoll()
        self.ep.register(self.sock_tcp, EPOLLIN)
        self.fdmap = {self.sock_tcp.fileno(): self.sock_tcp}
        while True:
            events = self.ep.poll()
            for fd, event in events:
                if fd == self.sock_tcp.fileno():
                    self.set_connect(fd)
                else:
                    self.dispose(fd)


if __name__ == '__main__':
    host = "0.0.0.0"
    port = 9999
    dir = "./static"
    ws = WebServer(host=host, port=port, dir=dir)
    ws.start()
