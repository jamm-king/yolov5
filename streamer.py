import json
import time
import requests
import threading
import cv2


class Streamer:
    HOST = 'http://pos05169.pythonanywhere.com'
    # HOST = 'http://127.0.0.1:8000'
    username = 'admin'
    password = 'Woals0313!'
    token = ''

    client = {}
    streaming = False
    cap = cv2.VideoCapture(0)
    frame = []
    is_frame_new = False

    def __init__(self):

        res = requests.post(self.HOST + '/api-token-auth/', {
            'username': self.username,
            'password': self.password
        })
        res.raise_for_status()
        self.token = res.json()['token']
        print(self.token)

        # thread_check = threading.Thread(target=self.check_client)
        # thread_app = threading.Thread(target=self.app)
        # thread_check.daemon = True
        # thread_app.daemon = True
        # thread_check.start()
        # thread_app.start()

    def app(self):
        while True:
            # print(f"client : {self.client['state']}")
            # print(f"streamer.streaming : {self.streaming}")
            # print(f"streamer.is_frame_new : {self.is_frame_new}")
            try:
                if len(self.client) == 0:
                    time.sleep(10)
                    continue
                print(self.client['state'])
                if self.client['state'] == 'sleep':
                    pass
                elif self.client['state'] == 'waiting_stream':
                    self.start_stream()
                elif self.client['state'] == 'streaming':
                    if self.is_frame_new:
                        _, encoded_frame = cv2.imencode('.jpg', self.frame)
                        if _:
                            self.send_frame(encoded_frame)
                            print("Sended Frame to Client")
                            self.is_frame_new = False
                    continue
                elif self.client['state'] == 'stopping_stream':
                    self.stop_stream()
            except:
                continue

    def work(self):
        try:
            if len(self.client) == 0:
                return
            print(self.client['state'])
            if self.client['state'] == 'sleep':
                pass
            elif self.client['state'] == 'waiting_stream':
                self.start_stream()
            elif self.client['state'] == 'streaming':
                if self.is_frame_new:
                    _, encoded_frame = cv2.imencode('.jpg', self.frame, [int(cv2.IMWRITE_JPEG_QUALITY), 50])
                    if _:
                        self.send_frame(encoded_frame)
                        print("Sended Frame to Client")
                        self.is_frame_new = False
                return
            elif self.client['state'] == 'stopping_stream':
                self.stop_stream()
        except:
            pass

    def check_client(self):
        while True:
            self.update_client()
            time.sleep(10)

    def start_stream(self):
        if not self.streaming:
            self.streaming = True
            headers = {
                'Authorization': 'JWT ' + self.token,
                'Accept': 'application/json'
            }
            body = {
                'name': self.client['name'],
                'state': "streaming",
                'host': self.client['host']
            }
            res = requests.put(url=self.HOST + '/api_root/client/1/', headers=headers, data=body)
            res.raise_for_status()

    def stop_stream(self):
        self.streaming = False
        headers = {
            'Authorization': 'JWT ' + self.token,
            'Accept': 'application/json'
        }
        body = {
            'name': self.client['name'],
            'state': "sleep"
        }
        res = requests.put(url=self.HOST + '/api_root/client/1/', headers=headers, data=body)
        res.raise_for_status()

    def send_frame(self, frame):
        # Send the frame to the Django server for distribution to the smartphone client
        headers = {
            # 'Authorization': 'JWT ' + self.token,
            'Content-Type': 'image/jpeg',
        }
        body = {
            'frame': frame
        }
        # res = requests.post(self.HOST + '/api_root/video_stream/', data=frame.tobytes(), headers=headers)
        res = requests.post('http://' + self.client['host'] + ':8080', data=frame.tobytes(), headers=headers)
        print(f"HOST : {self.client['host']}")
        res.raise_for_status()

    def update_client(self):
        headers = {
            'Authorization': 'JWT ' + self.token,
            'Accept': 'application/json'
        }
        res = requests.get(self.HOST + '/api_root/client/1/', headers=headers)
        data = res.json()
        self.client = data

    def set_frame(self, frame):
        self.frame = frame
        self.is_frame_new = True

if __name__ == '__main__':
    streamer = Streamer()
    streamer.app()