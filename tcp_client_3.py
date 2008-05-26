#!/usr/bin/python

import sys, socket, time, threading

LOGGING = True

loglock = threading.Lock()
def log(s, *a):
	if LOGGING:
		loglock.acquire()
		try:
			print '%s:%s' % (time.ctime(), (s % a)) 
			sys.stdout.flush()
		finally:
			loglock.release()

class PipeThread(threading.Thread):
	pipes = [] 
	pipeslock = threading.Lock()
	def __init__(self, source, sink):
		threading.Thread.__init__(self) 
		self.source = source 
		self.sink = sink 
		log('Creating new pipe thread %s ( %s -> %s )', self, source.getpeername(), sink.getpeername()) 
		self.pipeslock.acquire() 
		try: self.pipes.append(self) 
		finally: self.pipeslock.release() 
		self.pipeslock.acquire() 
		try: pipes_now = len(self.pipes) 
		finally: self.pipeslock.release() 
		log('%s pipes now active', pipes_now) 
	def run(self): 
		while True: 
			try: 
				data = self.source.recv(1024) 
				if not data: break 
				self.sink.send(data) 
			except: 
				break 
		log('%s terminating', self) 
		self.pipeslock.acquire() 
		try: self.pipes.remove(self) 
		finally: self.pipeslock.release() 
		self.pipeslock.acquire() 
		try: pipes_left = len(self.pipes) 
		finally: self.pipeslock.release() 
		log('%s pipes still active', pipes_left) 

class Pinhole(threading.Thread): 
	def __init__(self, port, newhost, newport): 
		threading.Thread.__init__(self) 
		log('Redirecting: localhost:%s -> %s:%s', port, newhost, newport) 
		self.newhost = newhost 
		self.newport = newport 
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
		self.sock.bind(('127.0.0.1', port)) 
		self.sock.listen(5) 
	def run(self): 
		while True: 
			newsock, address = self.sock.accept()
			log('Creating new session for %s:%s', *address)
			fwd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			fwd.connect((self.newhost, self.newport))
			PipeThread(newsock, fwd).start()
			PipeThread(fwd, newsock).start()
			quit()

if __name__ == '__main__': 
	print 'Starting Pinhole port forwarder/redirector' 
	# get the arguments, give help in case of errors 
	try: 
		port = int(sys.argv[1]) 
		newhost = sys.argv[2] 
		try: newport = int(sys.argv[3]) 
		except IndexError: newport = port 
	except (ValueError, IndexError): 
		print 'Usage: %s port newhost [newport]' % sys.argv[0] 
		sys.exit(1) 
	# start operations 
	sys.stdout = open('pinhole.log', 'w') 
	Pinhole(port, newhost, newport).start()
