import threading
import multiprocessing as mp
import work
from imp import reload
import os
from protocol import Consumer_parser

from net import Client


class Consumer(Client) :
    def __init__(self, ip, port, pool, nums) :
        Client.__init__(ip, port)
        self.parser = Consumer_parser(stop_method, args_handler)
        self.pool = pool
        self.nums = nums

        self.connect()
        self.parser.send_type(self.client)

    def get_args(self, args):
        pass

    def stop_current_work(self) :
        self.pool.terminate()
        self.pool = mp.Pool(4)



    def do_work(self, args) :
        try :
            reload(work)
            a = work.Work()
            res = a.run(args)
        except Exception as er :
            pass

    def callback(self) :
        pass










def processing_work(*args) :
    print("%s add work"%os.getpid(), args)
    try :
        reload(work)
        a = work.Work()

        res = a.run(args)
    except Exception as er :
        res = str(er)

    return res


def processing_callback(args) :
    print(args, "%s is done"%os.getpid())

def processing_erro(args) :
    print(args)

def work_process(pool) :
    pass

def watcher(pool) :
    pass

if __name__ == '__main__':
    pool = mp.Pool(4)

    while True :
        a = input(">> ")
        if a=="stop" :
            print("get stop......")
            pool.terminate()
            break
        else :
            print("add one work")
            pool.apply_async(func=processing_work, args=(a, ), callback=processing_callback)