import socket, cv2, pickle, struct
import PySimpleGUI as sg

def get_layout(host=""):
	if host == "":
		host_name = socket.gethostname()
		host_ip = socket.gethostbyname(host_name)
		host = f"{host_name}@{host_ip}"
		return [ 
		 	[sg.Text(f'{host}')],
			[sg.Text('Port: '), sg.InputText()],
			[sg.Button('Listen'), sg.Button('Cancel')] 
		]


def socket_setup(port):
	#socket create
	server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	host_name = socket.gethostname()
	host_ip = socket.gethostbyname(host_name)
	print('host ip:', host_ip)
	port = int(port)
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


def main():	
	host_name = socket.gethostname()
	host_ip = socket.gethostbyname(host_name)

	sg.theme('DarkAmber')   
	# Устанавливаем цвет внутри окна 
	layout = get_layout()

	# Создаем окно
	window = sg.Window('Listener', layout)
	# Цикл для обработки "событий" и получения "значений" входных данных
	while True:
	    event, values = window.read()
	    if event == sg.WIN_CLOSED or event == 'Cancel': 
	# если пользователь закрыл окно или нажал «Отмена»
	        break
	    window.close()
	    socket_setup(values[0])


	window.close()


if __name__ == '__main__':
	main()