#include "cache.h"

// * SLRU
#include <cstdlib>
#include <time.h>

#define RANDOM_PROMOTION_PROB 32 // p = 1/32 gets promoted
#define RANDOM_PROMOTION_ACTIVE true
#define AGING_ACTIVE true

// initialize replacement state
void CACHE::llc_initialize_replacement()
{
    srand(time(0));
}

// find replacement victim
uint32_t CACHE::llc_find_victim(uint32_t cpu, uint64_t instr_id, uint32_t set, const BLOCK *current_set, uint64_t ip, uint64_t full_addr, uint32_t type)
{
    uint32_t way = 0;

    for (way = 0; way < NUM_WAY; way++) {
        if (block[set][way].valid == false) {
            return way;
        }
    }

    if (way == NUM_WAY) {
        uint32_t victimBlock = 0;
        uint32_t victimBlockSLRU = 0;
        for (way = 0; way < NUM_WAY; way++) {
            if (block[set][way].current_group == prob && (block[set][way].slru >= victimBlockSLRU)) {
                victimBlock = way;
                victimBlockSLRU = block[set][way].slru;
            }
        }

        if (block[set][victimBlock].current_group == prob)
            return victimBlockSLRU;

        victimBlock = 0;
        victimBlockSLRU = 0;
        for (way = 0; way < NUM_WAY; way++) {
            if (block[set][way].current_group == prot && (block[set][way].slru >= victimBlock)) {
                victimBlock = way;
            }
        }

        if (block[set][victimBlock].current_group == prot)
            return victimBlockSLRU;
    }

    std::cout << "DEBUG: No victim block found!\n";

    return 0; // Normally. this line should not be executed
}

// called on every cache hit and cache fill
void CACHE::llc_update_replacement_state(uint32_t cpu, uint32_t set, uint32_t way, uint64_t full_addr, uint64_t ip, uint64_t victim_addr, uint32_t type, uint8_t hit)
{
    string TYPE_NAME;
    if (type == LOAD)
        TYPE_NAME = "LOAD";
    else if (type == RFO)
        TYPE_NAME = "RFO";
    else if (type == PREFETCH)
        TYPE_NAME = "PF";
    else if (type == WRITEBACK)
        TYPE_NAME = "WB";
    else
        assert(0);

    if (hit)
        TYPE_NAME += "_HIT";
    else
        TYPE_NAME += "_MISS";

    if ((type == WRITEBACK) && ip)
        assert(0);

    // uncomment this line to see the LLC accesses
    // cout << "CPU: " << cpu << "  LLC " << setw(9) << TYPE_NAME << " set: " << setw(5) << set << " way: " << setw(2) << way;
    // cout << hex << " paddr: " << setw(12) << paddr << " ip: " << setw(8) << ip << " victim_addr: " << victim_addr << dec << endl;

    if (hit && (type == WRITEBACK)) // writeback hit does not update SLRU state
        return;

    if (!hit && (type == LOAD || type == RFO)) { // miss, newly allocated line
        // aging
        if (AGING_ACTIVE) {
            uint32_t tempSLRU = 0;
            for (uint32_t i = 0; i < way; i++)
            {
                if (i != way && block[set][way].valid && block[set][way].current_group == prot)
                {
                    if (block[set][way].slru >= tempSLRU)
                        tempSLRU = i;
                }
            }

            if (block[set][tempSLRU].valid && block[set][tempSLRU].current_group == prot)
            {
                block[set][way].current_group = prob;
                slru_update(set, way);
            }
        }

        // random promotion
        if (RANDOM_PROMOTION_ACTIVE) {
            if (RANDOM_PROMOTION_ACTIVE && rand() % 100 < RANDOM_PROMOTION_PROB)
                block[set][way].current_group = prot;
            else
                block[set][way].current_group = prob;

            slru_update(set, way);
        }

        // TODO: add virtual bypass
    }

    if (type != WRITEBACK && hit) {
        // move to protected
        block[set][way].current_group = prot;
        slru_update(set, way);
    }
}

void CACHE::llc_replacement_final_stats()
{
    
}
