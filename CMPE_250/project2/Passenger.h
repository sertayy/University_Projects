//
// Created by Sertay Akpınar on 9.11.2018.
//

#ifndef SERTAYAKPİNAR2016400075_PASSENGER_H
#define SERTAYAKPİNAR2016400075_PASSENGER_H
#include <iostream>
using namespace std;

class Passenger{
public:


    char Luggage;
    char VIP;
    int arrival;
    int boarding;
    int LuggageTime;
    int SecurityTime;

    Passenger(int arrival, int boarding, int LuggageTime, int SecurityTime, char Luggage, char VIP);
    Passenger();
    ~Passenger();
    bool hasLuggage();
    bool isVIP();

};
struct CompareArrivalTime
{
    bool operator()(Passenger p1, Passenger p2)
    {
        return p1.arrival > p2.arrival;
    }
};


#endif //SERTAYAKPİNAR2016400075_PASSENGER_H
