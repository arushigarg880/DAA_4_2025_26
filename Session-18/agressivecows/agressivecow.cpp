class Solution {
public:

   
    bool canPlace(vector<int> &stalls, int k, int minallowed)
    {
        int cow = 1; 
        int lastposition = stalls[0];

        for(int i = 1; i < stalls.size(); i++)
        {
            if(stalls[i] - lastposition >= minallowed)
            {
                cow++;
                lastposition = stalls[i];
            }

            if(cow == k)
                return true;
        }

        return false;
    }

    int aggressiveCows(vector<int> &stalls, int k)
    {
        sort(stalls.begin(), stalls.end());

        int n = stalls.size();
        int l = 1;
        int r = stalls[n-1] - stalls[0];
        int ans = 0;

        while(l <= r)
        {
            int mid = (l + r)/2;

            if(canPlace(stalls,k,mid))
            {
                ans=mid;
                l=mid+1;
            }
            else
            {
                 r=mid-1;
            }
        }

        return ans;
    }
};
