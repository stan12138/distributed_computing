import threading
import multiprocessing as mp
import work
from imp import reload
import os


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