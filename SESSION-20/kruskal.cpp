#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;

struct Edge
{
    int u, v, weight;
};

vector<int> parent, sizeArr;


int findParent(int node)
{
    if (parent[node] == node)
        return node;

    return parent[node] = findParent(parent[node]);
}


void unionSet(int u, int v)
{
    int pu = findParent(u);
    int pv = findParent(v);

    if (pu == pv)
        return;

   
    if (sizeArr[pu] < sizeArr[pv])
    {
        parent[pu] = pv;
        sizeArr[pv] += sizeArr[pu];
    }
    else
    {
        parent[pv] = pu;
        sizeArr[pu] += sizeArr[pv];
    }
}

bool cmp(Edge a, Edge b)
{
    return a.weight < b.weight;
}

void kruskal(int V, vector<Edge> &edges)
{
    sort(edges.begin(), edges.end(), cmp);

    parent.resize(V);
    sizeArr.resize(V);

    for (int i = 0; i < V; i++)
    {
        parent[i] = i;
        sizeArr[i] = 1;   
    }

    int totalCost = 0;

    for (auto e : edges)
    {
        if (findParent(e.u) != findParent(e.v))
        {
            unionSet(e.u, e.v);
            totalCost += e.weight;
        }
    }

    cout << "Total cost of MST: " << totalCost << endl;
}

int main()
{
    int V = 5;

    vector<Edge> edges = {
        {0,1,2},
        {0,3,6},
        {1,2,3},
        {1,3,8},
        {1,4,5},
        {2,4,7},
        {3,4,9}
    };

    kruskal(V, edges);

    return 0;
}
