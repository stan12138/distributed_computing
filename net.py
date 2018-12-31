import socket
from select_epoll import SEpoll
from protocol import Server_parser
import threading


class Server :
    def __init__(self, ip='0.0.0.0', port=3000) :
        self.port = port
        self.ip = ip

        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((self.ip, self.port))
        self.server.listen(64)
        self.server.setblocking(False)

        self.fileno = self.server.fileno()

        self.epoll = SEpoll()
        self.epoll.register(self.fileno)

        self.protocol = Server_parser()

        self.ack = threading.Event()

        #self.msg_handler = Protocol()

        self.new_client = []   #存储刚刚连接的新客户端的fd
        self.producer = []     #存储生产者的fd
        self.consumer = []     #存储消费者的fd

        self.all_client = {}   #存储所有客户端的fd:socket字典

        self.client_info = {}  #存储所有客户端的fd：info， info是客户端的信息，结构为[(ip, port), nums]

        self.status = "wait"   #当前状态，wait等待任务； sending发布任务； working任务执行中

        self.tasks = []
        self.done_task = []
        self.doing_task = {}

        self.args = []   #任务的所有参数
        self.task_file = [] #任务依赖的所有代码文件


    def __del__(self) :
        print("use del")
        self.stop()

    def run(self) :
        fileno_list = self.epoll.poll()
        for fd in fileno_list :
            if fd == self.fileno :
                self.recv_connect()
            else :
                client = self.all_client[fd]
                with client.makefile("rb", "-1") as socket_file :
                    header = self.protocol.parse(socket_file)
                        if header=="TYPE" :
                            self.handle_client_type(fd, client, socket_file)
                        elif header=="GETNODES" :
                            self.protocol.send_node_list(client, [self.client_info[i] for i in self.consumer])
                        elif header=="FILE" :
                            self.protocol.parse_file(socket_file)
                        elif header=="STOP" :
                            self.handle_stop_task()
                        elif header=="ARGS" :
                            self.handle_args(socket_file)

    def work_threading(self) :
        pass


    def recv_connect(self) :
        client_socket, client_address = self.server.accept()
        client_socket.setblocking(False)
        self.epoll.register(client_socket.fileno())
        self.all_client[client_socket.fileno()] = client_socket
        self.new_client.append(client_socket.fileno())
        self.client_info[client_socket.fileno()] = [client_address]

    def handle_client_type(self, fd, client, socket_file) :
        client_type, nums = self.protocol.parse_type(socket_file)
        if client_type=="P" :
            if len(self.producer)==0 :
                self.producer.append(fd)
                self.protocol.send_node_list(client, [self.client_info[i] for i in self.consumer])
            else :
                self.protocol.send_occupy(client)
        elif client_type=="C" :
            if fd not in self.consumer :
                self.consumer.append(fd)
                self.client_info[fd].append(nums)
        
    def stop(self) :
        for key in self.new_client.keys() :
            self.new_client[key][0].close()
        for key in self.producer.keys() :
            self.producer[key][0].close()
        for key in self.consumer.keys() :
            self.consumer[key][0].close()
        self.server.close()


    def handle_stop_task(self) :
        for fd in self.consumer :
            self.protocol.send_stop(self.all_client[fd])

    def handle_args(socket_file) :
        self.args = self.protocol.parse_args(socket_file)

        self.start_task()


    def start_task(self) :
        for fd in self.consumer :


    def handle_header(self) :
        if header=="TYPE" :
                pass
            elif header=="GETNODES" :
                pass
            elif header=="FILE" :
                pass
            elif header=="STOP" :
                pass
            elif header=="ARGS" :
                pass
            elif header=="ERROR" :
                pass
            elif header=="CONFIRM" :
                pass
            elif header=="RESULT" :
                pass
            elif header=="ACK" :
                self.event.set()
            elif header=="START" :
                pass

class Client :
    def __init__(self, ip, port) :
        self.server_ip = ip
        self.server_port = port
        self.server_address = (ip, port)
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.epoll = SEpoll()
        

    def __del__(self) :
        print("use del")
        self.stop()

    def connect(self) :
        """
        持续尝试连接到服务器，直至成功
        """
        while True :
            try :
                self.client.connect(self.server_address)
                print("connect success....")
                break
            except :
                print("try again...")
                self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.setblocking(False)
        self.epoll.register(self.client.fileno())


    def wait_msg(self) :
        """
        持续阻塞，等待消息的到来，返回True
        """
        fd_list = self.epoll.poll()
        if fd_list[0] == self.client.fileno() :
            return True
        else :
            return False

    def stop(self) :
        self.client.close()