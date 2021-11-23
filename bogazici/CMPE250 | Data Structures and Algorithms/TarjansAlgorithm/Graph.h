//
// Created by Sertay Akpınar on 23.11.2018.
//

#include<iostream>
#include <list>
#include <stack>
#include <vector>

using namespace std;

// A class that represents an directed graph
class Graph
{

public:
    int V;    // No. of vertices
    int numOfSCC;
    stack<int> Stack;
    vector<vector<int>> adj;    // A dynamic array of adjacency lists
    int* SCCs;
    vector<int> members ;
    vector<int> breakThese;

    list<int> scc;
    // A Recursive DFS based function used by SCC()
    void SCCRecursive(int u, int *index, int *low, bool *inStack);

    Graph(int V);   // Constructor
    void createEdge(vector<int> keys);   // function to add an edge to graph
    void SCC();    // prints strongly connected components
};

