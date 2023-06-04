import threading
import time
try:
	import queue
except:
	import Queue as queue

class Threader:
	def __init__(self,pool_size=1,name='WAYBACK'):
		self.q = queue.Queue()
		self.pool_size = pool_size
		self.thread_name=name

	def __t(self):
		thread = self.q.get()
		thread.daemon=True
		thread.start()

	def __name(self):
		return self.thread_name

	def __wait(self):
		while 1:
			running = threading.enumerate()
			if remain := [x.name for x in running if self.__name() in x.name]:
				time.sleep(0.5)
			else:
				break

	def on_waiting(self):
		return self.q.qsize()

	def pop(self):
		return self.q.queue.pop()

	def finish_all(self):
		for _ in range(self.q.qsize()): self.__t()
		self.__wait()

	def put(self,target,args):
		if self.q.qsize() < self.pool_size:
			self.q.put(threading.Thread(target=target,name=self.__name(),args=tuple(args)))

		if self.q.qsize() >= self.pool_size:
			for _ in range(self.q.qsize()): self.__t()
			self.__wait()