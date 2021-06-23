import redis
import datetime
import logging
from view import UserView, AdminView
from conectionlistener import ConnectionListener


class Controller:
    def __init__(self):
        self.connection = redis.Redis(charset="utf-8", decode_responses=True)
        logging.basicConfig(filename="events.log", level=logging.INFO)

    def registration(self, username):
        if self.connection.hget('users:', username):
            print(f"Sorry, but user with this username: \"{username}\" already exists")
            self.connection.publish('users',
                               f"{datetime.datetime.now()}: Registration: Registration failure. Username \"{username}\" already exists\n")

            return

        pipeline = self.connection.pipeline(True)
        user_id = self.connection.incr('user:id:')
        pipeline.hset('users:', username, user_id)
        pipeline.hmset('user:%s' % user_id, {
            'username': username,
            'user_id': user_id,
            'in_queue': 0,
            'need_to_check': 0,
            'blocked_for_spam': 0,
            'sent_to_user': 0,
            'delivered_to_user': 0
        })
        pipeline.execute()

        self.connection.publish('users',
                           f"{datetime.datetime.now()}: Registration: Registration successful. \"{username}\" registered\n")

        return user_id

    def log_in(self, username, user_id):
        if not user_id:
            print(f"Sorry, there is no registered user with username: {username}")
            self.connection.publish('users',
                               f"{datetime.datetime.now()}: Log in: Log in failure. \"{username}\" does not exist\n")
            return -1

        self.connection.sadd("online:", username)
        self.connection.publish('users', f"{datetime.datetime.now()}: Log in: Log in successful. \"{username}\" logged in\n")

        return int(user_id)

    def log_out(self, username):
        self.connection.publish('users',
                           f"{datetime.datetime.now()}: Log out: Log out successful. \"{username}\" logged in\n")

        return self.connection.srem("online:", username)

    def new_message(self, message_text, sender_id, consumer_id):
        if not consumer_id:
            print("Current user does not exist %s, unable to send message"
                  % self.connection.hmget("user:%s" % consumer_id, ["username"])[0])

            return

        message_id = int(self.connection.incr('message:id:'))

        pipeline = self.connection.pipeline(True)
        pipeline.hmset('message:%s' % message_id, {
            'message_text': message_text,
            'message_id': message_id,
            'message_sender_id': sender_id,
            'message_consumer_id': consumer_id,
            'message_status': "created"
        })
        pipeline.lpush("in_queue:", message_id)
        pipeline.hmset('message:%s' % message_id, {
            'status': 'in_queue'
        })
        pipeline.zincrby("sent_to_user:", 1, "user:%s" % self.connection.hmget("user:%s" % sender_id, ["username"])[0])
        pipeline.hincrby("user:%s" % sender_id, "in_queue", 1)
        pipeline.execute()

        return message_id

    def show_messages(self, user_id):
        messages = self.connection.smembers("sentto:%s" % user_id)
        for message_id in messages:
            message = self.connection.hmget("message:%s" % message_id,
                                       ["message_sender_id", "message_text", "message_status"])
            print("From: %s - %s" % (self.connection.hmget("user:%s" % message[0], ["username"])[0], message[1]))

            if message[2] != "delivered_to_user":
                pipeline = self.connection.pipeline(True)
                pipeline.hset("message:%s" % message_id, "status", "delivered_to_user")
                pipeline.hincrby("user:%s" % message[0], "sent_to_user", -1)
                pipeline.hincrby("user:%s" % message[0], "delivered_to_user", 1)
                pipeline.execute()

    def start_user(self):
        connection_listener = ConnectionListener(self.connection)
        connection_listener.setDaemon(True)
        connection_listener.start()

        logged_in = False
        this_user_id = -1
        user_view = UserView()

        while True:
            if not logged_in:
                user_view.main_menu()
                option = int(input("=> "))

                if option == 1:
                    username = input("Enter your username: ")
                    self.registration(username)

                elif option == 2:
                    username = input("Enter your username: ")
                    this_user_id = self.log_in(username, self.connection.hget("users:", username))
                    logged_in = this_user_id != -1

                elif option == 3:
                    break

                else:
                    print("No such option. Please write number from 1 to 3")

            else:
                user_view.user_menu()
                option = int(input("=> "))

                if option == 1:
                    message = input("Enter your message: ")
                    receiver_text = input("Enter username of receiver: ")

                    receiver = self.connection.hget("users:", receiver_text)
                    if receiver is not None:
                        self.new_message(message, this_user_id, int(receiver))
                        print("Message is waiting to be processed")
                    else:
                        print("Sorry, there is no such user")

                elif option == 2:
                    self.show_messages(this_user_id)

                elif option == 3:
                    this_user = self.connection.hmget("user:%s" % this_user_id,
                                                 ['in_queue', 'need_to_check', 'blocked_for_spam', 'sent_to_user',
                                                  'delivered_to_user'])
                    print(
                        "In queue: %s\nNeed to check: %s\nBlocked for spam: %s\nSent to user: %s\nDelivered to user: %s" %
                        tuple(this_user))

                elif option == 4:
                    username = self.connection.hmget("user:%s" % this_user_id, ["username"])[0]
                    self.log_out(username)
                    logged_in = False
                    this_user_id = -1

                else:
                    print("No such option. Please write number from 1 to 4")

    def start_admin(self):
        admin_view = AdminView()

        while True:
            admin_view.admin_menu()
            option = int(input("=> "))

            if option == 1:
                print("Users online:")

                online_users = self.connection.smembers("online:")
                for user in online_users:
                    print(user)

            elif option == 2:
                N = int(input("Enter number of top senders: "))
                print("Top %s senders: " % N)

                senders = self.connection.zrange("sent_to_user:", 0, N - 1, desc=True, withscores=True)
                for index, sender in enumerate(senders):
                    print(f"{sender[0]} - {int(sender[1])} messages")

            elif option == 3:
                N = int(input("Enter number of top spammers: "))
                print("Top %s spammers: " % N)

                spammers = self.connection.zrange("spam:", 0, N - 1, desc=True, withscores=True)
                for index, spammer in enumerate(spammers):
                    print(f"{spammer[0]} - {int(spammer[1])} spam messages")

            elif option == 4:
                n = int(input("Write number of last rows to show: "))
                with open("events.log") as file:
                    print("Last %s lines of logs: " % N)
                    for line in file.readlines()[-n:]:
                        print(line)

            elif option == 5:
                break

            else:
                print("No such option. Please write number from 1 to 5")

