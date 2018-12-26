import time
import os

__all__ = ["Work"]

class Work :
    def run(self, *args) :
        with open(args[0][0]+"ttt.txt", "wb") as fi:
            sleep_time = 10
            #print("this is process %s"%os.getpid(), "going to sleep %s seconds"%sleep_time)
            time.sleep(sleep_time)

            fi.write(str(sleep_time).encode("utf-8"))

        return os.getpid(),sleep_time