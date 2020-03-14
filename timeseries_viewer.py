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


class TimeSeriesViewer(LineContainer):
    def __init__(self, data=None, time_col='time', draw_at_once=False):
        self.win = tk.Tk()
        self.win.title('TimeSeriesViewer_JSH')
        self.win.geometry('1400x900')
        self.win.resizable(width=False,height=False)#=False# config(resizable=False)

        if data is not None:
            self.data = data
            self.datalist = data.columns[1:]
        else:
            # Data Reader
            pass
        self.time_col = time_col

        self.line_container = LineContainer(self.win)
        self.line_container.container.grid(row=1, column=1)

        self.create_data_selector([0, 1])

        self.fig, ax = plt.subplots(2, 1, gridspec_kw={'height_ratios': [1, 5]}, figsize=(10, 6))

        self.main_pic = ax[1]
        self.main_pic.set_ylim(0, 10)
        self.main_pic.set_yticks([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        self.main_pic.grid(True)

        self.mp_start = tk.DoubleVar(value=0)
        self.mp_disp_step = tk.DoubleVar(value=300)
        self.mp_mv_step = tk.DoubleVar(value=60)

        self.create_canvas(self.win, [0, 0])

        self.update_main_picture()

        self.win.mainloop()

    def create_canvas(self, master, grid_pos):
        container = ttk.LabelFrame(master, text='플로터')
        container.grid(row=grid_pos[0], column=grid_pos[1],rowspan=2)

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

        time_scale = ttk.LabelFrame(time_widget,text='scale')
        time_scale.grid(row=0,column=0,columnspan=2)
        ttk.Button(time_scale, text='<<', command=lambda: move_pic(where='left')).grid(row=0, column=0)
        ttk.Button(time_scale, text='>>', command=lambda: move_pic(where='right')).grid(row=0, column=2)

        timemax = self.data[self.time_col][len(self.data) - 1]
        ttk.Scale(time_scale, orient=tk.HORIZONTAL, length=400, variable=self.mp_start, from_=0.0, to=timemax).grid(
            row=0, column=1)

        time_setter = ttk.LabelFrame(time_widget,text='setter')
        time_setter.grid(row=1,column=0)


        def set_div_time():
            self.mp_disp_step.set(float(timestep.get()))
            self.update_main_picture()
        timestep = tk.StringVar()
        ttk.Entry(time_setter,textvariable=timestep).grid(row=0,column=0)
        ttk.Button(time_setter, text='한칸당 초 update',command=set_div_time).grid(row=0,column=1)
        def set_move_time():
            self.mp_mv_step.set(float(timestep_mv.get()))
            self.update_main_picture()

        timestep_mv = tk.StringVar()
        ttk.Entry(time_setter,textvariable=timestep_mv).grid(row=1,column=0)
        ttk.Button(time_setter, text='이동속도 update',command=set_move_time).grid(row=1,column=1)

        time_result = ttk.LabelFrame(time_widget,text='result')
        time_result.grid(row=1,column=1)

        ttk.Label(time_result, text='한칸당(sec/div) : ').grid(row=1, column=0)
        ttk.Label(time_result, textvariable=self.mp_disp_step).grid(row=1, column=1)
        ttk.Label(time_result, text='이동속도(sec/click) : ').grid(row=2, column=0)
        ttk.Label(time_result, textvariable=self.mp_mv_step).grid(row=2, column=1)

        tmp = lambda x: self.update_main_picture()
        self.ani = FuncAnimation(self.fig, tmp, interval=2000)

    def create_data_selector(self,grid_pos):#,draw_at_once=False):
        container = ttk.LabelFrame(self.win, text='데이터 리스트')
        container.grid(row=grid_pos[0], column=grid_pos[1])

        choosers = ttk.LabelFrame(container, text='선택스')
        choosers.pack()

        dselected = tk.StringVar(value=self.datalist[0])
        ttk.Combobox(choosers, value=list(self.datalist), textvariable=dselected).grid(row=0, column=0)
        ttk.Button(choosers, text='Add',
                   command=lambda: self.add_col(dselected.get())).grid(row=0, column=1)

        # if draw_at_once:
        #     for i, dat in enumerate(self.datalist):
        #         self.add_col(dat)

    def update_main_picture(self):
        start = self.mp_start.get()
        end = start + self.mp_disp_step.get()
        self.main_pic.set_xlim(start, end)
        self.canvas.draw()

    def add_col(self,col,**kwargs):
        tmpline = self.line_container.add_linewidget(self.data, col, self.canvas.draw, time_col=self.time_col, **kwargs)
        if tmpline is not None:
            self.main_pic.add_line(tmpline)
        self.canvas.draw()

    def _remove_line(self, col):
        pass
        # if col in self.line_statemanager.keys():
        #     self.line_statemanager[col].destroy()
        #     del self.line_statemanager[col]
        #
        # if col in self.linelist.keys():
        #     self.linelist[col].destroy()
        #     del self.linelist[col]
        # self.canvas.draw()

if __name__ == '__main__':
    import pandas as pd
    import numpy as np
    data = pd.DataFrame()
    dlen = 30000
    Ts = 0.1
    data['time'] = np.arange(0, dlen * Ts, Ts)
    data['dat1'] = 3 * np.sin(2 * np.pi * 0.5 * data['time']) + 1 * np.cos(2 * np.pi * 3 * data['time'])
    data['dat2'] = 1 * np.random.randn(dlen) + data['dat1']

    a = TimeSeriesViewer(data)