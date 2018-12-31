import threading
from net import Client
from protocol import Producer_parser



class Producer(Client) :
	def __init__(self, ip, port, file_list, args) :
		Client.__init__(ip, port)

		self.ack = threading.Event()
		self.ack.set()

		self.parser = Producer_parser(self.get_result, self.ack)

		self.file_list = file_list
		self.args = args

		self.connect()

		self.parser.send_type(self.client)


	def get_result(self, result) :
		print(result)

	def release_task(self) :
		self.parser.send_file(self.client, self.file_list, self.ack)
		self.parser.send_args(self.client, self.args)

	def get_input(self) :
		while True :
			a = input(">> ")
			if a=="close" :    #关闭本节点
				self.stop()
				break
			elif a=="stop" :   #终止当前任务
				self.parser.send_stop(self.client)
			elif a=="list" :   #列出当前的任务节点
				self.parser.send_get_nodes(self.client)
			elif a=="run" :    #提交当前任务
				self.release_task(file_list, args)

	def keep_recv(self) :
		while True :
			if self.wait_msg() :
				self.parser.parse(self.client)

