import os
import posix

FIFO = 'mypipe'
os.mkfifo(FIFO, 0o777)

def readPipe():
	while True:
		try:
			p = os.open(FIFO, os.O_RDONLY | os.O_NONBLOCK)
			input = os.read(p, 1)
		except:
			continue

		if input:
			break

		os.close(p)
		print('...')

readPipe()
os.unlink(FIFO)