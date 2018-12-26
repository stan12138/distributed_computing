import socket
from select_epoll import SEpoll


class Server :
    def __init__(self, ip='0.0.0.0', port=3000) :
        self.port = port
        self.ip = ip

        self.server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server.bind((self.ip, self.port))

        self.fileno = self.server.fileno()

        self.epoll = SEpoll()

        self.epoll.register(self.fileno)

        self.clients = {}

    def __del__(self) :
        print("use del")
        self.stop()

    def run(self) :
        fileno_list = self.epoll.poll()
        for fd in fileno_list :
            if fd == self.fileno :
                msg, addr = self.server.recvfrom(1024)
                print(msg, addr)

    def stop(self) :
        self.server.close()


    def send(self, msg, addr) :
        pass


    def msg_parse(self, msg) :
        pass

class Client :
    def __init__(self, ip, port) :
        self.server_ip = ip
        self.server_port = port

        self.server_address = (ip, port)

        self.client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def __del__(self) :
        print("use del")
        self.stop()

    def send(self, msg) :
        ack = False
        data = self.msg_marker(msg, 1)
        self.client.sendto(data, self.server_address)


    def msg_marker(self, msg, msg_type) :
        msg = msg

        return msg.encode("utf-8")


    def msg_parse(self, msg) :
        pass


    def stop(self) :
        self.client.close()