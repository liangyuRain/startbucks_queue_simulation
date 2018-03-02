from utils import *
from inspect import signature


def func(f, *args, **kwargs):
    return lambda: f(*args[:min(len(signature(f).parameters), len(*args))], **kwargs)


class WorkShop:

    def __init__(self, worker_num):
        self.worker_num = worker_num
        self.queue = Queue()
        condition_scheduler.schedule_every_time(lambda: not self.queue.empty() and self.queue[0].priority_queue.empty(),
                                                self.queue.get)
        self.completed_order = []
        self.order_count = 0
        self.order_finished = 0
        self.workers = [[True, None, None] for _ in range(worker_num)]

        def end_worker(worker, order):
            order.ready_num += 1
            worker[0] = True
            worker[1] = None
            worker[2] = None

        def begin_work(worker):
            worker[0] = False
            worker[1] = self.queue[0].priority_queue.get()
            worker[2] = self.queue[0]
            time_scheduler.schedule(worker[1].time_cost, func(end_worker, worker, self.queue[0]))

        for worker in self.workers:
            condition_scheduler.schedule_every_time(
                func(lambda w: w[0] and not self.queue.empty() and not self.queue[0].priority_queue.empty(), worker),
                func(begin_work, worker)
            )

    def enqueue(self, person):
        if person is None:
            return
        self.order_count += 1
        order = Order(self.order_count, person)
        self.queue.put(order)
        order.wait_time.start()

        def ready(order):
            order.ready = True
            self.order_finished += 1
            self.completed_order.append(order)
            order.wait_time.end()

        condition_scheduler.schedule(func(lambda o: o.ready_num == len(o.items), order), func(ready, order))
        return order

    def stat(self):
        return 'workshop_queue_length:\t{0}\nworkers_busy:\t{1}'.format(len(self.queue),
                                                                        '\t'.join(['0' if w[0] else '1'
                                                                                   for w in self.workers]))

    def __repr__(self):
        return self.queue.__repr__()


class Window:
    RAPID_PICKUP = True
    RAPID_TIME_STANDARD = 10
    CASHIER_TIME_COST = 10

    def __init__(self, order_time_per_item, workshop, model):
        self.serving = None
        self.time_per_item = order_time_per_item
        self.workshop = workshop
        self.model = model
        condition_scheduler.schedule_every_time(lambda: self.serving is None and not self.model.exhausted(self),
                                                lambda: self.model.dequeue(self))

    def serve(self, person):
        if person is None:
            return
        self.serving = person

        def enqueue(person):
            person.ordered = True
            order = self.workshop.enqueue(person)
            person.drink_wait_time.start()
            condition_scheduler.schedule(func(lambda o: o.ready, order),
                                         func(self.model.func_after_ready,
                                              self, person, order))

            if Window.RAPID_PICKUP:
                q = Queue()
                while not order.priority_queue.empty() and \
                        order.priority_queue[-1].time_cost <= Window.RAPID_TIME_STANDARD:
                    item = order.priority_queue.pop(-1)
                    q.put(item)

                def work(order, q):
                    order.ready_num += 1
                    if not q.empty():
                        item = q.get()
                        time_scheduler.schedule(item.time_cost, func(work, order, q))
                    else:
                        func(self.model.func_after_ordered, self, person, order)()

                if not q.empty():
                    item = q.get()
                    time_scheduler.schedule(item.time_cost, func(work, order, q))
                    return
            func(self.model.func_after_ordered, self, person, order)()

        time_scheduler.schedule(self.time_per_item * len(person.items) + Window.CASHIER_TIME_COST,
                                func(enqueue, person))

    def available(self):
        return self.serving is None

    def __repr__(self):
        return str(vars(self))
