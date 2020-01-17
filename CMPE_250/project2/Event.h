//
// Created by Sertay Akpınar on 11.11.2018.
//

#define SERTAYAKPİNAR2016400075_EVENTS_H
#include "Passenger.h"

class Event {
public:

    int time;
    Passenger passenger;
    int event_type;

    Event(int time, Passenger passenger, int event_type);
    Event();
    ~Event();

};

struct compareEvents
{
    bool operator()(Event e1, Event e2)
    {

        if(e1.time == e2.time){
            return e1.event_type > e2.event_type;
        } else if(e1.time == e2.time && e1.event_type == e2.event_type) {
            return e1.passenger.arrival > e2.passenger.arrival;
        }
        return e1.time > e2.time;
    }
};


