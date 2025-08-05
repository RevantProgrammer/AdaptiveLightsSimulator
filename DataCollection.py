import pandas as pd
import os

features = ["CarsPassed", "PhaseDir", "TimeWaited", "EmergencyWaitTime", "TimeOfDay"]
file_name = "TrafficData.csv"
if os.path.exists(file_name):
    data = pd.read_csv(file_name).to_dict(orient="list")
else:
    data = {x: [] for x in features}


def add_entry(dic, *args):
    for i, arg in enumerate(args):
        dic[features[i]].append(arg)


print(data)
add_entry(data, 6, 5, 24.6, 0, 1)
print(data)

df = pd.DataFrame(data)
df.to_csv(file_name, index=False)
