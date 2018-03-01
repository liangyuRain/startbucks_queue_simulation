class Timer:

    timer_list = set()

    def __init__(self, initial=0):
        self.time = initial

    def start(self):
        assert self not in Timer.timer_list
        Timer.timer_list.add(self)

    def end(self):
        Timer.timer_list.remove(self)

    def __repr__(self):
        return str(self.time)


class Queue(list):

    def put(self, p):
        self.append(p)

    def get(self):
        return self.pop(0)

    def empty(self):
        return self.__len__() == 0


class Item:

    def __init__(self, name, time_cost, popularity):
        self.name = name
        self.time_cost = time_cost
        self.popularity = popularity

    def __repr__(self):
        return str(self.name)


class Person:
    people_list = []

    def __init__(self, name, items):
        self.name = name
        self.items = items
        self.ordered = False
        self.served = False
        self.order_wait_time = Timer()
        self.drink_wait_time = Timer()
        self.total_wait_time = Timer()
        Person.people_list.append(self)

    def __repr__(self):
        return str(vars(self))


class Order:
    order_list = []

    def __init__(self, num, person):
        self.num = num
        self.person = person
        self.items = person.items
        self.ready = False
        self.priority_queue = Queue(sorted(person.items, key=lambda i: i.time_cost, reverse=True))
        self.ready_num = 0
        self.wait_time = Timer()
        Order.order_list.append(self)

    def __repr__(self):
        dic = vars(self).copy()
        del dic['priority_queue']
        del dic['items']
        return str(dic)


class TimeScheduler:

    def __init__(self):
        self.time_line = Queue()
        self.every_time = {}
        self.counter = 0
        self.time = 0

    def schedule_every_time(self, func):
        self.counter += 1
        self.every_time[self.counter] = func
        return self.counter

    def unschedule_every_time(self, index):
        assert index in self.every_time
        del self.every_time[index]

    def schedule(self, delay, func):
        delay = int(delay)
        if delay == 0:
            func()
        else:
            index = delay - 1
            self.time_line += [[] for _ in range(index + 1 - len(self.time_line))]
            self.time_line[index].append(func)

    def time_pass(self):
        self.time += 1
        for t in Timer.timer_list:
            t.time += 1
        tmp1 = self.time_line.get() if not self.time_line.empty() else []
        tmp2 = self.every_time.copy().values()
        for func in tmp1:
            if func is list:
                for f in func:
                    f()
            else:
                func()
        for func in tmp2:
            if func is list:
                for f in func:
                    f()
            else:
                func()


class ConditionScheduler:

    def __init__(self):
        self.conditions = []
        self.every_time = {}
        self.counter = 0

    def schedule_every_time(self, condition, func):
        self.counter += 1
        self.every_time[self.counter] = (condition, func)
        return self.counter

    def unschedule_every_time(self, index):
        assert index in self.every_time
        del self.every_time[index]

    def schedule(self, condition, func):
        self.conditions.append((condition, func))

    def time_pass(self):
        no_end = True
        while no_end:
            no_end = False
            tmp1 = self.conditions.copy()
            tmp2 = self.every_time.copy().values()
            self.conditions = []
            for t in tmp1:
                if t[0]():
                    if t[1] is list:
                        for f in t[1]:
                            f()
                    else:
                        t[1]()
                    no_end = True
                else:
                    self.conditions.append(t)
            for t in tmp2:
                if t[0]():
                    if t[1] is list:
                        for f in t[1]:
                            f()
                    else:
                        t[1]()
                    no_end = True


time_scheduler = TimeScheduler()
condition_scheduler = ConditionScheduler()
