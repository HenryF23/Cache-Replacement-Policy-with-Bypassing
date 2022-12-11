import matplotlib.pyplot as plt
import seaborn as sns
import argparse
import pandas as pd

# All benchmarks
benchmark = ["600.perlbench_s-210B.champsimtrace.xz", "619.lbm_s-4268B.champsimtrace.xz", "627.cam4_s-573B.champsimtrace.xz", "644.nab_s-5853B.champsimtrace.xz", "602.gcc_s-734B.champsimtrace.xz", "620.omnetpp_s-874B.champsimtrace.xz", "628.pop2_s-17B.champsimtrace.xz", "648.exchange2_s-1699B.champsimtrace.xz", "603.bwaves_s-3699B.champsimtrace.xz", "621.wrf_s-575B.champsimtrace.xz", "631.deepsjeng_s-928B.champsimtrace.xz", "649.fotonik3d_s-1176B.champsimtrace.xz", "605.mcf_s-665B.champsimtrace.xz", "623.xalancbmk_s-700B.champsimtrace.xz", "654.roms_s-842B.champsimtrace.xz", "607.cactuBSSN_s-2421B.champsimtrace.xz", "625.x264_s-18B.champsimtrace.xz", "641.leela_s-800B.champsimtrace.xz", "657.xz_s-3167B.champsimtrace.xz", "638.imagick_s-10316B.champsimtrace.xz"]

# selected benchmarks
# benchmark = ["600.perlbench_s-210B.champsimtrace.xz", "627.cam4_s-573B.champsimtrace.xz", "644.nab_s-5853B.champsimtrace.xz", "602.gcc_s-734B.champsimtrace.xz", "628.pop2_s-17B.champsimtrace.xz", "621.wrf_s-575B.champsimtrace.xz", "654.roms_s-842B.champsimtrace.xz", "619.lbm_s-4268B.champsimtrace.xz"]


def read_data(replacement):
  short_ben = [x.split(".")[0] for x in benchmark]
  total_access = []
  total_miss = []
  miss_rate = []
  hit_rate = []
  miss_latency = []

  for ben in benchmark:
    path = "../results_100M/{}-perceptron-no-no-no-{}-1core.txt".format(ben, replacement)
    file = open(path)
    lines = file.readlines()
    for line in lines:
      if line.find("Core_0_LLC_total_access") != -1:
        total_access.append(int(line.split(" ")[1]))
      elif line.find("Core_0_LLC_total_miss") != -1:
        total_miss.append(int(line.split(" ")[1]))
      elif line.find("Core_0_LLC_average_miss_latency") != -1:
        miss_latency.append(float(line.split(" ")[1]))
    miss_rate.append(total_miss[-1] / total_access[-1])
    hit_rate.append((total_access[-1] - total_miss[-1]) / total_access[-1])
  return pd.DataFrame(data={"Benchmark": short_ben, "Total access": total_access,"Total miss": total_miss, "Miss rate": miss_rate, "Hit rate": hit_rate, "Miss latency": miss_latency})

# candidate_repla = ["slru", "lru_bp", "slru_with_bp", "slru_lru_and_selector", "slru_lru_with_bp_and_selector"]
# readable_name = ["SLRU", "LRU + bypass", "SLRU + bypass", "SLRU + selector", "SLRU + bypass + selector"]

candidate_repla = ["lru_bp", "lru_bp_without_vr"]
readable_name = ["LRU + bypass", "LRU + bypass (no virtual bypass)"]


baseline = read_data("lru")
baseline["Policy"] = "LRU"

final_result = pd.DataFrame(data={"Benchmark": [], "Relative hit rate": [], "Policy": []})


# for ben in benchmark:
for index, rep in enumerate(candidate_repla):
  result = read_data(rep)
  result["Policy"] = readable_name[index]
  result["Relative hit rate"] = result["Hit rate"] / baseline["Hit rate"]
  result["Relative miss rate"] = result["Miss rate"] / baseline["Miss rate"]
  result["Relative miss latency"] = result["Miss latency"] / baseline["Miss latency"]
  final_result = pd.concat([final_result, result], ignore_index=True)

final_result = final_result.sort_values(by = ["Benchmark"])

# # For virtual bypass test
# sns.set(rc={'figure.figsize':(7,4)})
# ax = sns.barplot(data = final_result, x="Benchmark", y="Hit rate", hue='Policy', hue_order=readable_name)
# plt.savefig("Hit rate for virtual.pdf", format='pdf', dpi=300, bbox_inches='tight')

sns.set(rc={'figure.figsize':(18,7)})
ax = sns.barplot(data = final_result, x="Benchmark", y="Relative hit rate", hue='Policy', hue_order=readable_name)
plt.savefig("Relative hit rate.pdf", format='pdf', dpi=600, bbox_inches='tight')

plt.clf()
ax = sns.barplot(data = final_result, x="Benchmark", y="Relative miss rate", hue='Policy', hue_order=readable_name)
plt.savefig("Relative miss rate.pdf", format='pdf', dpi=600, bbox_inches='tight')

# Add the baseline data for other non-relative diagram
final_result = pd.concat([final_result, baseline], ignore_index=True)
readable_name = ["LRU"] + readable_name

plt.clf()
ax = sns.barplot(data = final_result, x="Benchmark", y="Total access", hue='Policy')
ax.set(yscale="log")
plt.savefig("Total access.png", format='png', dpi=600)

plt.clf()
ax = sns.barplot(data = final_result, x="Benchmark", y="Total miss", hue='Policy')
ax.set(yscale="log")
plt.savefig("Total miss.png", format='png', dpi=600)

plt.clf()
ax = sns.barplot(data = final_result, x="Benchmark", y="Miss latency", hue='Policy', hue_order=readable_name)
# ax.set(yscale="log")
plt.savefig("Miss latency.pdf", format='pdf', dpi=600, bbox_inches='tight')

final_result.to_csv("raw_data.csv")