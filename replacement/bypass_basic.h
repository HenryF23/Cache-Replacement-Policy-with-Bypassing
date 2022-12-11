#include "../inc/cache.h"
#include <random>
#include <vector>

// Each set will have a BYPASS_INFO
struct BYPASS_INFO
{   // Index of prob_table, initial prob = 1/64
    int prob = 6;
    // competitor_tag store the tag of bypassed line
    std::vector<uint64_t> competitor_tag;
    // competitor_way store the tag of victim (been replaced) line
    std::vector<uint64_t> competitor_way;
};

// Probability of bypassing: 1/prob
int prob_table[14] = {1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096, 0};
// Random number generator
std::random_device dev;
std::mt19937 rng(dev());
// Define the number of ways we considerd as recently inserted
#define LRI_THRESHOLD 4

BYPASS_INFO bypass_control[LLC_SET];

void bypass_report()
{
    for(int i = 0; i < LLC_SET; ++i){
        printf("[set, prob, size of tag, size of way]: [%d, %d, %ld, %ld]\n", i, bypass_control[i].prob, bypass_control[i].competitor_tag.size(), bypass_control[i].competitor_way.size());
    }
}

#ifdef VIRTUAL_BY
void CACHE::virtual_bp_report()
{
    for(int set = 0; set < 2048; ++set){
        printf("In set %d:\n", set);
        for(int way = 0; way < (int)LLC_WAY; ++way){
            printf("Way %d's lri is %d\n", way, block[set][way].lri);
        }
    }
}

void virtual_bp_update(uint32_t set, uint32_t way, BLOCK* current_set){
    current_set[way].lri = 0;
    for(int i = 0; i < (int)LLC_WAY; ++i) {
        if(i != (int)way && current_set[i].valid && current_set[i].lri < LRI_THRESHOLD){
            // printf("At set %d, at way %d\n", set, i);
            current_set[i].lri++;
        }
    }
}

uint64_t CACHE::virtual_bypass_helper(uint32_t curr_set){
    std::vector<int> candidate_index;
    for(int i = 0; i < (int)LLC_WAY; ++i){
        if(block[curr_set][i].lri < LRI_THRESHOLD){
            candidate_index.push_back(i);
        }
    }

    std::uniform_int_distribution<std::mt19937::result_type> dist(0, LRI_THRESHOLD - 1);
    uint64_t luckboy_tag = block[curr_set][candidate_index[(int)dist(rng)]].address; 

    // printf("Virtual_tag: %ld\n", luckboy_tag);

    return luckboy_tag;
}
#endif

// If n is 0, will return false
bool prob_of_n_choose_1(int n)
{
    if(n <= 0){
        return false;
    }
    std::uniform_int_distribution<std::mt19937::result_type> dist(1, n);

    if(dist(rng) == 1){
        return true;
    }

    return false;
}

// This function will return a bool to indicate bypass decision
// It should be called after found the victim way
bool CACHE::bypass_decider(uint32_t curr_set, uint64_t newline_tag, uint64_t victim_tag, uint64_t virtual_tag)
{
    // If the victim address is 0 (this set still has empty/unused space), don't consider bypass at all!
    if(victim_tag == 0){
        return false;
    }

    bool result = prob_of_n_choose_1(prob_table[bypass_control[curr_set].prob]);
    // printf("Bypass decision: %d, curr_set: %d, newline_tag: %ld, victim_tag: %ld, virtual_tag: %ld\n", result, curr_set, newline_tag, victim_tag, virtual_tag);
    // Decide to bypass
    if (result){
        // Store the tag to evaluate the effect of bypassing
        bypass_control[curr_set].competitor_tag.push_back(newline_tag);
        bypass_control[curr_set].competitor_way.push_back(victim_tag);
        // printf("Bypass, tag push %ld and way push %ld\n", newline_tag, victim_tag);
    }
    // Decide not to bypass
    else{
        // Virtual bypassing evaluate
        #ifdef VIRTUAL_BY
            if(virtual_tag == 0){
                return false;
            }
            bypass_control[curr_set].competitor_tag.push_back(newline_tag);
            bypass_control[curr_set].competitor_way.push_back(virtual_tag);
            // printf("Not bypass, tag push %ld and way(virtual) push %ld\n", newline_tag, virtual_tag);
        #else
            bypass_control[curr_set].competitor_tag.push_back(newline_tag);
            bypass_control[curr_set].competitor_way.push_back(victim_tag);
            // printf("Not bypass, tag push %ld and way push %ld\n", newline_tag, victim_tag);
        #endif
    }

    return result;
}

template <typename F>
int vector_find(std::vector<F>& vec, F tar)
{
    int index = 0;
    for(auto& i : vec){
        if (i == tar){
            return index;
        }
        index++;
    }
    return -1;
}

void decr_prob(int& prob)
{
    int prob_size = sizeof(prob_table) / sizeof(prob_table[0]);
    if(prob < prob_size - 1){
        prob++;
    }
}

void incre_prob(int& prob)
{
    if(prob > 0){
        prob--;
    }
}

// This function must be called for each cache replacement!! (can before found the victim line)
// It updates the bypass probability for set (if there exist competition)
void CACHE::bypass_evaluator(uint32_t curr_set, uint64_t newline_tag)
{
    int index = vector_find(bypass_control[curr_set].competitor_tag, newline_tag);
    // Bypassed line win, ineffective bypass
    if (index != -1)
    {
        // printf("Decreased!\n");
        // printf("Set: %d, Prob value: %d\n", curr_set, bypass_control[curr_set].prob);
        decr_prob(bypass_control[curr_set].prob);
        // printf("Set: %d, Prob value: %d\n", curr_set, bypass_control[curr_set].prob);
        // Competition done, remove them from the list
        bypass_control[curr_set].competitor_tag.erase(bypass_control[curr_set].competitor_tag.begin() + index);
        bypass_control[curr_set].competitor_way.erase(bypass_control[curr_set].competitor_way.begin() + index);
    }

    index = vector_find(bypass_control[curr_set].competitor_way, newline_tag);
    // Victim line win, effective bypass
    if (index != -1)
    {
        // printf("Increased!\n");
        // printf("Set: %d, Prob value: %d\n", curr_set, bypass_control[curr_set].prob);
        incre_prob(bypass_control[curr_set].prob);
        // printf("Set: %d, Prob value: %d\n", curr_set, bypass_control[curr_set].prob);
        bypass_control[curr_set].competitor_tag.erase(bypass_control[curr_set].competitor_tag.begin() + index);
        bypass_control[curr_set].competitor_way.erase(bypass_control[curr_set].competitor_way.begin() + index);
    }
}