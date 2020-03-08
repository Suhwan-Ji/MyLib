import tkinter as tk
from tkinter import ttk
import numpy as np
#import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.animation import FuncAnimation

from line_manager import *

def time_format(x):
    hour, rest = np.divmod(x, 3600)
    minute, rest = np.divmod(rest, 60)
    second, rest = np.divmod(rest, 60)
    return f"{hour}: {minute}: {second}.{rest}"


class TimeSeriesViewer():
    def __init__(self, data=None, time_col='time', draw_at_once=False):
        self.win = tk.Tk()
        self.win.title('TimeSeriesViewer_JSH')
        if data is not None:
            self.data = data
            self.datalist = data.columns[1:]
        else:
            # Data Reader
            pass
        self.time_col = time_col

        self.linelist = {}
        self.line_statemanager = {}

        self.scalelist = [0.1, 0.2, 0.5, 1, 5, 10, 50, 100]
        div = 0.1
        self.positionlist = np.arange(0, 10 + div, div)

        self.fig, ax = plt.subplots(2, 1, gridspec_kw={'height_ratios': [1, 5]}, figsize=(10, 8))

        self.main_pic = ax[1]
        self.main_pic.set_ylim(0, 10)
        self.main_pic.set_yticks([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        self.main_pic.grid(True)

        self.mp_start = tk.DoubleVar(value=0)
        self.mp_disp_step = tk.DoubleVar(value=300)
        self.mp_mv_step = tk.DoubleVar(value=60)

        self.create_canvas(self.win, [0, 0])
        self.create_data_list(self.win, [0, 1], draw_at_once)

        self.update_main_picture()

        self.win.mainloop()

    def create_canvas(self, master, grid_pos):
        container = ttk.LabelFrame(master, text='플로터')
        container.grid(row=grid_pos[0], column=grid_pos[1])

        self.canvas = FigureCanvasTkAgg(self.fig, master=container)
        self.canvas.get_tk_widget().grid(row=0, column=0)

        time_widget = ttk.LabelFrame(container, text='시간축')
        time_widget.grid(row=1, column=0)

        def move_pic(where=None):
            if where == 'left':
                tmpstep = -self.mp_mv_step.get()
            elif where == 'right':
                tmpstep = self.mp_mv_step.get()
            else:
                tmpstep = 0
            self.mp_start.set(self.mp_start.get() + tmpstep)
            self.update_main_picture()

        ttk.Button(time_widget, text='<<', command=lambda: move_pic(where='left')).grid(row=0, column=0)
        ttk.Button(time_widget, text='>>', command=lambda: move_pic(where='right')).grid(row=0, column=2)

        timemax = self.data[self.time_col][len(self.data) - 1]
        ttk.Scale(time_widget, orient=tk.HORIZONTAL, length=800, variable=self.mp_start, from_=0.0, to=timemax).grid(
            row=0, column=1)

        ttk.Label(time_widget, textvariable=self.mp_start).grid(row=1, column=1)
        ttk.Label(time_widget, textvariable=self.mp_disp_step).grid(row=1, column=2)
        ttk.Label(time_widget, textvariable=self.mp_mv_step).grid(row=1, column=3)

        tmp = lambda x: self.update_main_picture()
        self.ani = FuncAnimation(self.fig, tmp, interval=2000)

    def create_data_list(self, master, grid_pos, draw_at_once):
        container = ttk.LabelFrame(master, text='데이터 리스트')
        container.grid(row=grid_pos[0], column=grid_pos[1])

        choosers = ttk.LabelFrame(container, text='선택스')
        choosers.pack()

        param = {
            'func_draw': self._mp_draw_column,
            'func_change': self._change_line
        }
        dselected = tk.StringVar(value=self.datalist[0])
        ttk.Combobox(choosers, value=list(self.datalist), textvariable=dselected).grid(row=0, column=0)
        ttk.Button(choosers, text='Add',
                   command=lambda: self._add_linesatemanager(container, dselected.get(), **param)).grid(row=0, column=1)

        if draw_at_once:
            for i, dat in enumerate(self.datalist):
                self._add_linesatemanager(container, dat, **param)

    def update_main_picture(self):
        start = self.mp_start.get()
        end = start + self.mp_disp_step.get()
        self.main_pic.set_xlim(start, end)
        self.canvas.draw()

    def _mp_draw_column(self, data_col, **kwargs):
        if data_col not in self.linelist.keys():
            tmpline = LineManager(self.data[self.time_col], self.data[data_col], scalelist=self.scalelist,
                                  poslist=self.positionlist,**kwargs)
            self.main_pic.add_line(tmpline)
            self.linelist[data_col] = tmpline
        else:
            self.linelist[data_col].toggle_line()
        self.canvas.draw()

    def _change_line(self, data_col, item, method='+', step=1):
        if data_col not in self.linelist.keys():
            return 0
        line = self.linelist[data_col]
        line.change_state(item, method, step)
        self.canvas.draw()

    def _add_linesatemanager(self, master, col, func_draw, func_change):
        if col in self.line_statemanager.keys():
            return None
        manager = ttk.LabelFrame(master)
        self.line_statemanager[col] = manager
        manager.pack()
        ttk.Label(manager, text=col).grid(row=0, column=0, rowspan=4)
        ttk.Button(manager, text='Draw', command=lambda d=col: func_draw(d), width=5).grid(row=0, column=1, rowspan=4)
        ttk.Button(manager, text='pos ++', command=lambda d=col: func_change(d, 'position', method='+', step=10),
                   width=5).grid(row=0, column=2)
        ttk.Button(manager, text='pos +', command=lambda d=col: func_change(d, 'position', method='+', step=1),
                   width=5).grid(row=1, column=2)
        ttk.Button(manager, text='pos -', command=lambda d=col: func_change(d, 'position', method='-', step=1),
                   width=5).grid(row=2, column=2)
        ttk.Button(manager, text='pos --', command=lambda d=col: func_change(d, 'position', method='-', step=10),
                   width=5).grid(row=3, column=2)
        ttk.Button(manager, text='scale +', command=lambda d=col: func_change(d, 'scale', method='+', step=1),
                   width=5).grid(
            row=0, column=3, rowspan=2)
        ttk.Button(manager, text='scale -', command=lambda d=col: func_change(d, 'scale', method='-', step=1),
                   width=5).grid(
            row=2, column=3, rowspan=2)

        ttk.Button(manager, text='remove', command=lambda d=col: self._remove_line(d), width=5).grid(row=0, column=4,
                                                                                                     rowspan=4)

        self._mp_draw_column(col)

    def _remove_line(self, col):
        if col in self.line_statemanager.keys():
            self.line_statemanager[col].destroy()
            del self.line_statemanager[col]

        if col in self.linelist.keys():
            self.linelist[col].destroy()
            del self.linelist[col]
        self.canvas.draw()

if __name__ == '__main__':
    import pandas as pd
    import numpy as np
    data = pd.DataFrame()
    dlen = 30000
    Ts = 0.1
    data['time'] = np.arange(0, dlen * Ts, Ts)
    data['sin05'] = 1 * np.sin(2 * np.pi * 0.5 * data['time'])
    data['cos01'] = 1 * np.cos(2 * np.pi * 0.1 * data['time'])
    data['dat1'] = data['sin05'] + 2 * data['cos01']
    data['dat2'] = 1 * np.random.randn(dlen) + 2 * data['cos01'] + 2 * data['time']

    a = TimeSeriesViewer(data,draw_at_once=True)