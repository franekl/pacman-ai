#%%
import matplotlib.pyplot as plt

# Coordinates of the nodes
nodes = [
    (16, 64), (96, 64), (192, 64), (240, 64), (336, 64), (416, 64),
    (16, 128), (96, 128), (144, 128), (192, 128), (240, 128), (288, 128), (336, 128), (416, 128),
    (16, 176), (96, 176), (144, 176), (192, 176), (240, 176), (288, 176), (336, 176), (416, 176),
    (144, 224), (192, 224), (240, 224), (288, 224),
    (0, 272), (96, 272), (144, 272), (288, 272), (336, 272), (432, 272),
    (144, 320), (288, 320),
    (16, 368), (96, 368), (144, 368), (192, 368), (240, 368), (288, 368), (336, 368), (416, 368),
    (16, 416), (48, 416), (96, 416), (144, 416), (192, 416), (240, 416), (288, 416), (336, 416), (384, 416), (416, 416),
    (16, 464), (48, 464), (96, 464), (144, 464), (192, 464), (240, 464), (288, 464), (336, 464), (384, 464), (416, 464),
    (16, 512), (192, 512), (240, 512), (416, 512)
]

# Separating the coordinates for plotting
x, y = zip(*nodes)

plt.figure(figsize=(12, 8))
plt.scatter(x, y, c='blue')  # Nodes as yellow dots to simulate Pac-Man style

# Adding coordinates above each dot
for i, txt in enumerate(nodes):
    plt.annotate(f"{txt}", (x[i], y[i]), textcoords="offset points", xytext=(0,10), ha='center')

plt.gca().invert_yaxis()  # Inverting the y-axis to match the typical game coordinate system
plt.title('Pac-Man Game Level Nodes with Coordinates')
plt.xlabel('X Coordinate')
plt.ylabel('Y Coordinate')
plt.grid(True)
plt.show()
# %%
