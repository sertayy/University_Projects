#include <iostream>
#include "fstream"
using namespace std;

int main() {

    //give the desired dataset's path to gain the result of the desired dataset
    ifstream infile("/Users/apple/CLionProjects/IE310/IE310Assignment1/Assignment1_Spring20_Data1.txt");
    int numofobj, maxvolume;
    int totalprofit = 0;
    int totalvolume = 0;
    double rilist[numofobj];
    int w = 0;
    double profit, cost, ri, temp;
    infile >> numofobj;
    infile >> maxvolume;
    int volumelist[numofobj], profitlist[numofobj], indexlist[numofobj];

    for(int i=0; i < numofobj; i++){
        infile >> profit;
        infile >> cost;
        ri = profit/cost;
        rilist[i] = ri;
        volumelist[i] = cost;
        profitlist[i] = profit;
        indexlist[i] = i+1;
    }

    for(int i=0; i < numofobj; i++){

        for(int j=i+1; j < numofobj; j++){

            if(rilist[i]<rilist[j]){
                temp  = rilist[i];
                rilist[i] = rilist[j];
                rilist[j] = temp;

                temp = volumelist[i];
                volumelist[i] = volumelist[j];
                volumelist[j] = temp;

                temp = profitlist[i];
                profitlist[i] = profitlist[j];
                profitlist[j] = temp;

                temp = indexlist[i];
                indexlist[i] = indexlist[j];
                indexlist[j] = temp;
            }
        }
    }

    cout<<"Knapsack contains: " <<endl;
    for(int i=0; i < numofobj; i++){
        if((w + volumelist[i]) <= maxvolume){

            w+=volumelist[i];
            totalprofit += profitlist[i];
            totalvolume += volumelist[i];
            cout<<indexlist[i] <<". object, " << "ri value: " << rilist[i] << ", volume: " << volumelist[i] << ", profit: " << profitlist[i] << endl;

        }
    }
    cout << "Total profit is " << totalprofit << "." << endl;
    cout << "Total value consumed is " << totalvolume << "." << endl;
    cout << "Best found object is " <<indexlist[0] <<". object with ri value of " << rilist[0] << ".";
    return 0;
}