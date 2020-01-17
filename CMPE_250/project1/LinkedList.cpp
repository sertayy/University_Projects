#include "LinkedList.h"

LinkedList::LinkedList() {

    this->length=0;
    this->head=NULL;
    this->tail=NULL;
}
LinkedList::LinkedList(const LinkedList &list) {

    if(list.head!=NULL) {
        this->length = list.length;
        this->head = new Node(*list.head);
        Node* temp = head;

        while (temp->next != NULL) {
            temp = temp->next;
        }

        tail = temp;
    }
}

LinkedList& LinkedList::operator=(const LinkedList &list) {

    this->length = list.length;
    delete this->head;
    this->head = new Node(*list.head);

    Node *temp;
    temp = head;

    while (temp->next != nullptr) {
        temp = temp->next;
    }

    tail = temp;
    return *this;
}

LinkedList::LinkedList(LinkedList &&list) {

   this->length = move(list.length);
   this->head = move(list.head);
   Node* temp;
   temp = head;

   while(temp->next != nullptr){
       temp = temp->next;
   }

   tail = temp;
   this->tail = move(list.tail);

   list.length=0;
   list.head=NULL;
   list.tail=NULL;
}

LinkedList& LinkedList::operator=(LinkedList &&list) {

    this->length = move(list.length);
    delete this->head;// bak
    this->head = move(list.head);
    Node* temp = head;

    while(temp->next != nullptr){
        temp = temp->next;
    }
    tail = temp;
    this->tail = move(list.tail);

    list.length=0;
    list.head=NULL;
    list.tail=NULL;

    return *this;
}
// add a new element to the back of LinkedList
void LinkedList::pushTail(string _name, float _amount) {

    Node* temp= new Node(_name, _amount);

    if(this->head == NULL){
        head = temp;
        // tail = head;
    }else {
        Node *temp_2 = head;

        while (temp_2->next != NULL) {

            temp_2 = temp_2->next;
        }
    temp_2->next = temp;
    tail = temp;
    }

    this->length++;
}


void LinkedList::updateNode(string _name, float _amount) {

    Node* temp = head;
    while(temp->next!= NULL){

        if(temp->name == _name){
            temp->amount=_amount;
        }
        temp = temp->next;
    }
}

LinkedList::~LinkedList() {

    if(this->head){
        delete this->head;
    }
}