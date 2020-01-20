#include <iostream>
#include <fstream>
#include <vector>
#include <queue>
#include "Path.h"
#include "Graph.h"

using namespace std;

int main(int argc, char* argv[]) {
/*
    if (argc != 3) {
        cout << "Run the code with the following command: ./project3 [input_file] [output_file]" << endl;
        return 1;
    }
*/
    ifstream infile("/Users/sertayakpinar/CLionProjects/Project4/small.txt");

    ios_base::sync_with_stdio(false);
    Graph mygraph;
    int rows;
    int columns;
    infile >> rows;
    infile >> columns;

    for (int i=1; i<=rows; i++) {
        for (int j=1; j<=columns; j++) {

            int height;
            infile >> height;
            mygraph.matrix[i][j] = height;
        }
    }

    int x;

    int initX;
    int initY;
    int destX;
    int destY;

    infile >> x;

    infile >> initX;
    infile >> initY;
    infile >> destX;
    infile >> destY;

    mygraph.Simulator(initX,initY,destX,destY);

    return 0;
}