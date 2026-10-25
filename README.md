# Adaptive Lights Simulator

A Pygame simulation of a four-way intersection controlled by **adaptive traffic lights**, plus a statistics script that compares simulated car wait times against wait times collected by hand at a real intersection (Gungahlin, ACT).

Instead of cycling through phases on a fixed timer, the adaptive controller looks at how many cars are queued in each phase and how long they have been waiting, then gives the green to the phase that "costs" the most. Emergency vehicles get priority.

## Features

- 600×600 top-down intersection with a traffic light drawn at each corner
- Four approaches (north, south, east, west), each with two queues:
  - `F`/`R`: a shared forward + kerbside-turn lane
  - `L`: a turn lane that crosses oncoming traffic, served by its own protected turn phase
- Up to 9 queued cars per lane, with turning cars following curved paths through the intersection
- Four signal phases with a yellow/clearance interval between them:

  | Phase | Movement |
  |-------|----------|
  | 1 | North + South `L` turn lanes |
  | 2 | North + South `F`/`R` lanes |
  | 3 | East + West `L` turn lanes |
  | 4 | East + West `F`/`R` lanes |

- Several light controllers (see [Controllers](#controllers))
- Several traffic generators: uniform random, sinusoidal (demand swings between the N/S and E/W roads), and custom per-direction probabilities
- Emergency vehicles (about a 1% chance per spawned car, drawn in white)
- The car that has waited longest slowly fades to black, so starvation is easy to spot
- Every run records KPIs to CSV for later analysis

## Requirements

- Python 3.10 or newer (the code uses `match` statements)
- The packages in `requirements.txt` (pygame, numpy, pandas, scipy, matplotlib, seaborn)

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
```

## Running the simulation

Run it from the project root so the `images/` folder is found:

```bash
python ATLSimulation.py
```

A run lasts **100 seconds**, or until you close the window. Afterwards a summary is printed to the console and the results are saved (see [Output data](#output-data)).

### Controls

| Key | Action |
|-----|--------|
| `N` / `S` / `E` / `W` | Spawn a car on the north / south / east / west approach |
| `B` | Pause or resume the light controller |
| `1`–`4` | Force a phase |
| `Q` | Print the mouse position to the console (debugging) |

### Configuration

All settings are near the top of the main loop in `ATLSimulation.py`:

| Setting | Default | Meaning |
|---------|---------|---------|
| `minim` | `True` | `True`: a car spawns every 0.4 s (denser traffic) and results go to `SlowSim*`. `False`: a car every 0.67 s, results go to `FastSim*` |
| `CAR_VEL` | `2` | Car speed. Green and yellow timings scale with it |
| `MAX_CARS_PER_LANE` | `9` | Queue capacity per lane |
| run length | `100` s | The `elapsed > 100` check in the main loop |
| generator | `sinusoidal_car_generation` | Swap for `random_car_generation` or `custom_car_generation` (with `custom_prob`) |
| controller | `control_smart_lights_v3` | Swap for any controller below (both calls in the main loop) |

## Controllers

Each controller is called every frame. It returns `"yellow"` when the current phase should end. When called with `decide=True` it returns the next phase to serve.

| Function | Strategy |
|----------|----------|
| `control_standard_lights` | Fixed-time baseline that cycles 1 → 2 → 3 → 4 with a short fixed green |
| `control_smart_lights_v1` | Picks the highest-cost phase. Green length scales with √(queue length), capped |
| `control_smart_lights_v2` | Keeps a minimum green, then ends the phase early once its queue is empty or another phase's cost passes a threshold |
| `control_smart_lights_v3` | v2 plus emergency vehicle priority, and it won't cut a phase until the cars it was called for have cleared |

The cost of a phase grows quickly with both queue length and wait time:

```
cost(cars, t) = (cars + 1) ^ (0.1 · t) + cars / 50
```

In v3, `t` is the wait time of the oldest car in that phase. When an emergency vehicle is queued, v3 switches to the phase with the most emergency vehicles, breaking ties by whichever has waited longest.

## Output data

When a run ends, `ATLSimulation.py` **appends** one row to `SlowSimData.csv` or `FastSimData.csv` (depending on `minim`):

| Column | Meaning |
|--------|---------|
| `P1ClearRate` … `P4ClearRate` | Cars cleared per second by each phase group |
| `AvgPhaseWait`, `MedianPhaseWait` | Time each phase waited before getting a green (s) |
| `AvgCarWait`, `MedianCarWait`, `MaxCarWait` | Per-car wait from spawning to entering the intersection (s) |
| `MaxEmWait` | Longest emergency vehicle wait, or `No emergency` |

Each car's wait time (1.2 s or more) is also appended to `SlowSimCarWaits.txt` / `FastSimCarWaits.txt`, one value per line. A small random reaction delay (|N(2, 1)| seconds) is added to every wait so the numbers are closer to real drivers.

## Real-world comparison

`DataProcessing.py` compares the simulated waits with data collected at a real intersection:

```bash
python DataProcessing.py
```

It loads `TrafficData.csv`, `CarWaits.txt` and `SlowSimCarWaits.txt`, then:

- prints summary statistics (mean, median, std, IQR, CV and more) for real and simulated waits
- runs a Mann–Whitney U test and Welch's t-test
- computes bootstrap 95% confidence intervals, Cohen's d and Cliff's δ
- repeats the Mann–Whitney test on 1000 random simulation subsamples the same size as the real sample
- plots wait-time KDEs, the p-value and effect-size distributions, means with CIs, and cumulative wait-time curves

### Real data files

- `TrafficData.csv`: one row per observed phase, with the columns `CarsPassed, PhaseDir, Lane, TimeWaited, EmergencyWaitTime, TimeOfDay`
- `CarWaits.txt`: individual observed car wait times in seconds, one per line
- `DataCollectionFormat.txt`: the collection plan and the codes used for `PhaseDir`, `Lane` and `TimeOfDay`

## Project structure

```
.
├── ATLSimulation.py          # Pygame simulation and light controllers
├── DataProcessing.py         # Real vs. simulated statistical comparison
├── DataCollectionFormat.txt  # Field data collection plan and codes
├── TrafficData.csv           # Real per-phase observations
├── CarWaits.txt              # Real per-car wait times
├── SlowSimData.csv           # Simulation KPIs (minim = True)
├── SlowSimCarWaits.txt       # Simulated per-car waits (minim = True)
├── FastSimData.csv           # Simulation KPIs (minim = False)
├── FastSimCarWaits.txt       # Simulated per-car waits (minim = False)
├── images/                   # Intersection background and light sprites
└── requirements.txt
```

## Credits

The rotated rectangle drawing in `draw_rectangle` is adapted from [Tim Swast's Replit example](https://replit.com/@TimSwast1/RotateARectanlge?v=1#main.py).
