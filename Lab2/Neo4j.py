# This Python file uses the following encoding: utf-8
import random
import threading
import time
import neo4j
import redis
from pip._vendor.distlib.compat import raw_input


def checkSpam(messages, name, forWhom):
    #thread = threading.Thread(target=Check, args=(messages, name, forWhom))
    #thread.start()
    Check(messages, name, forWhom)


def isSpam(message):
    list = worker.base.lrange('spam', 0, -1)
    for item in list:
        if "b'" + message + "'" == str(item):
            return True
    return False


def Check(message, name, forWhom):
    #time.sleep(10)
    mes = message.split(" ")
    count = 0
    for word in mes:
        if isSpam(word):
            count += 1
    if count > 5:
        worker.base.zrem(name, message)

        worker.base.zincrby("spamers", 1, name)
        data = {}
        data[message] = 3.0
        worker.base.zadd(name, data)
        worker.base.zadd(forWhom + '_get', data)
        session.run('create (' + name + ')-[:belongTo]->(spam)')
        session.run(
            "MATCH (a:clients),(b:clients) WHERE a.name = '" + name + "' AND b.name = '" + forWhom + "' CREATE ("
                                                                                                     "a)-["
                                                                                                     'r:messagedSend{'
                                                                                                     'text: \"' +
            message + '\", spam: "true" }]->(b) RETURN type(r), r.name')
    else:
        worker.base.zrem(name, message)
        data = {}
        data[message] = 2.0
        worker.base.zadd(name, data)
        worker.base.zadd(forWhom + '_get', data)
        session.run(
            "MATCH (a:clients),(b:clients) WHERE a.name = '" + name + "' AND b.name = '" + forWhom + "' CREATE ("
                                                                                                     "a)-["
                                                                                                     'r:messagedSend{'
                                                                                                     'text: \"' +
            message + '\", spam: "false"}]->(b) RETURN type(r), r.name')

    '''session.run("MATCH (a:clients),(b:clients) WHERE a.name = '" + name + "' AND b.name = '" + forWhom + "' CREATE ("
                                                                                                       "b)-["
                                                                                                       "r:messagedGet]->(a) RETURN type(r), r.name")'''


def fortag(tags):
    query = 'match (n: clients) where '
    for i in tags:
        query += 'exists {(n)-[:taged]->(t: tags{name: "' + str(i) + '"})} and '

    list1 = list(query)
    list1.pop()
    list1.pop()
    list1.pop()
    list1.pop()
    query = "".join(list1)
    query += 'return (n)'
    res = session.run(query)
    print(query)
    for r in res:
        print(r['n'])


def matchHead(name):
    list = worker.base.smembers("Administrators")
    for names in list:
        if "b'" + name + '\'' == str(names):
            return True
    return False


def matchUsers(name):
    list = worker.base.smembers("Users")
    for names in list:
        if 'b\'' + name + '\'' == str(names):
            return True
    return False


class Worker:
    base = redis.Redis()


def showMessages(name):
    messages = worker.base.zrange(name, 0, -1, withscores=True)
    for message in messages:
        print(message)


def showGotMessages(name):
    messages = worker.base.zrange(name + '_get', 0, -1, withscores=True)
    for message in messages:
        print(message)


def showOnline():
    print(worker.base.hgetall(online))


def showSpamers():
    print(worker.base.zrange("spamers", 0, -1, withscores=True))


def ShortestPath(vertex1, vertex2):
    print(
        'MATCH path=shortestPath((a:clients{name: \'' + vertex1 + '\'})-[:messagedSend]-(b:clients{name: \'' + vertex2 + '\'})) RETURN length(path)')
    res = session.run(
        'MATCH path=shortestPath((a:clients{name: \'' + vertex1 + '\'})-[:messagedSend]-(b:clients{name: \'' + vertex2 + '\'})) RETURN length(path)')
    for r in res:
        print(r['length(path)'])


def vertexByPath(number):
    print('MATCH p=(a:clients)-[messagedSend]-(b:clients)  RETURN (a), (b)')
    res = session.run('MATCH p=(a:clients)-[messagedSend*' + str(number) + ']-(b:clients)  RETURN (a), (b)')
    for r in res:
        print(r['a'])
        print(r['b'])
        print()


def emulate():
    i = 0

    while (i < 20):

        name1 = 'client'
        rand = random.uniform(0, 11)
        if int(rand) == 0:
            name1 = name1
        else:
            name1 = name1 + str(int(rand))
        name2 = 'client'
        a = rand
        while rand == a:
            a = random.uniform(0, 11)
        rand = a
        if int(rand) == 0:
            name2 = name2
        else:
            name2 = 'client' + str(int(rand))

        tag = tags[int(random.uniform(0, len(tags)))]
        data = {}
        message = "someMessage"
        j = 0
        while j < 6:
            message += ' ' + tag
            j += 1
        data[message] = 1
        worker.base.zadd(name1, data)
        checkSpam(message, name1, name2)
        CheckTag(message, name1)

        i = i + 1


def isTag(word):
    for w in tags:
        if w == word:
            return True
    return False


def CheckTag(message, name):
    for word in message.split(' '):
        if isTag(word):
            session.run(
                "MATCH (a:clients),(b:tags) WHERE a.name = '" + name + "' AND b.name = '" + tag + "' CREATE ("
                                                                                                  "a)-["
                                                                                                  "r:taged]->(b) RETURN type(r), r.name")


def notBinded(list):
    query = 'match (n: clients), (b: clients) where'
    for item in list:
        query += ' exists{(n)-[:taged]->(m: tags {name: "' + item + '"}), (b)-[:taged]->(m)} and'
    query += ' not exists {(n)-[:messagedSend]-(b)} return (n), (b)'
    print(query)
    res = session.run(query)
    for r in res:
        print(r['n'])
        print(r['b'])
        print()


def onlySpam():
    query = 'MATCH (a:clients)-[r:messagedSend]->(b:clients) where not exists{(a)-[:messagedSend{spam: "false"}]->(b)} RETURN a, b LIMIT 25'
    res = session.run(query)
    print(query)
    for r in res:
        print(r['a'])
        print(r['b'])
        print()

worker = Worker()
worker.base.sadd("Administrators", "Lider")
worker.base.sadd("Users", "client")
worker.base.sadd("Users", "client1")
worker.base.sadd("Users", "client2")
worker.base.sadd("Users", "client3")
worker.base.sadd("Users", "client4")
worker.base.sadd("Users", "client5")
worker.base.sadd("Users", "client7")
worker.base.sadd("Users", "client6")
worker.base.sadd("Users", "client8")
worker.base.sadd("Users", "client9")
worker.base.sadd("Users", "client10")
# db = neo4j.GraphDatabase('http://localhost:7474", username="neo4j", password=neo4j')
# worker.base.sadd("Адміністратои", "Лідер")
# worker.base.sadd("Адміністраторри", "Gy")
gd = neo4j.GraphDatabase
driver = gd.driver("bolt://localhost:7687", auth=neo4j.basic_auth("neo4j", "password"), encrypted=False)
session = driver.session()
'''for user in worker.base.smembers("Users"):
    nameLikeList = list(str(user))
    nameLikeList.pop()
    nameLikeList.pop(0)
    nameLikeList.pop(0)
    name = "".join(nameLikeList)
    session.run("create (" + name + ": clients {name: \'" + name + "\'})")'''

online = "online"

tags = ["institute", 'db', 'session', 'mark', 'action']

'''for user in tags:
    name = user
    session.run("create (" + user + ": tags {name: \'" + user + "\'})")'''

pubsub = worker.base.pubsub()
for tag in tags:
    worker.base.lpush('spam', tag)
# list = worker.base.lrange('spam', 0, -1)
# print(list)
print("Увійти як: 1 - звичайний користувач, 2 - адміністратор")
if (input()) == "1":
    print("Ім'я")
    name = input()
    if matchUsers(name):
        worker.base.hset(online, name, "true")
        print("Ласкаво просимо")
        while True:
            print("Обрати опцію: 1 - написати повідомлення, 2 - переглянути чергу відправлених вами повідомлень, "
                  "3 - подивитися список отриманих повідомлень\n, 4 - підписка, 5 - зробити публікацію, "
                  "6 - вийти")
            choice = int(input())
            if choice == 1:
                print("Ваше повідомлення: \n")
                messageSend = input()
                print("Кому: ")
                forWhom = input()
                data = {}
                data[messageSend] = 1.0
                worker.base.zadd(name, data)
                checkSpam(messageSend, name, forWhom)
                CheckTag(messageSend, name)
            if choice == 2:
                showMessages(name)
            if choice == 3:
                showGotMessages(name)
            if choice == 4:

                print("1 - підписатися, інше - отримати публікації")
                choice = int(input())
                if choice == 1:
                    print("Ім'я корстувача: ")
                    pub = input()
                    pubsub.subscribe(pub)
                else:
                    try:

                        print(pubsub.get_message()['data'])
                    except Exception:
                        print()

            if choice == 5:
                worker.base.publish(name
                                    , input())
            if choice == 6:
                worker.base.hset(online, name, "false")
                break
else:
    print("Увійти як адміністратор. Ім'я: ")
    # print(worker.base.smembers("Адміністратори"))

    name = input()
    if matchHead(name):
        print("Ласкаво просимо")
        while True:
            print("Обрати опцію: 1 - подивитися користувачів в мережі, 2 - подивитися активність спаму, 3 - емуляція, 4 - завдання 1, 5 - завдання 2, 6 - завдання 3\n, 7 - завдання 4, 8 - завдання 5")
            choice = int(input())
            if choice == 1:
                showOnline()
            if choice == 2:
                showSpamers()
            if choice == 3:
                try:
                    emulate()
                except Exception:
                    print()
            if choice == 4:
                print("Кількість")
                number = int(input())
                print("Почергове введення")
                list2 = []
                for i in range(0, number):
                    list2.append(input())
                fortag(list2)
            if choice == 5:
                print("Користувач1")
                vertex1 = input()
                print("Користувач2")
                vertex2 = input()
                ShortestPath(vertex1, vertex2)
            if choice == 6:
                print("Номер")
                number = int(input())
                vertexByPath(number)
            if choice == 7:
                print("Кількість")
                number = int(input())
                print("Почергове введення")
                list2 = []
                for i in range(0, number):
                    list2.append(input())
                notBinded(list2)
            if choice == 8:
                    onlySpam()