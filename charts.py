# %%
from email.mime import audio
import pandas as pd
import matplotlib.pyplot as plt

headers = ['Multiplier', 'Time', 'Nodes Explored', 'Distance']

euclidean_df = pd.read_csv('data/euclidean.csv', names = headers)
manhattan_df = pd.read_csv('data/manhattan.csv', names = headers)

print(f"Printing Euclidean dataset")
print(euclidean_df)
print(f"Printing Manhattan dataset")
print(manhattan_df)

# %% 
euclidean_fig, ax1 = plt.subplots()

mult = euclidean_df["Multiplier"]

nodes = euclidean_df["Nodes Explored"]
dist = euclidean_df["Distance"]

ax1.set_xlabel('Multiplier')
ax1.set_ylabel('Nodes Explored')
color = 'tab:orange'
ax1.plot(mult, nodes, color=color)

ax2 = ax1.twinx()

color = 'tab:blue'
ax2.set_ylabel('Distance of path found')
ax2.plot(mult, dist, color=color)

plt.title("Euclidean Time vs Optimality")
plt.show()

# %%

# %%
manhatten_fig, ax1 = plt.subplots()

mult = manhattan_df["Multiplier"]

nodes = manhattan_df["Nodes Explored"]
dist = manhattan_df["Distance"]

ax1.set_xlabel('Multiplier')
ax1.set_ylabel('Nodes Explored')
color = 'tab:orange'
ax1.plot(mult, nodes, color=color)

ax2 = ax1.twinx()

color = 'tab:blue'
ax2.set_ylabel('Distance of path found')
ax2.plot(mult, dist, color=color)

plt.title("Manhattan Time vs Optimality")
plt.show()
# %%