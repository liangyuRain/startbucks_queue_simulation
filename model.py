import numpy as np
from queue_models import *
import sys

SECOND_PER_PERSON = 5

NUM_OF_WINDOW = 2
NUM_OF_WORKER = 5

item_list = []

with open('Data.csv') as fin:
    for l in fin:
        arr = l.split(',')
        item_list.append(Item(arr[0], int(arr[1]), float(arr[2])))

pops = np.array([item.popularity for item in item_list])
probs = pops / np.sum(pops)
item_num_distribution = np.array([73, 19, 5, 3])

lambdas = []

def generator(model):
    alpha = 1 / SECOND_PER_PERSON
    beta = np.log(2) / 15
    items_per_person = np.sum(item_num_distribution *
                              np.arange(1, (item_num_distribution.shape[0] + 1))) / np.sum(item_num_distribution)
    accumulate = 0
    person_num = 0
    while True:
        lam = alpha * np.exp(-beta * (model.people_count - model.people_served))
        lambdas.append(lam)
        accumulate += np.random.poisson(lam)
        l = []
        while accumulate >= 1:
            accumulate -= 1
            person_num += 1
            p = Person(person_num, [])
            for _ in range(np.random.poisson(items_per_person - 1) + 1):
                p.items.append(np.random.choice(item_list, p=probs))
            l.append(p)
        yield l


def run_model(model, simulation_time):
    print(type(model).__name__)
    for _ in range(simulation_time):
        # print(model.print_stat())
        # if time_scheduler.time % 60 == 0:
        #     input()
        time_scheduler.time_pass()
        condition_scheduler.time_pass()
    print(model.print_stat())

    print('total_people_arrived:\t{0}'.format(model.people_count))
    print('total_people_served:\t{0}'.format(model.people_served))
    print('total_order_placed:\t{0}'.format(model.workshop.order_count))
    print('total_order_finished:\t{0}'.format(model.workshop.order_finished))
    total_wait_time = np.array([p.total_wait_time.time for p in Person.people_list if p.served])
    print('total_wait_time_avg:\t{0}\ttotal_wait_time_std:\t{1}'.format(round(np.average(total_wait_time), 2),
                                                                        round(np.std(total_wait_time), 2)))
    drink_wait_time = np.array([p.drink_wait_time.time for p in Person.people_list if p.served])
    print('drink_wait_time_avg:\t{0}\tdrink_wait_time_std:\t{1}'.format(round(np.average(drink_wait_time), 2),
                                                                        round(np.std(drink_wait_time), 2)))
    order_wait_time = np.array([p.order_wait_time.time for p in Person.people_list if p.served])
    print('order_wait_time_avg:\t{0}\torder_wait_time_std:\t{1}'.format(round(np.average(order_wait_time), 2),
                                                                        round(np.std(order_wait_time), 2)))
    order_cost_time = np.array([o.wait_time.time for o in Order.order_list if o.ready])
    print('order_cost_time_avg:\t{0}\torder_cost_time_std:\t{1}'.format(round(np.average(order_cost_time), 2),
                                                                        round(np.std(order_cost_time), 2)))
    total_item_num = np.sum(np.array([len(p.items) for p in Person.people_list if p.served]))
    print('average_time_per_item_ordered:\t{0}'.format(round(np.sum(total_wait_time) / total_item_num, 2)))
    assert total_item_num <= np.sum(np.array([len(o.items) for o in Order.order_list if o.ready]))
    print('average_lambda:\t{0}'.format(round(np.average(lambdas), 2)))
    print()


if __name__ == '__main__':
    assert len(sys.argv) == 2, 'illegal arguments'
    simulation_time = int(sys.argv[1])
    models = [OneLineModel,
              OneLinePickupModel,
              MultiLineModel,
              MultiLinePickupModel]
    for m in models:
        time_scheduler.reset()
        condition_scheduler.reset()
        Person.reset()
        Order.reset()
        lambdas.clear()
        run_model(m(window_num=NUM_OF_WINDOW, worker_num=NUM_OF_WORKER, person_generator=generator),
                  simulation_time)
