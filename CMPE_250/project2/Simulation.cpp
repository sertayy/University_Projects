//
// Created by Sertay Akpınar on 9.11.2018.
//
#include "Simulation.h"
#include <iostream>
#include <vector>
#include <queue>

using namespace std;

Simulation::Simulation(int P, int L, int S, bool Luggage, bool VIP, bool FirstToFly, priority_queue<Event, vector<Event>, compareEvents> event_queue) {

    this->P = P;
    this->L = L;
    this->S = S;
    this->Luggage = Luggage;
    this->VIP = VIP;
    this->FirstToFly = FirstToFly;
    this->event_queue = event_queue;
}

Simulation::Simulation() {


}

Simulation::~Simulation() {


}

void Simulation::Simulate() {
    priority_queue<Event, vector<Event>, compareEvents> luggageCounter;
    priority_queue<Event, vector<Event>, compareEvents>  securityCounter;
    priority_queue<Event, vector<Event>, compareEvents> luggageOrder;
    priority_queue<Event, vector<Event>, compareEvents>  securityOrder;


    int currentTime = 0;
    int passengers = 0;
    int totalTime = 0;

    while(!event_queue.empty()){

        Event e1 = event_queue.top();
        event_queue.pop();

        if(event_queue.top().event_type == 2){

            if (luggageCounter.size() >= L) {

                luggageOrder.push(e1);

            } else{

                if(!luggageOrder.empty()){
                    e1 = luggageOrder.top();
                    luggageOrder.pop();
                }

                e1.time += e1.passenger.LuggageTime;
                // e1.time = currentTime ;
                e1.event_type = 1;
                luggageCounter.push(e1);
                //Event newEvent = luggageCounter.top();
                event_queue.push(e1);

            }
        }else if(event_queue.top().event_type == 1){



            if(securityCounter.size() >= S){

                securityOrder.push(e1);

            }else{

                if(!securityOrder.empty()) {
                    e1 = securityOrder.top();
                    securityOrder.pop();

                }
                e1.time += e1.passenger.SecurityTime;
                //  currentTime = e1.time;
                e1.event_type = 0;
                securityCounter.push(e1);
                //  Event newEvent = securityCounter.top();
                event_queue.push(e1);


            }

        }else{

            if(currentTime > e1.passenger.boarding){
                cout<<1<<endl;
                passengers++;

            }
            totalTime += currentTime - e1.passenger.arrival;

        }
    }

    float averageT = ((float)totalTime/P)*100;
    int averageTime = averageT;
    averageT = averageTime/100;
    cout<< averageT <<" "<<passengers<<endl;

};
/*
    int securityCounter;
    int luggageCounter;
    queue<Passenger> securityOrder;
    queue<Passenger> luggageOrder;
    */
/*
    while (!event_queue.empty()) {

        Event e1 = event_queue.top();
        event_queue.pop();

        if (e1.event_type == 2 && luggageOrder.empty()) {

            if (luggageCounter < L) {
                e1.event_type = 1;
                e1.time += e1.passenger.LuggageTime;
                event_queue.push(e1);
                luggageCounter++;
            } else {

                luggageOrder.push(e1.passenger);

            }
        }else if(e1.event_type == 2 && !luggageOrder.empty()){


            e1.passenger = luggageOrder.front();
            e1.time += e1.passenger.LuggageTime;
            e1.event_type=1;
            event_queue.push(e1);
            luggageCounter++;
            luggageOrder.pop();
        }
        if(e1.event_type == 1 && securityOrder.empty()){

            if(securityCounter < S){

                e1.event_type = 0;
                e1.time += e1.passenger.SecurityTime;
                event_queue.push(e1);
                securityCounter++;
                luggageCounter--;
            }else{
                securityOrder.push(e1.passenger);
            }
        }else if(e1.event_type == 1 && !securityOrder.empty()){

            e1.passenger = securityOrder.front();
            e1.time += e1.passenger.SecurityTime;
            event_queue.push(e1);
            securityCounter++;
            securityOrder.pop();
            luggageCounter--;

        }


        else if(e1.event_type == 1){

            if(securityCounter < S){
                e1.event_type = 0;
                e1.time += e1.passenger.SecurityTime;
                event_queue.push(e1);
                securityCounter++;
                luggageCounter--;
            }else{
                securityOrder.push(e1.passenger);

            }
        }

    }


}
*/



/*
Event* e=http://event.top ();
event.pop();

if(e->eventType==2){  ///luggage counterlara giriş

if(nuLugCount <= lugQ.size()){      ///luggage counterda yer yokken

lugWait.push(e);      ///bekleme sırasına geçti
currentTime=e->beginTime;

} else {
if (i < nuLugCount) { ///luggagecounterlar boşken

currentTime = e->beginTime;
Event *e1 = new Event(e->pass, e->pass->luggageWait + e->pass->arrivalTime, 1);
event.push(e1);
lugQ.push(e1);
} else {

Event *e1 = new Event(e->pass, e->pass->luggageWait + e->pass->arrivalTime, 1);
event.push(e1);
lugQ.push(http://lugWait.top ()); ///bekleyenlerin en öndekini aldı
currentTime=http://lugWait.top ()->beginTime;
lugWait.pop();
lugQ.pop();
}
}
i++;

}
else if(e->eventType==1) {

if(nuSecCount <= secQ.size()){

secWait.push(e);
currentTime=e->beginTime;

} else {
if(j < nuSecCount) {

currentTime = e->beginTime;
Event *e1 = new Event(e->pass, e->pass->luggageWait + e->pass->arrivalTime+e->pass->securityWait, 0);
event.push(e1);
secQ.push(e1);
} else {

Event *e1 = new Event(e->pass, e->pass->luggageWait + e->pass->arrivalTime+e->pass->securityWait, 0);
event.push(e1);
secQ.push(http://secWait.top ()); ///bekleyenlerin en öndekini aldı
currentTime=http://secWait.top ()->beginTime;
secWait.pop();
}

}
j++;
} else {

currentTime=e->beginTime;

}
*/





