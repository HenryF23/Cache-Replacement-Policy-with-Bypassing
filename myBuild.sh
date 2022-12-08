#!/bin/bash
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

./build_champsim.sh perceptron no no no $1 1
# $2	number of instructions for warmup (1 million)
# $3	number of instructinos for detailed simulation (10 million)

if [[ $2 == "test" ]]
then
    echo "Running in test mode"
    echo "Running 602.gcc_s-734B.champsimtrace.xz..."
    ./run_champsim.sh perceptron-no-no-no-$1-1core 1 5 602.gcc_s-734B.champsimtrace.xz
else
    echo "Running 600.perlbench_s-210B.champsimtrace.xz..."
    ./run_champsim.sh perceptron-no-no-no-$1-1core $2 $3 600.perlbench_s-210B.champsimtrace.xz
    echo "Running 602.gcc_s-734B.champsimtrace.xz..."
    ./run_champsim.sh perceptron-no-no-no-$1-1core $2 $3 602.gcc_s-734B.champsimtrace.xz
    echo "Running 625.x264_s-18B.champsimtrace.xz..."
    ./run_champsim.sh perceptron-no-no-no-$1-1core $2 $3 625.x264_s-18B.champsimtrace.xz
    echo "Running 641.leela_s-800B.champsimtrace.xz..."
    ./run_champsim.sh perceptron-no-no-no-$1-1core $2 $3 641.leela_s-800B.champsimtrace.xz
    echo "Running 648.exchange2_s-1699B.champsimtrace.xz..."
    ./run_champsim.sh perceptron-no-no-no-$1-1core $2 $3 648.exchange2_s-1699B.champsimtrace.xz
fi

echo "Done!"
