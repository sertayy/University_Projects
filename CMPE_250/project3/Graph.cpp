#include "Graph.h"

Graph::Graph(int V)
{
    this->V = V;
    adj.push_back(vector<int>(1));
    numOfSCC=0;
    SCCs = new int[V+1];
    members.push_back(1);
}

void Graph::createEdge(vector<int> keys)
{
    adj.push_back(keys);
}

void Graph::SCCRecursive(int u, int *index, int *low, bool *inStack)
{
    // A static variable is used for simplicity, we can avoid use
    // of static variable by passing a pointer.
    static int time = 0;

    // Initialize discovery time and low value
    index[u] = low[u] = ++time;
    Stack.push(u);
    inStack[u] = true;

    // Go through all vertices adjacent to this
    vector<int>::iterator i;
    for (i = adj[u].begin(); i != adj[u].end(); ++i)
    {
        int v = *i;  // v is current adjacent of 'u'

        // If v is not visited yet, then recur for it
        if (index[v] == -1)
        {
            SCCRecursive(v, index, low, inStack);

            // Check if the subtree rooted with 'v' has a
            // connection to one of the ancestors of 'u'
            // Case 1 (per above discussion on Disc and Low value)
            low[u]  = min(low[u], low[v]);
        }

            // Update low value of 'u' only of 'v' is still in stack
            // (i.e. it's a back edge, not cross edge).
            // Case 2 (per above discussion on Disc and Low value)
        else if (inStack[v] == true)
            low[u]  = min(low[u], index[v]);
    }

    if (low[u] == index[u])
    {
        numOfSCC++;
        while (true)
        {
            int curr = (int) Stack.top();
            Stack.pop();
            inStack[curr] = false;
            SCCs[curr]=numOfSCC;
            if (u==curr) {
                members.push_back(u);
                break;
            }
        }
    }

/*    bool isChild[numOfSCC];
    for(int i =0; i<SCCs.size(); i++){
      isChild[i] = false;
    }

    for(int i = 0; i < V; i++){
        for(int j=0; j < adj[i].size(); j++){

            if(SCCs[j]!= SCCs[i]){
                isChild[SCCs[j]] = true;
            }
        }
    }
    */
}


// The function to do DFS traversal. It uses SCCRecursive()
void Graph::SCC()
{

    int *index = new int[V+1];
    int *low = new int[V+1];
    bool *inStack = new bool[V+1];

    // Initialize disc and low, and stackMember arrays
    for (int i = 1; i <= V; i++)
    {
        index[i] = -1;
        low[i] = -1;
        inStack[i] = false;
    }

    // Call the recursive helper function to find strongly
    // connected components in DFS tree with vertex 'i'
    for (int i = 1; i <= V; i++)
        if (index[i] == -1) {
            SCCRecursive(i, index, low, inStack);
        }


    bool hasAparent[numOfSCC +1];

    for(int i=0; i<=numOfSCC; i++){

        hasAparent[i] = false;

    }

    for(int u=1; u<=V; u++){

        vector<int>::iterator v;
        for(v = adj[u].begin(); v != adj[u].end() ; ++v) {
            if (SCCs[u] != SCCs[*v]) {
                hasAparent[SCCs[*v]]=true;
            }
        }

    }


    for(int i = 1 ; i<=numOfSCC; i++){

        if(hasAparent[i] == false){
           breakThese.push_back(members[i]);

        }

    }

    cout<< breakThese.size()<< " ";
    vector<int>::iterator i;
    for(i = breakThese.begin(); i!= breakThese.end(); ++i ){

        cout << *i <<  " ";

    }



}
