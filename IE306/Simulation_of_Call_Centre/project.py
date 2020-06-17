import simpy
import random
import numpy
import math

# initialize a set of globals that define the characteristics of the model instance to be simulated.
# which includes the random seed list for the random number generators, and key parameters for the interarrival
# and service time distribution.
interarrival_mean = 6
interarrival_rate = 1.0 / interarrival_mean
record_mean = 5 # record and collect the details of the caller, exp_distributed
record_rate = 1.0 / record_mean
service_range_2 = [1, 7] # operator 2 uniformly distributed
breaktime = 3   # 3 min break time duration
breaktime_rate = 1.0 / 60
opt1_mean = math.log(144/math.sqrt(180))    # opt1 log normally dist. with 12 mean
opt1_std = math.sqrt(math.log(1+(36/144)))
random_seed_list = [978, 900, 800, 700, 550, 657, 723, 129, 1000, 324]  #

class Customer(object):
    def __init__(self, name, env, opt1, opt2): #initialize
        self.env = env
        self.name = name
        self.arrival_t = self.env.now   #customer is arriving now
        self.action = env.process(self.call())  # call process begins

    def call(self): #customer call
        total_cust.append(self.name)    # total customers who call the system
        customers_answ.append(self.name) #the customers in the answering system
        if len(customers_answ) <=100:    # the system has maximum 100 parallel answering channels
            yield self.env.process(self.collect_info()) # collecting info process begins
            self.ans_system_done = self.env.now

            rand = random.random() #used for prob. of operators
            rand_mis = random.random() #used for prob. of routing the call to the wrong operator(mistake)
            #operator 1's prob. = 0.3, operator 2's prob. = 0.7, wrong operator mistake prob. = 0.1
            if rand < 0.3 and rand_mis > 0.1:
                #caller is routed to operator 1.
                operator1_q.append(1)   #The important thing is nothing but queue's length, so just append 1
                avg_num_opt.append(len(operator1_q))
                with opt1.request() as req:
                    yield req
                    if 10 >= self.env.now - self.ans_system_done: #arriving customer can wait at most 10 min
                        queue_w_times.append(self.env.now - self.ans_system_done) #keeps the waiting time of each customer
                        yield self.env.process(self.ask_question_1())
                    else:
                        queue_w_times.append(10) #wait time is reached 10 min so customer hangs up the phone
                        operator1_q.pop()
                        avg_num_opt.append(len(operator1_q))
                        unsatisfied.append(self.name)   #keeps the unsatisfied customers

            elif rand >= 0.3 and rand_mis > 0.1: #same process as in the operator 1, only probability is changing
                operator2_q.append(1)
                avg_num_opt.append(len(operator2_q))
                with opt2.request() as req:
                    yield req
                    if  10 >= self.env.now - self.ans_system_done:
                        queue_w_times.append(self.env.now - self.ans_system_done)
                        yield self.env.process(self.ask_question_2())
                    else:
                        queue_w_times.append(10)
                        operator2_q.pop()
                        avg_num_opt.append(len(operator2_q))
                        unsatisfied.append(self.name)
            else:
                unsatisfied.append(self.name) #customers routed to the wrong operator

        else:
            customers_answ.pop(0)   #customer can not connect to the system because of the 100 channel limit

    def collect_info(self): #the process for collecting and recording the details of the caller
        duration = random.expovariate(record_rate)
        while duration < 0:
            duration = random.expovariate(record_rate) #total time spent for collecting the necessary info of the caller
        answering_time.append(duration)
        yield self.env.timeout(duration)
        customers_answ.pop(0)    #customer's info is collected and it is ready for routing an operator

    def ask_question_1(self):   #the process for asking to operator 1
        duration = numpy.random.lognormal(opt1_mean, opt1_std)
        while duration < 0:
            duration = numpy.random.lognormal(opt1_mean, opt1_std)

        operator1_q.pop(0)
        avg_num_opt.append(len(operator1_q))
        yield self.env.timeout(duration)
        service1_times.append(duration) #keeps service time of each customer, operator's job with the customer is done

    def ask_question_2(self):   #the process for asking to operator 2
        duration = random.uniform(*service_range_2)
        while duration < 0:
            duration = random.uniform(*service_range_2)

        operator2_q.pop(0)
        avg_num_opt.append(len(operator2_q))
        yield self.env.timeout(duration)
        service2_times.append(duration)

def customer_generator(env, opt1, opt2):
    """Generate new customers who call the call centre."""
    for i in range(custom_count):
        yield env.timeout(random.expovariate(interarrival_rate))
        customer = Customer('Cust %s' %(i+1), env, opt1, opt2)

def break_generator1(env, opt1):
    """Generate breaks for operator 1"""
    while True:
        if len(total_cust) == custom_count: #Checks if all customers called the call centre.
            break
        if (len(operator1_q) == 0): #if operator does not have any waiting customer, gives a break
            yield env.timeout(random.expovariate(breaktime_rate))
            with opt1.request() as req:
                yield req
                yield env.timeout(breaktime)
        else:
            break

def break_generator2(env, opt2):
    """Generate breaks for operator 2"""
    while True:
        if len(total_cust) == custom_count:
            break
        if (len(operator2_q) == 0):
            yield env.timeout(random.expovariate(breaktime_rate))
            with opt2.request() as req:
                yield req
                yield env.timeout(breaktime)
        else:
            break

for j in range(2): #simulation of the project
    #resets the necessary set of arrays used for statistics in 1000 and 5000 calls.
    all_utilize_answer_sys = []
    all_util_operators = []
    all_wait_time = []
    all_wait_time_ratio = []
    all_avg_people_waiting_opt = []
    all_unsatisfied = []
    if(j == 0):
        custom_count = 1000
        print("Statistics of the simulation for 1000 call")
    else:
        custom_count = 5000
        print()
        print("Statistics of the simulation for 5000 call")
    for i in range(10):

        #resets the necessary set of arrays in each run
        queue_w_times = [] #Time spent by a customer while it waits for the operator (Queue waiting time Wq)
        service1_times = [] #Duration of the conversation between the customer and the operator1 (Service time)
        service2_times = [] #Duration of the conversation between the customer and the operator2 (Service time)
        answering_time = [] #answering system utilization
        total_cust = [] #total customers called the call centre
        customers_answ = []  #customers in the answering system
        operator1_q = []    #customers in the operator 1's queue
        operator2_q = []    #customers in the operator 2's queue
        avg_num_opt = []    #customers in the operators' queue
        unsatisfied = []    #unsatisfied customers
        random.seed(random_seed_list[i])
        env = simpy.Environment()
        opt1 = simpy.Resource(env, capacity = 1)
        opt2 = simpy.Resource(env, capacity = 1)
        env.process(customer_generator(env, opt1, opt2))
        env.process(break_generator1(env, opt1))
        env.process(break_generator2(env, opt2))

        env.run()
        #necessary informations used to report the statistics in each run
        all_utilize_answer_sys.append(sum(answering_time)/custom_count)
        all_util_operators.append((sum(service1_times)+sum(service2_times))/env.now)
        all_wait_time.append(sum(queue_w_times))
        all_wait_time_ratio.append(sum(queue_w_times)/env.now)
        all_avg_people_waiting_opt.append(sum(avg_num_opt)/len(avg_num_opt))
        all_unsatisfied.append(len(unsatisfied))

    #prints the results of 1000 and 5000 calls
    print("Utilization of the answering system: " ,sum(all_utilize_answer_sys)/10)
    print("Utilization of the operators: ", sum(all_util_operators)/10)
    print("Average Total Waiting Time: ",sum(all_wait_time)/10)
    print("Maximum Total Waiting Time to Total System Time Ratio: ",max(all_wait_time_ratio))
    print("Average number of people waiting to be served by each operator: ",sum(all_avg_people_waiting_opt)/10)
    print("Average number of customers leaving the system unsatisfied: ",sum(all_unsatisfied)/10)
