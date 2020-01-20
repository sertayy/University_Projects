#include <iostream>
#include <sstream>
#include <fstream>
#include <vector>
#include "Graph.h"


using namespace std;

int main(int argc, char* argv[]) {


    if (argc != 3) {
        cout << "Run the code with the following command: ./project1 [input_file] [output_file]" << endl;
        return 1;
    }

    cout << "input file: " << argv[1] << endl;
    cout << "output file: " << argv[2] << endl;

    ifstream infile(argv[1]);

    if (infile.fail()) {
        cerr << "aha hata aldın" << endl;
        exit(1);
    }

    ios_base::sync_with_stdio(false);
    int vertices;
    infile >> vertices;
    Graph mygraph(vertices);



    for (int i=1; i<=vertices; i++) {
        int size;
        infile >> size;
        vector<int> temp;
        for (int j=0; j<size; j++) {
            int key;
            infile >> key;
            temp.push_back(key);
        }
        mygraph.createEdge(temp);
    }


    infile.close();
    mygraph.SCC();
/*
    cout << mygraph.V << endl;
    cout << mygraph.numOfSCC << endl;

*/

    return 0;
}




