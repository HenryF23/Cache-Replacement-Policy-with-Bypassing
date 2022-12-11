# Cache-Replacement-Policy-with-Bypassing - Henry Fang & Haoyuan Zhao

## How to run
```bash
cd $repo
./run_all.sh $1 $2
```
$1 is the number of instructions for warmup (in millions).

$2 is the number of instructinos for simulationn (in millions).

This command will run all variant of our implemented replacement policies (6 of them) using all benchmarks (20 of them)

## How to plot diagram
```bash
cd $repo
cd /plot
python3 plot.py
```
