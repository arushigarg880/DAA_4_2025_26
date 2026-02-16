class Solution {
public:

    bool possible(vector<int>& piles, int mid, int h){
        long long c = 0;
        for(int x : piles){
            c += (x + mid - 1) / mid;
        }
        return c <= h;
    }

    int binary1(int left, int right, int h, vector<int>& piles){
        while(left <= right){
            int middle = left + (right - left) / 2;

            if(possible(piles, middle, h)){
                right = middle - 1;
            }
            else{
                left = middle + 1;
            }
        }
        return left;
    }

    int minEatingSpeed(vector<int>& piles, int h) {
        int maxx = *max_element(piles.begin(), piles.end());
        

        int result = binary1(1, maxx, h, piles);
        return result;
    }
};
