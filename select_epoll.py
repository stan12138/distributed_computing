import select
"""
将会自动根据平台选择使用select,poll或者epoll
使用方式与epoll保持一致，首先实例化一个SEpoll对象，然后注册文件描述符
每一个socket都应该被设置为非阻塞的
然后事件类型不可设置，都被设置为了可读事件
取消也使用unregister
等待和epoll一致，调用poll方法，返回值只包含了可读socket的文件描述符，不包含event

"""




__all__ = ["SEpoll"]


class SEpoll:
	def __init__(self) :
		if "epoll" in dir(select) :
			print("OS of this computer could use epoll...")
			self.platform = "linux"
			self.selector = select.epoll()
		elif "poll" in dir(select) :
			print("OS of this computer could only use poll...")
			self.platform = "ios"
			self.selector = select.poll()	
		elif "select" in dir(select) :
			print("OS of this computer use select...")
			self.platform = "win"
		else :
			print("Can not find select, poll or epoll, please stop !!!!!!")
		self.event_list = []

	def register(self, fd) :
		if self.platform=="win" :
			self.event_list.append(fd)
		elif self.platform=="linux" :
			self.selector.register(fd, select.EPOLLIN)
		elif self.platform=="ios" :
			self.selector.register(fd, select.POLLIN)

	def poll(self) :
		if self.platform=="win" :
			r_list, w_list, erro_list = select.select(self.event_list, [], [])

			return r_list
		elif self.platform=="linux" :
			event_list = self.selector.poll()
			r_list = []
			for fd, event in event_list :
				if event==select.EPOLLIN :
					r_list.append(fd)
		elif self.platform=="ios" :
			event_list = self.selector.poll()
			r_list = []
			for fd, event in event_list :
				if event==select.POLLIN :
					r_list.append(fd)
		return r_list

	def unregister(self, fd) :
		if self.platform=="win" :
			self.event_list.remove(fd)
		else :
			self.selector.unregister(fd)
