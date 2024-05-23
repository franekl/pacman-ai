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
