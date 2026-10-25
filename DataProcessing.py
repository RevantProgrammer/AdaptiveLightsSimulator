import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import ttest_ind, mannwhitneyu

real_data = pd.read_csv("TrafficData.csv")
sim_data = pd.read_csv("SlowSimData.csv")

sim_data_phase_wait = sim_data["P2ClearRate"].mean()
real_data_phase = real_data.loc[real_data["PhaseDir"] == 6]
real_cars_in_phase = real_data_phase["CarsPassed"].sum()
real_time_waited = real_data_phase["TimeWaited"].sum()

# print(sim_data_phase_wait, real_cars_in_phase/real_time_waited)

real_car_waits = []
sim_car_waits = []
with open("CarWaits.txt", "r") as f:
    for line in f.readlines():
        real_car_waits.append(float(line.strip()))

with open("SlowSimCarWaits.txt", "r") as f:
    for line in f.readlines():
        sim_car_waits.append(float(line.strip()))
real_car_waits = np.array(real_car_waits)
sim_car_waits = np.array(sim_car_waits)


def summarize(arr, zeroes=True):
    if not zeroes:
        a = arr[arr != 0]
    else:
        a = arr
    return {
      'n': len(a),
      'mean': a.mean(),
      'median': np.percentile(a, 50),
      'std': a.std(ddof=1),
      'min': a.min(),
      'max': a.max(),
      'IQR': np.percentile(a, 75) - np.percentile(a, 25),
      'CV': a.std(ddof=1)/arr.mean() if arr.mean()!=0 else None,
      'zeros_pct': (arr==0).mean()  # works on all arrays
    }


def bootstrap_ci(a, n_boot=2000, alpha=0.05):
    means = [np.mean(np.random.choice(a, size=len(a), replace=True)) for _ in range(n_boot)]
    return np.percentile(means, [100*alpha/2, 100*(1-alpha/2)])


def cohens_d(a, b):
    na, nb = len(a), len(b)
    pooled = np.sqrt(((na-1)*a.var(ddof=1) + (nb-1)*b.var(ddof=1)) / (na+nb-2))
    return (a.mean() - b.mean()) / pooled


def cliffs_delta(a, b):
    n1, n2 = len(a), len(b)
    greater = sum(x > y for x in a for y in b)
    less = sum(x < y for x in a for y in b)
    return (greater - less) / (n1 * n2)


def subsample_tests(real_queue, sim_queue, R=1000):
    n = len(real_queue)
    ps = []
    deltas = []
    for _ in range(R):
        sample = np.random.choice(sim_queue, size=n, replace=False)
        u, p = mannwhitneyu(real_queue, sample, alternative='two-sided')
        d = cliffs_delta(real_queue, sample)
        ps.append(p)
        deltas.append(d)
    return np.array(ps), np.array(deltas)


print(summarize(real_car_waits))
print(summarize(sim_car_waits))

sns.set_style("whitegrid")
sns.set_context("talk", font_scale=0.9)
sns.set_palette("Set2")

sns.kdeplot(real_car_waits, label='Real Car Waits', fill=True, color='#d9534f')
sns.kdeplot(sim_car_waits, label='Simulation Car Waits', fill=True, color='#5cb85c')
plt.axvline(np.median(real_car_waits), color='red', linestyle='--', linewidth=2, label=f'Real wait times median = {np.median(real_car_waits):.2f}')
plt.axvline(np.median(sim_car_waits), color='green', linestyle='--', linewidth=2, label=f'Simulation wait times median = {np.median(sim_car_waits):.2f}')
plt.legend()
plt.xlabel("Car Wait Times (s)")
plt.title("Comparison of Car Wait Time Distributions: Real vs Simulation")
plt.show()


# sns.boxplot(data=[real_car_waits, sim_car_waits])
# plt.xticks([0, 1], ['Real', 'Sim'])
# plt.ylabel('Wait (s)')
# plt.show()

u, p = mannwhitneyu(real_car_waits, sim_car_waits, alternative='two-sided')
t, p_t = ttest_ind(real_car_waits, sim_car_waits, equal_var=False)
ci_real = bootstrap_ci(real_car_waits)
ci_sim = bootstrap_ci(sim_car_waits)
d1 = cohens_d(real_car_waits, sim_car_waits)
d2 = cliffs_delta(real_car_waits, sim_car_waits)
print(d1, d2)
print(ci_real, ci_sim)
print(u, p)
print(t, p_t)

p_vals, deltas = subsample_tests(real_car_waits, sim_car_waits)
print("Prop p<0.05:", (p_vals < 0.05).mean())
print(summarize(p_vals))
print(summarize(deltas))

# sns.boxplot(p_vals)
# plt.show()

plt.figure(figsize=(6, 4))
# sns.histplot(p_vals, bins=20, color='#69b3a2', edgecolor='black', alpha=0.7)
sns.kdeplot(p_vals, fill=True, color='#69b3a2', alpha=0.6, linewidth=2)
plt.axvline(0.05, color='red', linestyle='--', linewidth=2, label='α = 0.05')

plt.xscale('log')
plt.xlabel("p-value (log scale)")
plt.ylabel("Frequency")
plt.title("Distribution of p-values (log scale)")
plt.legend()
plt.tight_layout()
plt.show()

plt.figure(figsize=(6,4))
sns.kdeplot(deltas, fill=True, color='#69b3a2', alpha=0.6, linewidth=2)
# sns.histplot(deltas, bins=20, color='#ffb347', edgecolor='black', alpha=0.7)
plt.axvline(0, color='gray', linestyle='--', linewidth=2)
plt.axvline(0.147, color='green', linestyle='--', linewidth=2)
plt.axvline(0.33, color='orange', linestyle='--', linewidth=2)
plt.axvline(0.474, color='red', linestyle='--', linewidth=2)
mean_dels = np.mean(deltas)
plt.axvline(mean_dels, color='blue', linestyle=':', linewidth=1, label=f'Mean = {mean_dels:.3f}')

plt.xlabel("Cliff's Delta (δ)")
plt.ylabel("Frequency")
plt.title("Distribution of Effect Sizes (Cliff's δ)")
plt.text(0.05, plt.ylim()[1]*0.9, "Negligible", color='gray')
plt.text(0.23, plt.ylim()[1]*0.9, "Small", color='green')
plt.text(0.38, plt.ylim()[1]*0.9, "Medium", color='orange')
plt.text(0.50, plt.ylim()[1]*0.9, "Large", color='red')
plt.xlim(0, 0.55)
plt.tight_layout()
plt.legend()
plt.show()

means = [real_car_waits.mean(), sim_car_waits.mean()]
cis_lower = [ci_real[0], ci_sim[0]]
cis_upper = [ci_real[1], ci_sim[1]]
error_lower = np.array(means) - np.array(cis_lower)
error_upper = np.array(cis_upper) - np.array(means)

bars = plt.bar(['Real', 'Simulation'], means, yerr=[error_lower, error_upper],
               capsize=10, color=['#d9534f', '#5cb85c'], alpha=0.8)

# Add text on top of bars
plt.axhline(means[0], color='red', linestyle='--', alpha=0.6)
plt.axhline(means[1], color='green', linestyle='--', alpha=0.6)
plt.text(0.42, means[0]+0.9, f'Mean: {means[0]:.2f}s', fontsize=8, color='black')
plt.text(0.42, means[1]+0.9, f'Mean: {means[1]:.2f}s', fontsize=8, color='black')

plt.ylabel('Mean Wait Time (s)')
plt.title('Mean Wait Time with 95% Confidence Intervals')
plt.grid(axis='y', alpha=0.3)
plt.show()


real_sorted = np.sort(real_car_waits)
sim_sorted = np.sort(sim_car_waits)
plt.plot(real_sorted, np.arange(1,len(real_sorted)+1)/len(real_sorted),
         label='Real', color='red', linewidth=2)
plt.plot(sim_sorted, np.arange(1,len(sim_sorted)+1)/len(sim_sorted),
         label='Simulation', color='green', linewidth=2)

plt.axhline(0.5, color='gray', linestyle='--', alpha=0.6)
plt.text(70, 0.52, "Median wait time", fontsize=8, color='gray')
plt.xlim(0, max(max(real_sorted), max(sim_sorted)))
plt.ylim(0, 1.0)
plt.xlabel('Wait Time (s)')
plt.ylabel('Proportion of Cars Cleared')
plt.title('Cumulative Wait-Time Distribution')
plt.legend()
plt.grid(alpha=0.3)
plt.show()
