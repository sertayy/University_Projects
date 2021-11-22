//
// Created by Sertay Akpınar on 9.11.2018.
//
#include "Passenger.h"
#include <iostream>
#include <queue>
#include <vector>
#include <functional>
#include <list>

using namespace std;

Passenger::Passenger(int arrival, int boarding, int LuggageTime, int SecurityTime, char Luggage, char VIP) {

    this->arrival = arrival;
    this->boarding = boarding;
    this->LuggageTime = LuggageTime;
    this->SecurityTime = SecurityTime;
    this->VIP = VIP;
    this->Luggage = Luggage;
  //  bool hasLuggage;
  //  bool hasVIP;
/*
    if(Luggage == 'L'){
        hasLuggage = true;
    } else {
        hasLuggage = false;
    }

    if(VIP == 'V'){
        hasVIP = true;
    } else {
        hasVIP = false;
    }
    */
}

Passenger::Passenger() {


}
Passenger::~Passenger() {

}

bool Passenger::hasLuggage() {
    if(Luggage == 'L'){
        return true;
    }
    return false;
}

bool Passenger::isVIP() {
    if(VIP == 'V'){
        return true;
    }
    return false;

}











