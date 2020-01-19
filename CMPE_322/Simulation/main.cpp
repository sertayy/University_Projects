/*
 * Implemented by Sertay Akpinar, 02.01.2020 ®
 */

#include <iostream>
#include <pthread.h>
#include <fstream>
#include <thread>         // std::this_thread::sleep_for
#include <chrono>         // std::chrono::seconds
#include <queue>
using namespace std;
void *atm_threads(void *param);
void *customer_threads(void *param);
int number_of_cust; //number of the customers
int electric;
int gas;
int cableTv;
int telecom;
int water;
int max_sleep;  //maximum sleep time among the customers
pthread_mutex_t atm_ = PTHREAD_MUTEX_INITIALIZER;   //mutex for atm
pthread_mutex_t cust = PTHREAD_MUTEX_INITIALIZER;   //mutex for customer
pthread_mutex_t g = PTHREAD_MUTEX_INITIALIZER; //mutex for gas
pthread_mutex_t cable = PTHREAD_MUTEX_INITIALIZER;
pthread_mutex_t elec = PTHREAD_MUTEX_INITIALIZER;
pthread_mutex_t wat = PTHREAD_MUTEX_INITIALIZER;
pthread_mutex_t tele = PTHREAD_MUTEX_INITIALIZER;

struct customer{        //necessary data for customer
    int sleep;
    string billtype;
    int atm_instance;
    int amount;
    int index;
};

struct atm{         //necessary data for atm
    queue<customer> atm_queue;
    int ind;
};
ofstream output;
atm atm_array[10];  //queue array

int main(int argc, char* argv[]) {
    string line;
    ifstream infile(argv[1]); //one for customer data
    ifstream in1file(argv[1]);  // one for finding the maximum sleep among the customers
    string file = argv[1];
    file = file.substr(0,file.find("."));
    file.append("_log.txt");    //to create the <input_name>_log.txt file
    output.open(file);
    infile >> number_of_cust;
    pthread_t atms[10];
    //I found the maximum sleep time among the customers via this for loop
    max_sleep =0;
    for(int i=0; i<number_of_cust; i++){
        in1file >> line;
        if(max_sleep < stoi(line.substr(0,line.find(",")))){
            max_sleep = stoi(line.substr(0,line.find(",")));
        }
    }
    for (int i = 0; i < 10; i++) {
        atm_array[i].ind = i;
        pthread_create(&atms[i], 0, atm_threads, &atm_array[i].ind);    //creates the atm threads and sends the each atms index's address
    }
    pthread_t customs[number_of_cust];
    customer customers[number_of_cust];
    //In the first for loop implemented below, I identified each customer's data according to the input file by using substr()
    //after that I created the customer thread and send each customer's address
    for(int i=0; i<number_of_cust;i++) {
        infile >> line;
        string temporary;
        customers[i].index = i+1;
        customers[i].sleep = stoi(line.substr(0, line.find(",")));
        temporary = line.substr(0, line.find(","));
        line = line.substr(temporary.size()+1);
        if(max_sleep<customers[i].sleep){
            max_sleep = customers[i].sleep;
        }
        customers[i].atm_instance = stoi(line.substr(0, line.find(",")));
        temporary = line.substr(0, line.find(","));
        line = line.substr(temporary.size()+1);
        customers[i].billtype = line.substr(0, line.find(","));
        temporary = line.substr(0, line.find(","));
        line = line.substr(temporary.size()+1);
        customers[i].amount = stoi(line.substr(0, line.find(",")));
        pthread_create(&customs[i], 0, customer_threads, &customers[i]);
    }
    for (int i = 0; i < 10; i++) {
        pthread_join(atms[i], NULL);
    }
    for(int i=0; i<number_of_cust;i++) {
        pthread_join(customs[i],NULL);
    }
    output<<"All payments are completed"<<endl;
    output<<"CableTV:"<< cableTv <<endl;
    output<<"Electricity:"<< electric <<endl;
    output<<"Gas:" << gas<< endl;
    output<<"Telecommunication:" << telecom << endl;
    output<<"Water:" << water;
    return 0;
}

void *customer_threads(void *param){ //creates customer according to the *param, (I've sent each customer's address in the main function)
    customer customers1 = *(customer *) param;
    this_thread::sleep_for(chrono::milliseconds(customers1.sleep));//each customer sleeps according to the sleep time
    int index = customers1.atm_instance;
    int temp = index -1 ;
    atm_array[temp].atm_queue.push(customers1); //I want one customer thread at a time while pushing the customers to the queue array
    pthread_exit(0);    //exits after making its job
}

void *atm_threads(void *param){
    int atm_index = *(int *) param;     // matches the atm_index with the *param, (I've sent each atms index's address in the main function)
    //This sleep function is for protecting the queue accesses between the atm and customer threads
    //In other words, since atm threads may access the queues before the customer pushed the queue,
    //I want block the atm threads from accessing the queue for a while
    this_thread::sleep_for(chrono::milliseconds(max_sleep+2000));
    while(!atm_array[atm_index].atm_queue.empty()){
        customer head_cust = atm_array[atm_index].atm_queue.front();    //the first customer who will pay his bill
        // In the if-else block mentioned below, I calculated the each bill type
        if(!head_cust.billtype.compare("cableTV")){
            pthread_mutex_lock(&cable);
            cableTv += head_cust.amount;
            pthread_mutex_unlock(&cable);
        } else if(!head_cust.billtype.compare("electricity")){
            pthread_mutex_lock(&elec);
            electric += head_cust.amount;
            pthread_mutex_unlock(&elec);
        } else if(!head_cust.billtype.compare("gas")){
            pthread_mutex_lock(&g);
            gas += head_cust.amount;
            pthread_mutex_unlock(&g);
        } else if(!head_cust.billtype.compare("water")){
            pthread_mutex_lock(&wat);
            water += head_cust.amount;
            pthread_mutex_unlock(&wat);
        } else if(!head_cust.billtype.compare("telecommunication")){
            pthread_mutex_lock(&tele);
            telecom += head_cust.amount;
            pthread_mutex_unlock(&tele);
        }
        pthread_mutex_lock(&atm_);  //I want one thread at a time
        output << "Customer" << head_cust.index<<","<<head_cust.amount << "TL," << head_cust.billtype << endl;
        atm_array[atm_index].atm_queue.pop();   //pops the customer from the atm's atm_queue after he pays his bill
        pthread_mutex_unlock(&atm_);
    }
    pthread_exit(0);     //exits after making its job
}
