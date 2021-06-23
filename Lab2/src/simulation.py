from random import randint
from threading import Thread
from faker import Faker
import redis
from controller import Controller

class User(Thread):
    def __init__(self, connection, username, users_list, users_count, controller):
        Thread.__init__(self)
        self.connection = connection
        self.users_list = users_list
        self.users_count = users_count
        controller.registration(username)
        self.user_id = controller.log_in(username, connection.hget("users:", username))

    def run(self):
        while True:
            message_text = fake_users.sentence(nb_words=10, variable_nb_words=True, ext_word_list=None)
            receiver = users[randint(0, count_users - 1)]
            controller.new_message(message_text, self.user_id, self.connection.hget("users:", receiver))


if __name__ == '__main__':
    fake_users = Faker()
    count_users = 5
    users = [fake_users.profile(fields=['username'], sex=None)['username'] for u in range(count_users)]
    threads = []
    controller = Controller()
    for x in range(count_users):
        print(users[x])
        threads.append(User(
            redis.Redis(charset="utf-8", decode_responses=True),
            users[x], users, count_users, controller))
    for t in threads:
        t.start()

    connection = redis.Redis(charset="utf-8", decode_responses=True)
    online = connection.smembers("online:")
    for member in online:
        connection.srem("online:", member)
    print("Ctrl+C to exit")