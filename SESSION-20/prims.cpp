#include <iostream>
#include <vector>
#include <queue>
using namespace std;

typedef pair<int, int> pii;   

void prims(int V, vector<vector<pii>> &adj)
{
    priority_queue<pii, vector<pii>, greater<pii>> pq;
    vector<bool> visited(V, false);

    pq.push({0, 0});   
    int totalCost = 0;

    while (!pq.empty())
    {
        int weight = pq.top().first;
        int node = pq.top().second;
        pq.pop();

        if (visited[node])
            continue;

        visited[node] = true;
        totalCost += weight;

        for (auto it : adj[node])
        {
            int nextNode = it.second;
            int edgeWeight = it.first;

            if (!visited[nextNode])
            {
                pq.push({edgeWeight, nextNode});
            }
        }
    }

    cout << "Total cost of MST: " << totalCost << endl;
}

int main()
{
    int V = 5;
    vector<vector<pii>> adj(V);

   
    adj[0].push_back({2,1});
    adj[1].push_back({2,0});

    adj[0].push_back({6,3});
    adj[3].push_back({6,0});

    adj[1].push_back({3,2});
    adj[2].push_back({3,1});

    adj[1].push_back({8,3});
    adj[3].push_back({8,1});

    adj[1].push_back({5,4});
    adj[4].push_back({5,1});

    adj[2].push_back({7,4});
    adj[4].push_back({7,2});

    adj[3].push_back({9,4});
    adj[4].push_back({9,3});

    prims(V, adj);

    return 0;
}
