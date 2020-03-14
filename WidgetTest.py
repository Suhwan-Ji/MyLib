import numpy as np
import pandas as pd
import tkinter as tk
from tkinter import ttk
from line_manager import *


# Dummy Data
data = pd.DataFrame()
data_len = 3000
data['time'] = np.arange(data_len)
data['sin'] = 5* np.sin(2*np.pi*5*data['time'])
data['cos'] = 2* np.cos(2*np.pi*3*data['time']+10)
data['random'] = np.random.randn(data_len)

# create window
win = tk.Tk()
win.geometry("640x400+100+100")


lc = LineContainer(win)
container = lc.container
container.pack()


lc.add_linewidget(data,'sin')
lc.add_linewidget(data,'cos')
lc.add_linewidget(data,'random')

win.mainloop()

