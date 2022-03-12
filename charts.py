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
color = 'tab:red'
ax1.plot(mult, nodes, color=color, label='Nodes Explored')


ax2 = ax1.twinx()

color = 'tab:blue'
ax2.set_ylabel('Distance of path found')
ax2.plot(mult, dist, color=color, label='Path Distance')

ax1.legend(loc=2)
ax2.legend(loc=1)

plt.title("Optimality Plot for Euclidean Distance")
plt.show()

# %%
manhatten_fig, ax1 = plt.subplots()

mult = manhattan_df["Multiplier"]

nodes = manhattan_df["Nodes Explored"]
dist = manhattan_df["Distance"]

ax1.set_xlabel('Multiplier')
ax1.set_ylabel('Nodes Explored')
color = 'tab:red'
ax1.plot(mult, nodes, color=color, label='Nodes Explored')

ax2 = ax1.twinx()

color = 'tab:blue'
ax2.set_ylabel('Distance of path found')
ax2.plot(mult, dist, color=color, label='Path Distance')

ax1.legend(loc=2)
ax2.legend(loc=1)

plt.title("Optimality Plot for Manhattan Distance")
plt.show()
# %%