#include <iostream>
using namespace std;


int lowerbound(int arr[], int n, int key) {
    int l = 0, r = n-1;
    int lb = -1;

    while(l <= r) {
        int mid = (l + r) / 2;

        if(arr[mid] == key) {
             lb = mid;
            r = mid - 1;   
        }
        else if(arr[mid] < key)
            l= mid + 1;
        else
            r = mid - 1;
    }
    return lb;
}

int upperbound(int arr[], int n, int key) {
    int l = 0, r = n-1;
    int ub = -1;

    while(l <= r) {
        int mid = (l + r) / 2;

        if(arr[mid] == key) {
              ub = mid;
            l = mid + 1;   
        }
        else if(arr[mid] < key)
            l= mid + 1;
        else
            r = mid - 1;
    }
    return ub;
}

int main() {

    int A[5] = {5,4,2,4,1};
    int B[5] = {2,3,4,5,6};

    int count = 0;


    for(int i = 0; i < 5; i++) {

        int key = 7 - A[i];

        int first = lowerbound(B, 5, key);

        if(first != -1) {
            int last = upperbound(B, 5, key);
            count = count+(last - first + 1);
        }
    }

    cout << "Total pairs with sum 7 = " << count;

    return 0;
}
