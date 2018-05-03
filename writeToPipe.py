import posix
import os

FIFO = 'mypipe'
#os.mkfifo(FIFO)

def writeToPipe():
	while True:
		with open (FIFO, 'wb', 0) as file:
			file.write(b'hi')
		print("Hallelujah")

writeToPipe()