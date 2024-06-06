#%%
import pandas as pd
import pickle


#%%
#load pickled file
with open('qt.pkl', 'rb') as f:
    q_table = pickle.load(f)
# %%
q_table
# %%


#%%
#load pickled file
with open('scores.pkl', 'rb') as f:
    scores = pickle.load(f)
# %%
scores
# %%
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
def read_scores(file_path):
    scores = []
    with open(file_path, 'r') as file:
        for line in file:
            try:
                score = float(line.strip())
                scores.append(score)
            except ValueError:
                continue  # Skip lines that cannot be converted to float
    return scores

def average_scores(scores, interval):
    averaged_scores = []
    for i in range(0, len(scores), interval):
        interval_scores = scores[i:i + interval]
        if interval_scores:
            average_score = sum(interval_scores) / len(interval_scores)
            averaged_scores.append(average_score)
    return averaged_scores

def plot_scores(scores, averaged_scores, interval):
    episodes = list(range(1, len(scores) + 1))
    avg_episodes = list(range(interval, len(averaged_scores) * interval + 1, interval))
    
    plt.figure(figsize=(10, 5))
    
    # Plot greyed out dots for all scores
    plt.scatter(episodes, scores, color='grey', alpha=0.15)
    
    # Plot averaged scores with a red line
    plt.plot(avg_episodes, averaged_scores, linestyle='-', color='red', lw=2)
    
    plt.title('Q-Learning Convergence: Scores over Episodes')
    plt.xlabel('Episodes')
    plt.ylabel('Scores')
    plt.grid(True)
    plt.ylim(0, 7000)
    plt.savefig("qlearning_convergence_more_features.png", dpi=300)
    plt.show()

# Replace 'scores.txt' with the path to your text file containing the scores
file_path = 'scores.txt'
scores = read_scores(file_path)

# Calculate the average score for every 5 episodes
interval = 15
averaged_scores = average_scores(scores[:1001], interval)

# Plot the scores and averaged scores
plot_scores(scores[:1001], averaged_scores, interval)
# %%
len(scores)
# %%
