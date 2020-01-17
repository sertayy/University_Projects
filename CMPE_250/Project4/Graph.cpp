//
// Created by Sertay Akpınar on 13.12.2018.
//

#include "Graph.h"
#include <queue>
#include <iostream>
#include "Path.h"
using namespace std;

Graph::Graph() {

}
void Graph::Simulator(int initX, int initY, int destX, int destY) {

    priority_queue<Path,vector<Path>,compareDistance>* paths = new priority_queue<Path,vector<Path>,compareDistance>();
    Path p1(initX,initY,initX,initY,0);
    paths->push(p1);


    while(!paths->empty()){

        if(paths->top().destX == destX && paths->top().destY == destY){

            cout<<paths->top().distance<<endl;
            return;
        }

        vector<Path> edges;

        if(matrix[paths->top().destX+1][paths->top().destY] != 0 && marked[paths->top().destX+1][paths->top().destY] == false){

            Path newEdge(paths->top().destX, paths->top().destY, paths->top().destX+1, paths->top().destY, max(paths->top().distance,(abs(matrix[paths->top().destX][paths->top().destY] - matrix[paths->top().destX+1][paths->top().destY]))));
            edges.push_back(newEdge);
            //  cout<<max(paths->top().distance,(abs(matrix[paths->top().destX][paths->top().destY] - matrix[paths->top().destX+1][paths->top().destY])))<<endl;

        }
        if(matrix[paths->top().destX-1][paths->top().destY] != 0 && marked[paths->top().destX-1][paths->top().destY] == false){

            Path newEdge(paths->top().destX, paths->top().destY, paths->top().destX-1, paths->top().destY, max(paths->top().distance,(abs(matrix[paths->top().destX][paths->top().destY] - matrix[paths->top().destX-1][paths->top().destY]))));
            edges.push_back(newEdge);
        }
        if(matrix[paths->top().destX][paths->top().destY+1] != 0 && marked[paths->top().destX][paths->top().destY+1] == false){

            Path newEdge(paths->top().destX, paths->top().destY, paths->top().destX, paths->top().destY+1, max(paths->top().distance,(abs(matrix[paths->top().destX][paths->top().destY] - matrix[paths->top().destX][paths->top().destY+1]))));
            edges.push_back(newEdge);
        }
        if(matrix[paths->top().destX][paths->top().destY-1] != 0 && marked[paths->top().destX][paths->top().destY-1] == false){

            Path newEdge(paths->top().destX, paths->top().destY, paths->top().destX, paths->top().destY-1, max(paths->top().distance,(abs(matrix[paths->top().destX][paths->top().destY] - matrix[paths->top().destX][paths->top().destY-1]))));
            edges.push_back(newEdge);
        }
        marked[paths->top().destX][paths->top().destY] = true;
        paths->pop();

        for(int i=0; i < edges.size(); i ++){
            paths->push(edges[i]);
        }

    }
}