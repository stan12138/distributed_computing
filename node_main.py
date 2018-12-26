from net import Client


node = Client("10.112.145.120", 3000)



while True :
    s = input(">> ")
    if s=="stop" :
        break
    node.send(s)