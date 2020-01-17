//
// Created by Sertay Akpınar on 12.12.2018.
//

#ifndef PROJECT4_PATH_H
#define PROJECT4_PATH_H


class Path {
public:
    int initX;
    int destX;
    int initY;
    int destY;
    int distance;
    Path(int initX, int destX, int initY, int destY, int distance);

};

struct compareDistance
{
    bool operator()(const Path& p1, const Path& p2)
    {
        return p1.distance > p2.distance;
    }
};

#endif //PROJECT4_PATH_H
