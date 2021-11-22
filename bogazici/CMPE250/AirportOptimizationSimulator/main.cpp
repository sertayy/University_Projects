/*
 NOT COMPLETED
 */
#include <iostream>
#include <sstream>
#include <fstream>
#include <vector>
#include <iterator>
#include "Simulation.h"
#include <list>


using namespace std;

template <class Container>
void split1(const string& str, Container& cont)
{
    istringstream iss(str);
    copy(istream_iterator<string>(iss),
         istream_iterator<string>(),
         back_inserter(cont));
}


int main(int argc, char* argv[]) {



     // read the file named <argv[1]>
        ifstream infile("/Users/sertayakpinar/CLionProjects/cmpe250-project2-sertayakpinar2016400075/inputSmallEarly.txt");

        string line;
        vector<string> input;
        // process first line
        getline(infile, line);


        vector<string> words;
        split1(line,words);

        Simulation MySimulation;

        MySimulation.P = stoi(words[0]);
        MySimulation.L = stoi(words[1]);
        MySimulation.S = stoi(words[2]);

        priority_queue<Passenger, vector<Passenger>, CompareArrivalTime> passenger_queue;
        vector<Passenger> list;
        priority_queue<Event, vector<Event>, compareEvents> arrival_queue;


        /*
        Passenger pass1 = new Passenger(1,10,6,3,'N','N');
        Passenger pass2 = new Passenger(3,16,3,6,'N','N');
        Passenger pass3 = new Passenger(4,11,2,3,'N','N');

        Event enterluggage = new Event(1,pass1,2);
        Event entersecurity = new Event(2,pass2,1);
     // Event enterflight = new Event(2,pass3,0);
        Event entersecurity2 = new Event(2,pass3,1);
      */

        for (int i=0; i<MySimulation.P ; i++) {

            getline(infile, line);
            vector<string> words;
            split1(line,words);

            int arrival = stoi(words[0]);
            int boarding =  stoi(words[1]);
            int LuggageTime = stoi(words[2]);
            int SecurityTime = stoi(words[3]);
            char Luggage = (words[4])[0];
            char VIP = (words[5])[0];

            Passenger MyPassenger = Passenger(arrival, boarding, LuggageTime, SecurityTime, Luggage, VIP);

            passenger_queue.push(MyPassenger);
            list.push_back(MyPassenger);

            Event arrival_Event(MyPassenger.arrival,MyPassenger,2);

            /*
            arrival_Event.passenger = MyPassenger;
            arrival_Event.time = MyPassenger.arrival;
            arrival_Event.event_type = 2;
            */

            arrival_queue.push(arrival_Event);
            cout << "line: " << line << endl;

        }

       Simulation(MySimulation.P, MySimulation.L, MySimulation.S, false, false, false, arrival_queue).Simulate();



    /*while(!queue1.empty()){

            event_queue.push();
            queue1.pop();
        }
*/






  /*
    event_queue.push(enterluggage);
   // event_queue.push(enterflight);
    event_queue.push(entersecurity);
    event_queue.push(entersecurity2);
  */


    /*while(!event_queue.empty()) {
        cout << event_queue.top()->passenger->arrival << endl;
        event_queue.pop();
    }

    */

    cout << "input file has been read" << endl;





        // here, perform the output operation. in other words,
        // print your results into the file named <argv[2]>

        ofstream myfile;
        myfile.open (argv[2]);

        // myfile << minExp << " " << maxExp << " " << avgExp << endl;
        //myfile << queue1() <<endl;
        myfile.close();

        return 0;

}
