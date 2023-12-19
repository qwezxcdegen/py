import socket, cv2, pickle, struct

def main():
	#socket create
	server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	host_name = socket.gethostname()
	host_ip = socket.gethostbyname(host_name)
	print('host ip:', host_ip)
	port = 9984
	socket_address = (host_ip, port)

	#socket bind
	server_socket.bind(socket_address)

	#socket listen
	server_socket.listen()
	print("listening at:", socket_address)

	#socket accept
	while True:
		client_socket, addr = server_socket.accept()
		print("got connection from:", addr)
		if client_socket:
			vid = cv2.VideoCapture(0)
			while vid.isOpened():
				img, frame = vid.read()
				a = pickle.dumps(frame)
				message = struct.pack("Q", len(a)) + a
				client_socket.sendall(message)
				cv2.imshow("transmitting video", frame)
				key = cv2.waitKey(1)
				if key == ord('q'):
					client_socket.close()


if __name__ == '__main__':
	main()