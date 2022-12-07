#include "cache.h"
#include <vector>
#include <algorithm>

uint32_t CACHE::find_victim(uint32_t cpu, uint64_t instr_id, uint32_t set, const BLOCK *current_set, uint64_t ip, uint64_t full_addr, uint32_t type)
{
    // baseline LRU replacement policy for other caches 
    return lru_victim(cpu, instr_id, set, current_set, ip, full_addr, type); 
}

void CACHE::update_replacement_state(uint32_t cpu, uint32_t set, uint32_t way, uint64_t full_addr, uint64_t ip, uint64_t victim_addr, uint32_t type, uint8_t hit)
{
    if (type == WRITEBACK) {
        if (hit) // wrietback hit does not update LRU state
            return;
    }

    return lru_update(set, way);
}

uint32_t CACHE::lru_victim(uint32_t cpu, uint64_t instr_id, uint32_t set, const BLOCK *current_set, uint64_t ip, uint64_t full_addr, uint32_t type)
{
    uint32_t way = 0;

    // fill invalid line first
    for (way=0; way<NUM_WAY; way++) {
        if (block[set][way].valid == false) {

            DP ( if (warmup_complete[cpu]) {
            cout << "[" << NAME << "] " << __func__ << " instr_id: " << instr_id << " invalid set: " << set << " way: " << way;
            cout << hex << " address: " << (full_addr>>LOG2_BLOCK_SIZE) << " victim address: " << block[set][way].address << " data: " << block[set][way].data;
            cout << dec << " lru: " << block[set][way].lru << endl; });

            break;
        }
    }

    // LRU victim
    if (way == NUM_WAY) {
        for (way=0; way<NUM_WAY; way++) {
            if (block[set][way].lru == NUM_WAY-1) {

                DP ( if (warmup_complete[cpu]) {
                cout << "[" << NAME << "] " << __func__ << " instr_id: " << instr_id << " replace set: " << set << " way: " << way;
                cout << hex << " address: " << (full_addr>>LOG2_BLOCK_SIZE) << " victim address: " << block[set][way].address << " data: " << block[set][way].data;
                cout << dec << " lru: " << block[set][way].lru << endl; });

                break;
            }
        }
    }

    if (way == NUM_WAY) {
        cerr << "[" << NAME << "] " << __func__ << " no victim! set: " << set << endl;
        assert(0);
    }

    return way;
}

void CACHE::lru_update(uint32_t set, uint32_t way)
{
    // update lru replacement state
    for (uint32_t i=0; i<NUM_WAY; i++) {
        if (block[set][i].lru < block[set][way].lru) {
            block[set][i].lru++;
        }
    }
    block[set][way].lru = 0; // promote to the MRU position
}

typedef struct temp_block {
    uint32_t way;
    uint32_t slru_pos;
} temp_block;

void CACHE::slru_update(uint32_t set, uint32_t way)
{
    block_group myGroup = block[set][way].current_group;

    vector<temp_block> tempSet;

    // update slru replacement state
    for (uint32_t i = 0; i < NUM_WAY; i++) {
        if (block[set][i].current_group == myGroup) {
            tempSet.push_back(temp_block{i, block[set][i].slru});
        }
    }

    sort(tempSet.begin(), tempSet.end(), [](const temp_block &lhs, const temp_block &rhs)
         { return lhs.slru_pos < rhs.slru_pos; });
    
    uint32_t tempPos = 1;
    for (auto ele : tempSet) {
        block[set][ele.way].slru = tempPos++;
    }

    block[set][way].slru = 0; // promote current block to the MRU position
}

uint32_t CACHE::slru_victim(uint32_t cpu, uint64_t instr_id, uint32_t set, const BLOCK *current_set, uint64_t ip, uint64_t full_addr, uint32_t type)
{
    uint32_t way = 0;

    for (way = 0; way < NUM_WAY; way++)
    {
        if (block[set][way].valid == false)
        {
            return way;
        }
    }

    if (way == NUM_WAY)
    {
        uint32_t victimBlock = 0;
        uint32_t victimBlockSLRU = 0;

        // TODO: combine two loops into one loop
        for (way = 0; way < NUM_WAY; way++)
        {
            if (block[set][way].current_group == prob && (block[set][way].slru >= victimBlockSLRU))
            {
                victimBlock = way;
                victimBlockSLRU = block[set][way].slru;
            }
        }

        if (block[set][victimBlock].current_group == prob)
            return victimBlockSLRU;

        victimBlock = 0;
        victimBlockSLRU = 0;
        for (way = 0; way < NUM_WAY; way++)
        {
            if (block[set][way].current_group == prot && (block[set][way].slru >= victimBlock))
            {
                victimBlock = way;
            }
        }

        if (block[set][victimBlock].current_group == prot)
            return victimBlockSLRU;
    }

    std::cout << "DEBUG: No victim block found!\n";

    return 0; // Normally. this line should not be executed
}

void CACHE::replacement_final_stats()
{

}

#ifdef NO_CRC2_COMPILE
void InitReplacementState()
{
    
}

uint32_t GetVictimInSet (uint32_t cpu, uint32_t set, const BLOCK *current_set, uint64_t PC, uint64_t paddr, uint32_t type)
{
    return 0;
}

void UpdateReplacementState (uint32_t cpu, uint32_t set, uint32_t way, uint64_t paddr, uint64_t PC, uint64_t victim_addr, uint32_t type, uint8_t hit)
{
    
}

void PrintStats_Heartbeat()
{
    
}

void PrintStats()
{

}
#endif
