//
// Created by Sertay Akpınar on 9.11.2018.
//

#define SERTAYAKPİNAR2016400075_SİMULATİON_H
#include "Passenger.h"
#include <vector>
#include <queue>
#include "Event.h"

using namespace std;

class Simulation{
public:

    bool Luggage;
    bool VIP;
    int P;
    int L;
    int S;
    bool FirstToFly;

    priority_queue<Event, vector<Event>, compareEvents> event_queue;
    Simulation();
    void Simulate();
    Simulation(int P, int L, int S, bool Luggage, bool VIP, bool FirstFoFly, priority_queue<Event, vector<Event>, compareEvents> event_queue);
    ~Simulation();

};
