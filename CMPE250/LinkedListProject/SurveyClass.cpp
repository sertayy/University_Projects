#include "SurveyClass.h"

SurveyClass::SurveyClass() {

    this->members=new LinkedList();

}

SurveyClass::SurveyClass(const SurveyClass &other) {

    if(other.members != NULL){
    this->members = new LinkedList(*(other.members));

    }
}

SurveyClass& SurveyClass::operator=(const SurveyClass &list) {

    delete this->members;
    this->members = new LinkedList(*(list.members));
    return *this;

}


SurveyClass::SurveyClass(SurveyClass &&other) {

    this->members = move(other.members);
    other.members = NULL;

}

SurveyClass& SurveyClass::operator=(SurveyClass &&list) {
    delete this->members;

    this->members = move(list.members);
    list.members = NULL;
    return *this;
}

void SurveyClass::handleNewRecord(string _name, float _amount) {

    Node* temp = new Node(_name, _amount);
    while(temp->next!= NULL){

        if(temp->name == _name){
        this->members->updateNode(_name, _amount);
        return;
        }
        temp = temp->next;

    }
  //  if(temp==members->tail){

        this->members->pushTail(_name, _amount);

    //}
}

SurveyClass::~SurveyClass() {

    if(this->members){
        delete this->members;
    }
}

float SurveyClass::calculateMinimumExpense() {

float min = members->head->amount;
Node* temp = members->head;

while(temp->next != NULL){

    if(temp->amount < min){
        min = temp->amount;
    }
    temp = temp->next;
}
return min;

}


float SurveyClass::calculateMaximumExpense() {

float max = members->head->amount;
Node* temp = members->head;

while(temp->next != NULL){

    if(temp->amount > max ){
        max = temp->amount;
    }
    temp = temp->next;
}
return max;

}

float SurveyClass::calculateAverageExpense() {

float total;
Node* temp = members->head;

    while(temp->next != NULL){

        total += temp->amount;
        temp = temp->next;
    }

    return total/members->length;
}





