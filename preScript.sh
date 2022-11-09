#!/bin/bash
cd "$(dirname "$0")"
if [[ -z "${TRACE_DIR}" ]]
then
    echo "Added PATH for TRACE_DIR"
    export TRACE_DIR=/data/dpc3_traces/
fi

if [[ -z "${LAB_PATH}" ]]
then
    echo "Added PATH for LAB_PATH"
    export LAB_PATH=/data/home/fanghaof/Cache-Replacement-Policy-with-Bypassing
fi
