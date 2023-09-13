import json
import logging
import time

import gevent
import requests
import websocket
from locust import FastHttpUser, between, task

BOOKS = [
    {
        "name": "minwook",
        "urls": ["https://minkj1992.github.io/about/"],
        "description": "useful to know about minwook je",
        "max_depth": 1,
    },
    {
        "name": "wrtn",
        "urls": ["https://wrtn.career.greetinghr.com/o/76191"],
        "description": "useful to know about wrtn SW Engineer (LMOps/ML) requirements.",
        "max_depth": 2,
    },
]

ROOM = {"name": "minwook and wrtn", "prompt": "You are an job consultant."}


def load_data(url):
    book_pks = []
    for book in BOOKS:
        response = requests.post(f"{url}/books/urls", json=book)
        pk = response.json().get("book_ulid")
        book_pks.append(pk)

    room_dict = {"books": book_pks, **ROOM}
    response = requests.post(f"{url}/rooms/", json=room_dict)
    room_pk = response.json().get("room_pk")

    return book_pks, room_pk


class GreetTestUser(FastHttpUser):
    wait_time = between(1, 5)

    @task
    def home(self):
        self.client.get(url="/")

    @task
    def ping(self):
        self.client.get(url="/ping")


class ApiTestUser(FastHttpUser):
    wait_time = between(1, 5)

    @task
    def get_a_book(self):
        for pk in self.book_pks:
            self.client.get(url=f"/books/{pk}")
            time.sleep(1)

    @task
    def get_a_room(self):
        self.client.get(url=f"/rooms/{self.room_pk}")

    # @task
    # def post_book(self):
    #     self.client.post(url="/books/urls")

    # @task
    # def post_a_room(self):
    #     self.client.post(url="/rooms/")

    def on_start(self):
        book_pks, room_pk = load_data(self.host)
        self.room_pk = room_pk
        self.book_pks = book_pks


class ChatTesUser(FastHttpUser):
    wait_time = between(1, 5)

    @task
    def chat_hi(self):
        start_time = time.time()
        self.end = False
        body = json.dumps({"text": "Hi"})
        self.environment.events.request.fire(
            request_type="wss",
            name="Hi",
            response_time=int((time.time() - start_time) * 1000),
            response_length=len(body),
            exception=None,
        )

        self.ws.send(body)

        while not self.end:
            time.sleep(1)

    @task
    def chat_minwook(self):
        start_time = time.time()
        self.end = False
        body = json.dumps(
            {
                "text": "Please tell me who minwook is in one short sentence. For example, minwook is a businessman."
            }
        )
        self.environment.events.request.fire(
            request_type="wss",
            name="Minwook",
            response_time=int((time.time() - start_time) * 1000),
            response_length=len(body),
            exception=None,
        )

        self.ws.send(body)

        while not self.end:
            time.sleep(1)

    @task
    def chat_wrtn(self):
        start_time = time.time()
        self.end = False
        body = json.dumps(
            {"text": "Please give a really short answer to wrtn's devops requirements."}
        )
        self.environment.events.request.fire(
            request_type="wss",
            name="Wrtn",
            response_time=int((time.time() - start_time) * 1000),
            response_length=len(body),
            exception=None,
        )

        self.ws.send(body)

        while not self.end:
            time.sleep(1)

    def on_message(self, message):
        start_time = time.time()
        data = json.loads(message)
        if data["type"] == "end":
            self.end = True
            self.environment.events.request.fire(
                request_type="wss",
                name="end",
                response_time=int((time.time() - start_time) * 1000),
                response_length=0,
                exception=None,
            )

    def on_start(self):
        _, room_pk = load_data(self.host)
        self.connect(room_pk)

    def connect(self, room_pk):
        ws = websocket.create_connection(f"ws://nginx/chat/{room_pk}")
        self.ws = ws
        self.ws_greenlet = gevent.spawn(self.receive_loop)

    def on_quit(self):
        self.ws.close()

    def receive_loop(self):
        start_time = time.time()
        try:
            while True:
                message = self.ws.recv()
                self.on_message(message)
        except Exception as e:
            self.environment.events.request.fire(
                request_type="wss",
                name="end",
                response_time=int((time.time() - start_time) * 1000),
                response_length=0,
                exception=e,
            )