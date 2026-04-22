#include <iostream>
#include <unordered_map>
using namespace std;

int main() {
    int n;
    cin >> n;

    unordered_map<int, int> mp1;
    mp1[0] = -1;   

    int sum = 0;
    int maxLength = 0;

    for (int i = 0; i < n; i++) {
        char ch;
        cin >> ch;

        if (ch == 'P' || ch == 'p')
            sum += 1;
        else if (ch == 'A' || ch == 'a')
            sum -= 1;

        if (mp1.find(sum) != mp1.end()) {
            maxLength = max(maxLength, i - mp1[sum]);
        } else {
            mp1[sum] = i;
        }
    }

    cout << maxLength;
    return 0;
}
