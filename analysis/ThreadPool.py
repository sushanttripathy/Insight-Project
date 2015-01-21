__author__ = 'Sushant'

import threading
import time


class ThreadPool(object):
    def __init__(self, num_threads=8):
        self.num_threads = num_threads
        self.threads = []
        self.events = []

        self.main_event = threading.Event()
        self.main_thread = threading.Thread(target=self.pool_leader, args=[])
        self.acknowledge_event = threading.Event()

        self.work_queue = []

        for i in range(0, self.num_threads):
            ev = threading.Event()
            self.events.append(ev)
            th = threading.Thread(target=self.thread_handler, args=[i, ev])
            th.start()

        self.main_thread.start()


    def find_free_thread(self):
        while 1:
            for i in range(0, self.num_threads):
                if not self.events[i].is_set():
                    return i
            time.sleep(0.2)
        return None

    def pool_leader(self):
        while self.main_event.wait():
            self.main_event.clear()
            while len(self.work_queue):
                t = self.find_free_thread()
                if t is not None:
                    self.events[t].set()
                    self.acknowledge_event.wait()
                    self.acknowledge_event.clear()


    def push_work(self, func, args):
        self.work_queue.append((func, args))
        self.main_event.set()


    def thread_handler(self, thread_num, thread_ev):
        # print "Initiating thread "+`thread_num`
        while thread_ev.wait():
            func, args = self.work_queue.pop()
            self.acknowledge_event.set()
            #print "Thread "+`thread_num`+" activated!"
            #print(args)
            func(*args)
            thread_ev.clear()

"""
def f(a, b):
    print a + b


th = ThreadPool()

for i in range(0, 9):
    th.push_work(func=f, args=[i, 1])

while 1:
    pass

"""