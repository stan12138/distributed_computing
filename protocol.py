import pickle
import io


class Protocol :


    """
    代码文件发送与接收
    """
    def parse_file(self, socket_file) :
        """
        可以根据文件协议，从socket_file中解析出代码文件，并自动发回ACK确认
        """
        name = socket_file.readline(4096).decode("utf-8").rstrip("\r\n")
        name_list = name.split(";")
        size = socket_file.readline(4096).decode("utf-8").rstrip("\r\n")
        size = size.split(";")
        size_list = [int(i) for i in size]
        for name, size in zip(name_list, size_list) :
            length = 0
            with open("data/"+name, "wb") as fi :
                while length<size :
                    data = socket_file.read(size)
                    length += len(data)
                    fi.write(data)
        self.send(client, b"ACK\r\n")


    def send_file(self, client, file_list, event) :
        """
        可以根据依赖文件的列表自动发送一系列的依赖文件
        必须依赖事件来实现ACK的接收
        """
        sequence = self.generate_send_sequence(file_list)
        for se in sequence :
            event.wait()
            header = "File\r\n"
            name = ""
            size = ""
            body = b""
            for file in se :
                if file != se[-1] :
                    name = name + file + ";"
                    size = size + str(os.path.getsize(file)) + ";" 
                else :
                    name = name + file + "\r\n"
                    size = size + str(os.path.getsize(file)) + "\r\n"
                with open(file, "rb") as fi :
                    body += fi.read()
            header = header + name + size
            msg = header.encode("utf-8") + body
            event.clear()
            client.send(msg)

    def generate_send_sequence(self, file_list) :
        """
        根据依赖文件列表，生成文件发送序列
        """
        send_sequence = []
        sequence = []
        size = 0
        for file in file_list :
            size += os.path.getsize(file)
            if size<=self.max_file_size :
                sequence.append(file)
            else :
                send_sequence.append(sequence)
                size = os.path.getsize(file)
                sequence = []
                sequence.append(file)
        if len(sequence) :
            send_sequence.append(sequence)
        
        return send_sequence  



    """
    参数发布与解析
    """
    def send_args(self, client, args) :
        """
        发送参数
        """
        data = pickle.dumps(args)
        size = str(len(data))
        header = "ARGS\r\n"+size+"\r\n"
        msg = header.encode("utf-8")+data
        client.send(msg)

    def parse_args(self, socket_file) :
        """
        接收参数
        """
        data, _ = self.get_content(socket_file)
        s = io.BytesIO(data)
        args = pickle.load(s)

        return args


    """
    结果发送接收与转发
    """
    def send_result(self, client, result) :
        """
        发送结果
        """
        data = pickle.dumps(result)
        size = str(len(data))
        header = "RESULT\r\n"+size+"\r\n"

        msg = header.encode("utf-8")+data

        client.send(msg)

    def parse_result(self, socket_file) :
        """
        接受结果
        """
        return self.recv_args(socket_file)

    def forward_result(self, socket_file, client) :
        """
        转发结果
        """
        data, size = self.get_content(socket_file)
        msg = ("RESULT\r\n"+str(size)+"\r\n").encode("utf-8")+data
        client.send(msg)


    """
    类型解析
    """



    """
    错误解析发送与转发
    """
    def parse_error(self, socket_file) :
        """
        解析错误信息
        """
        data, _ = self.get_content(socket_file)

        return data.decode("utf-8")

    def send_error(self, client, info) :
        """
        发送错误信息
        """
        data = info.encode("utf-8")
        client.send(("ERROR\r\n"+str(len(data))+"\r\n").encode("utf-8")+data)

    def forward_error(self, socket_file, client) :
        """
        转发错误信息
        """
        data, size = self.get_content(socket_file)

        return ("ERROR\r\n"+str(size)+"\r\n").encode("utf-8")+data


    """
    任务开始转发与接收
    """
    def parse_start(self, socket_file) :
        """
        解析任务开始确认信息
        """
        data, _ = self.get_content(socket_file)

        return data.decode("utf-8")

    def send_start(self, client) :
        """
        任务节点发送任务开始确认信息
        """
        client.send("ERROR\r\n0\r\n".encode("utf-8"))

    def forward_start(self, socket_file, socket_address, client) :
        """
        转发任务开始确认信息
        """
        data, _ = self.get_content(socket_file)
        data = socket_address[0]+":"+str(socket_address[1])
        data = data.encode("utf-8")

        client.send(("ERROR\r\n"+str(len(data))+"\r\n").encode("utf-8")+data)



    def get_content(self, socket_file) :
        """
        公用方法，获取报文内容，要求是下一行是内容长度信息，接下来是二进制内容
        返回值就是二进制的内容信息和长度信息
        """
        size = int(socket_file.readline(4096).decode("utf-8").rstrip("\r\n"))
        length = 0
        data = b""
        while length<size :
            data += socket_file.read(size)
            length = len(data)

        return data, size

    """
    停止当前任务
    """
    def send_stop(self, client) :
        client.send("STOP\r\n".encode("utf-8"))

class Server_parser(Protocol) :
    """
    为服务器提供的协议解析器
    可接受的数据头：
    [TYPE, GETNODES, FILE, STOP, ARGS, ERROR, CONFIRM, RESULT, ACK, START, CLEAR]
    """
    def __init__(self) :
        pass

    def parser(self, socket_file) :
        header = socket_file.readline(1024).decode("utf-8").rstrip("\r\n")
        return header

    def send_node_list(self, client, node_info_list) :
        """
        发送计算节点的信息
        [node1_info, node2_info....]
        node1_info = [(ip, port), nums]
        """
        body = ""
        for index,node_info in enumerate(node_info_list) :
            body += (node_info[0][0]+":"+str(node_info[0][1])+":"+str(node_info[1]))
            if index != (len(node_info_list)-1) :
                body += ";"
        body = body.encode("utf-8")

        msg = ("NODES\r\n"+str(len(body))+"\r\n").encode("utf-8")+body

        client.send(msg)


    def parse_type(self, socket_file) :
        """
        解析类型协议
        """
        client_type = socket_file.readline(1024).decode("utf-8").rstrip("\r\n")
        nums = int(socket_file.readline(1024).decode("utf-8").rstrip("\r\n"))
        return client_type, nums

    def send_occupy(self, client) :
        client.send("OCCUPY\r\n".encode("utf-8"))


class Producer_parser(Protocol) :
    """
    为生产者提供的协议解析器
    可接受的数据头：
    [OCCUPY, NODES, ACK, RESULT, CONFIRM, ERROR, START]
    """

    # parser_dict = {"OCCUPY":self.parse_occupy, "NODES":self.parse_node_list, "ACK", self.parse_ack, }


    # def parse_occupy(self) :
    #     return "producer occupy"

    # def parse_ack(self, ) :
    #     return "producer occupy"

    def __init__(self, result_handler, event) :
        self.result_handler = result_handler
        self.event = event

    def parse(self, client) :
        with client.makefile("rb", -1) as socket_file :
            header = socket_file.readline(1024).decode("utf-8").rstrip("\r\n")
            if header=="OCCUPY" :
                print("has producer already...going to close")
                client.close()
            elif header=="NODES" :
                print(self.parse_node_list(socket_file))
            elif header=="ACK" :
                self.event.set()
            elif header=="RESULT" :
                self.result_handler(self.parse_result(socket_file))
            elif header=="CONFIRM" :
                print("all task stop...")
            elif header=="ERROR" :
                print("error happen:\r\n", self.parse_error(socket_file))
            elif header=="START" :
                print("node begin task,", self.parse_start(socket_file))

    def send_type(self, client) :
        """
        发送类型报告
        """
        client.send(("TYPE\r\nP\r\n0\r\n").encode("utf-8"))

    def send_get_nodes(self, client) :
        """
        发送节点请求
        """
        client.send("GETNODES\r\n".encode("utf-8"))

    def parse_node_list(self, socket_file) :
        """
        解析节点列表
        """
        data, _ = self.get_content(socket_file)

        return data..decode("utf-8").split(";")

    def send_clear(self, client) :
        client.send("CLEAR\r\n".encode("utf-8"))




class Consumer_parser(Protocol) :
    """
    为消费者提供的协议解析器
    可接受的数据头
    [STOP, ARGS, FILE]
    """
    def __init__(self, stop_method, args_handler) :
        self.stop = stop_method
        self.args_handler = args_handler


    def parse(self, client) :
        with client.makefile("rb", -1) as socket_file :
            header = socket_file.readline(1024).decode("utf-8").rstrip("\r\n")
            if header=="STOP" :
                self.stop()
                self.send_stop(client)
            elif header=="ARGS" :
                self.args_handler(self.parse_args(socket_file))
            elif header=="FILE" :
                self.parse_file(socket_file)

    def send_type(self, client, nums) :
        client.send(("TYPE\r\nC\r\n"+str(nums)+"\r\n").encode("utf-8"))