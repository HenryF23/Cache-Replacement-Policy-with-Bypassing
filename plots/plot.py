import matplotlib.pyplot as plt
import seaborn as sns
import argparse
import pandas as pd

benchmark = ["600.perlbench_s-210B.champsimtrace.xz", "602.gcc_s-734B.champsimtrace.xz", "625.x264_s-18B.champsimtrace.xz", "641.leela_s-800B.champsimtrace.xz", "648.exchange2_s-1699B.champsimtrace.xz"]

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

candidate_repla = ["lru_bp", "lru"]
baseline = read_data("lru")

final_result = pd.DataFrame(data={"Benchmark": [], "Relative hit rate": [], "Policy": []})


# for ben in benchmark:
for rep in candidate_repla:
  result = read_data(rep)
  result["Policy"] = rep
  result["Relative hit rate"] = result["Hit rate"] / baseline["Hit rate"]
  final_result = pd.concat([final_result, result], ignore_index=True)

sns.set(rc={'figure.figsize':(18,7)})
ax = sns.barplot(data = final_result, x="Benchmark", y="Relative hit rate", hue='Policy')
plt.savefig("test.png", format='png', dpi=600)

