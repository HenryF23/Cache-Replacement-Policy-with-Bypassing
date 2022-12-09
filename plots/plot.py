import matplotlib.pyplot as plt
import seaborn as sns
import argparse
import pandas as pd

benchmark = ["600.perlbench_s-210B.champsimtrace.xz", "619.lbm_s-4268B.champsimtrace.xz", "627.cam4_s-573B.champsimtrace.xz", "644.nab_s-5853B.champsimtrace.xz", "602.gcc_s-734B.champsimtrace.xz", "620.omnetpp_s-874B.champsimtrace.xz", "628.pop2_s-17B.champsimtrace.xz", "648.exchange2_s-1699B.champsimtrace.xz", "603.bwaves_s-3699B.champsimtrace.xz", "621.wrf_s-575B.champsimtrace.xz", "631.deepsjeng_s-928B.champsimtrace.xz", "649.fotonik3d_s-1176B.champsimtrace.xz", "605.mcf_s-665B.champsimtrace.xz", "623.xalancbmk_s-700B.champsimtrace.xz", "654.roms_s-842B.champsimtrace.xz", "607.cactuBSSN_s-2421B.champsimtrace.xz", "625.x264_s-18B.champsimtrace.xz", "641.leela_s-800B.champsimtrace.xz", "657.xz_s-3167B.champsimtrace.xz"]

def read_data(replacement):
  short_ben = [x.split(".")[0] for x in benchmark]
  total_access = []
  total_miss = []
  miss_rate = []
  hit_rate = []
  for ben in benchmark:
    path = "../results_100M/{}-perceptron-no-no-no-{}-1core.txt".format(ben, replacement)
    file = open(path)
    lines = file.readlines()
    for line in lines:
      if line.find("Core_0_LLC_total_access") != -1:
        total_access.append(int(line.split(" ")[1]))
      elif line.find("Core_0_LLC_total_miss") != -1:
        total_miss.append(int(line.split(" ")[1]))
    miss_rate.append(total_miss[-1] / total_access[-1])
    hit_rate.append((total_access[-1] - total_miss[-1]) / total_access[-1])
  return pd.DataFrame(data={"Benchmark": short_ben, "Total access": total_access,"Total miss": total_miss, "Miss rate": miss_rate, "Hit rate": hit_rate})

# def q1():
#   sns.set(rc={'figure.figsize':(18,7)})
#   data_t = read_data("taken", "q1", [0])
#   data_not = read_data("not_taken", "q1", [0])
#   data_t['Predictor'] = "Always taken"
#   data_not['Predictor'] = "Always not taken"
#   data = pd.concat([data_t, data_not])
#   data.to_csv("q1_data.csv", index=False)

#   ax = sns.barplot(data = data, x="Predictor", y="Prediction Accuracy", hue='Benchmark')
#   sns.move_legend(ax, "upper left", bbox_to_anchor=(1, 1))
#   plt.xlabel("Predictor")
#   plt.ylabel("Accuracy(%)")
#   plt.title("Question 1: Always taken vs Always not taken")
#   # plt.ylim(70, 100)

#   plt.savefig("q1.png", format='png', dpi=600)

candidate_repla = ["slru", "lru_bp", "slru_with_bp", "slru_lru_and_selector", "slru_lru_with_bp_and_selector"]
baseline = read_data("lru")
baseline["Policy"] = "lru"

final_result = pd.DataFrame(data={"Benchmark": [], "Relative hit rate": [], "Policy": []})


# for ben in benchmark:
for rep in candidate_repla:
  result = read_data(rep)
  result["Policy"] = rep
  result["Relative hit rate"] = result["Hit rate"] / baseline["Hit rate"]
  result["Relative miss rate"] = result["Miss rate"] / baseline["Miss rate"]
  final_result = pd.concat([final_result, result], ignore_index=True)

sns.set(rc={'figure.figsize':(18,7)})
ax = sns.barplot(data = final_result, x="Benchmark", y="Relative hit rate", hue='Policy')
plt.savefig("Relative hit rate.png", format='png', dpi=600)

plt.clf()
ax = sns.barplot(data = final_result, x="Benchmark", y="Relative miss rate", hue='Policy')
plt.savefig("Relative miss rate.png", format='png', dpi=600)

final_result = pd.concat([final_result, baseline], ignore_index=True)

plt.clf()
ax = sns.barplot(data = final_result, x="Benchmark", y="Total access", hue='Policy')
ax.set(yscale="log")
plt.savefig("Total access.png", format='png', dpi=600)

plt.clf()
ax = sns.barplot(data = final_result, x="Benchmark", y="Total miss", hue='Policy')
ax.set(yscale="log")
plt.savefig("Total miss.png", format='png', dpi=600)

final_result.to_csv("raw_data.csv")