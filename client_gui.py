import socket, cv2, pickle, struct
from ultralytics import YOLO
import math
import PySimpleGUI as sg


def get_layout():
	return [ 
		[sg.Text('IP: '), sg.InputText()],
		[sg.Text('Port: '), sg.InputText()],
		[sg.Text('Filename: '), sg.InputText()],
		[sg.Button('Connect'), sg.Button('Cancel')]
	]

def socket_setup(host_ip, port, filename):
	a = 1
	model = YOLO("yolov8n-face.pt") #path to model

	client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	host_ip = str(host_ip)
	port = int(port)
	client_socket.connect((host_ip, port))
	data = b""
	payload_size = struct.calcsize("Q")
	while True:
		while len(data) < payload_size:
			packet = client_socket.recv(4*1024)
			if not packet: break
			data += packet
		packed_msg_size = data[:payload_size]
		data = data[payload_size:]
		msg_size = struct.unpack("Q", packed_msg_size)[0]

		while len(data) < msg_size:
			data += client_socket.recv(4*1024)
		frame_data = data[:msg_size]
		data = data[msg_size:]
		frame = pickle.loads(frame_data)

		results = model(frame, stream=True)

		for r in results:
			boxes = r.boxes
			for box in boxes:
				# bounding box
				x1, y1, x2, y2 = box.xyxy[0]
				x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2) # convert to int values

				# put box in cam
				cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 255), 3)

				# confidence
				confidence = math.ceil((box.conf[0]*100))/100
				print("Confidence --->",confidence)

				# object details
				org = [x1, y1]
				font = cv2.FONT_HERSHEY_SIMPLEX
				fontScale = 1
				color = (255, 0, 0)
				thickness = 2
				with open(f'{filename}.txt', 'a') as f:
					f.write(f'frame {a}: {box.xyxy[0]}\n')
				f.close()
				a += 1

				cv2.putText(frame, f"Face {confidence}", org, font, fontScale, color, thickness)
			cv2.imshow('received', frame)

		key = cv2.waitKey(1)
		if key == ord('q'):
			break
	client_socket.close()


def main():
	sg.theme('DarkAmber')   
	# Устанавливаем цвет внутри окна 
	layout = get_layout()

	# Создаем окно
	window = sg.Window('Client', layout)
	# Цикл для обработки "событий" и получения "значений" входных данных
	while True:
	    event, values = window.read()
	    if event == sg.WIN_CLOSED or event == 'Cancel': 
	# если пользователь закрыл окно или нажал «Отмена»
	        break
	    window.close()
	    socket_setup(values[0], values[1], values[2])


	window.close()

if __name__ == '__main__':
	main()