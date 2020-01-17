//
// Created by Sertay Akpınar on 13.12.2018.
//

#ifndef PROJECT4_GRAPH_H
#define PROJECT4_GRAPH_H


class Graph {
public:

    int matrix[1002][1002] = {0};
    bool marked[1002][1002] = {false};
    Graph();
    void Simulator(int initX, int initY, int destX, int destY);
};


#endif //PROJECT4_GRAPH_H
