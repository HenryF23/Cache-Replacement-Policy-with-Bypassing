#!/bin/bash
#
# SBATCH --cpus-per-task=8
# SBATCH --time=10:00
# SBATCH --mem=16G

declare -a ben=("600.perlbench_s-210B.champsimtrace.xz" "602.gcc_s-734B.champsimtrace.xz" "625.x264_s-18B.champsimtrace.xz" "641.leela_s-800B.champsimtrace.xz" "648.exchange2_s-1699B.champsimtrace.xz")
declare -a nonbp_replacement=("slru")
declare -a bp_replacement=("slru_with_bp" "slru_lru_with_bp_and_selector")

if [[ -z "${TRACE_DIR}" ]]
then
    echo "Added PATH for TRACE_DIR"
    export TRACE_DIR=/data/dpc3_traces/
fi

if [[ -z "${LAB_PATH}" ]]
then
    echo "Added PATH for LAB_PATH"
    export LAB_PATH=~/Cache-Replacement-Policy-with-Bypassing
fi

if [ "$#" -ne 2 ]; then
  echo "Please enter the number of instructions for warmup and the number of instructinos for detailed simulationn (in million)."
  exit
fi

for i in "${bp_replacement[@]}"
do
  ./build_champsim.sh perceptron no no no $i 1
  for j in "${ben[@]}"
  do
    echo "$i: Start to run $j..."
    ./run_champsim.sh perceptron-no-no-no-$i-1core $1 $2 $j
    echo "$i: $j run end"
  done
done

# Comment the bypass flag
sed -i "s/#define MY_BYPASS/\/\/ #define MY_BYPASS/" replacement/enhancement_switch.h
sed -i "s/#define VIRTUAL_BY/\/\/ #define VIRTUAL_BY/" replacement/enhancement_switch.h

for i in "${nonbp_replacement[@]}"
do
  ./build_champsim.sh perceptron no no no $i 1
  for j in "${ben[@]}"
  do
    echo "$i: Start to run $j..."
    ./run_champsim.sh perceptron-no-no-no-$i-1core $1 $2 $j
    echo "$i: $j run end"
  done
done

# Uncomment the bypass flag
sed -i "s/\/\/ #define MY_BYPASS/#define MY_BYPASS/" replacement/enhancement_switch.h
sed -i "s/\/\/ #define VIRTUAL_BY/#define VIRTUAL_BY/" replacement/enhancement_switch.h
