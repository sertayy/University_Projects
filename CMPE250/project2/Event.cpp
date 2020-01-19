//
// Created by Sertay Akpınar on 11.11.2018.
//

#include "Event.h"
#include <iostream>
#include <vector>
#include <queue>

using namespace std;

Event::Event(int time, Passenger passenger, int event_type) {
    this->time = time;
    this->passenger = passenger;
    this->event_type = event_type;
}
Event::Event() {

}

Event::~Event() {

}


