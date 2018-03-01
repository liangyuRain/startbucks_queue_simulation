import abc
from workshop import *
from utils import *
import random

ORDER_TIME_PER_ITEM = 3
TIME_TO_WINDOW = 1


class AbstractModel(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def __init__(self, window_num, worker_num, person_generator):
        self.window_num = window_num
        self.workshop = WorkShop(worker_num)
        self.windows = [Window(ORDER_TIME_PER_ITEM, self.workshop, self) for _ in range(window_num)]
        self.generator = person_generator(self)
        self.people_count = 0
        self.people_served = 0

        def gen():
            try:
                l = next(self.generator)
            except StopIteration:
                return
            if l is not None:
                for p in l:
                    self.enqueue(p)

        time_scheduler.schedule_every_time(gen)

    @abc.abstractmethod
    def enqueue(self, person):
        self.people_count += 1
        person.order_wait_time.start()
        person.total_wait_time.start()

        def served(person):
            self.people_served += 1
            person.total_wait_time.end()

        condition_scheduler.schedule(func(lambda p: p.served, person), func(served, person))

    @abc.abstractmethod
    def dequeue(self, window):
        pass

    @abc.abstractmethod
    def exhausted(self, window):
        pass

    @abc.abstractmethod
    def stat(self):
        pass

    def func_after_ordered(self, window, person, order):
        pass

    def func_after_ready(self, window, person, order):
        pass

    def print_stat(self):
        return """time:\t{0}
people_count:\t{1}
people_served:\t{2}
windows_busy:\t{3}
{4}
{5}
""".format(time_scheduler.time,
           self.people_count,
           self.people_served,
           '\t'.join(['0' if w.available() else '1' for w in self.windows]),
           self.stat(),
           self.workshop.stat())


# Model manage: Person.served,
#               Person.order_wait_time.end(),
#               Person.drink_wait_time.end(),
#               Window.serving,
#               Window.serve(person)


class OneLineModel(AbstractModel):

    def __init__(self, window_num, worker_num, person_generator):
        super(OneLineModel, self).__init__(window_num, worker_num, person_generator)
        self.queue = Queue()

    def enqueue(self, person):
        super(OneLineModel, self).enqueue(person)
        self.queue.put(person)

    def dequeue(self, window):
        if not self.queue.empty():
            person = self.queue.get()
            person.order_wait_time.end()
            window.serving = person
            time_scheduler.schedule((self.windows.index(window) + 1) * TIME_TO_WINDOW,
                                    func(window.serve, person))

    def exhausted(self, window):
        return self.queue.empty()

    def func_after_ready(self, window, person, order):
        person.drink_wait_time.end()
        window.serving = None
        person.served = True

    def stat(self):
        return 'model_queue_length:\t{0}'.format(len(self.queue))


class OneLinePickupModel(AbstractModel):

    PARALLEL_PICKUP = 5
    PICKUP_SPEED_TO_POOL_SIZE = 0.1

    def __init__(self, window_num, worker_num, person_generator):
        super(OneLinePickupModel, self).__init__(window_num, worker_num, person_generator)
        self.queue = Queue()
        self.pickup_order_queue = Queue()
        self.pickup_space = [None for _ in range(OneLinePickupModel.PARALLEL_PICKUP)]
        self.pickup_people_pool = set()

        def pickup_call(pos):
            order = self.pickup_order_queue.get()
            self.pickup_space[pos] = order

            def pickup(order, pos):
                self.pickup_space[pos] = None
                self.pickup_people_pool.remove(order.person)
                order.person.served = True
                order.person.drink_wait_time.end()

            time_scheduler.schedule(round(len(self.pickup_people_pool) *
                                          OneLinePickupModel.PICKUP_SPEED_TO_POOL_SIZE),
                                    func(pickup, order, pos))

        for i in range(len(self.pickup_space)):
            condition_scheduler.schedule_every_time(func(lambda pos: self.pickup_space[pos] is None and
                                                          not self.pickup_order_queue.empty(), i),
                                                    func(pickup_call, i))

    def enqueue(self, person):
        super(OneLinePickupModel, self).enqueue(person)
        self.queue.put(person)

    def dequeue(self, window):
        OneLineModel.dequeue(self, window)

    def exhausted(self, window):
        return self.queue.empty()

    def func_after_ordered(self, window, person, order):
        window.serving = None
        self.pickup_people_pool.add(person)

    def func_after_ready(self, window, person, order):
        self.pickup_order_queue.put(order)

    def stat(self):
        return """model_queue_length:\t{0}
pickup_space_busy:\t{1}
pickup_queue_length:\t{2}
pickup_people_size:\t{3}""".format(len(self.queue),
                                   '\t'.join(['0' if s is None else '1' for s in self.pickup_space]),
                                   len(self.pickup_order_queue),
                                   len(self.pickup_people_pool))


class MultiLineModel(OneLineModel):

    def __init__(self, window_num, worker_num, person_generator):
        super(MultiLineModel, self).__init__(window_num, worker_num, person_generator)
        del self.queue
        self.queues = [Queue() for _ in range(window_num)]

    def enqueue(self, person):
        AbstractModel.enqueue(self, person)
        min_length = min([len(q) for q in self.queues])
        random.choice([q for q in self.queues if len(q) == min_length]).put(person)

    def dequeue(self, window):
        q = self.queues[self.windows.index(window)]
        if not q.empty():
            person = q.get()
            person.order_wait_time.end()
            window.serving = person
            time_scheduler.schedule(TIME_TO_WINDOW, func(window.serve, person))

    def exhausted(self, window):
        return self.queues[self.windows.index(window)].empty()

    def stat(self):
        return 'model_queue_length:\t{0}'.format('\t'.join([str(len(q)) for q in self.queues]))


class MultiLinePickupModel(OneLinePickupModel):

    def __init__(self, window_num, worker_num, person_generator):
        super(MultiLinePickupModel, self).__init__(window_num, worker_num, person_generator)
        del self.queue
        self.queues = [Queue() for _ in range(window_num)]

    def enqueue(self, person):
        MultiLineModel.enqueue(self, person)

    def dequeue(self, window):
        MultiLineModel.dequeue(self, window)

    def exhausted(self, window):
        return MultiLineModel.exhausted(self, window)

    def stat(self):
        return """model_queue_length:\t{0}
pickup_space_busy:\t{1}
pickup_queue_length:\t{2}
pickup_people_size:\t{3}""".format('\t'.join([str(len(q)) for q in self.queues]),
                                   '\t'.join(['0' if s is None else '1' for s in self.pickup_space]),
                                   len(self.pickup_order_queue),
                                   len(self.pickup_people_pool))
