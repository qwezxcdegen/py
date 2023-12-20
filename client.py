import socket, cv2, pickle, struct
from ultralytics import YOLO
import math

def main():

	model = YOLO("yolov8n-face.pt") #path to model

	client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	host_ip = input("Host ip: ")
	port = int(input("Port: "))
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

				cv2.putText(frame, "Face", org, font, fontScale, color, thickness)
			cv2.imshow('received', frame)

		key = cv2.waitKey(1)
		if key == ord('q'):
			break
	client_socket.close()

if __name__ == '__main__':
	main()