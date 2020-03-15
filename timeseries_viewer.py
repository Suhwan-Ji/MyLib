import tkinter as tk
from tkinter import ttk
import numpy as np
#import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.backend_bases import MouseButton

from line_manager import *

def time_format(x):
    hour, rest = np.divmod(x, 3600)
    minute, rest = np.divmod(rest, 60)
    second, rest = np.divmod(rest, 60)
    return f"{hour}: {minute}: {second}.{rest}"


class TimeSeriesViewer():
    def __init__(self, data=None, time_col='time',main_col=None, draw_at_once=False):
        self.win = tk.Tk()
        self.win.title('TimeSeriesViewer_JSH')
        self.win.geometry('1400x900')
        self.win.resizable(width=False,height=False)

        ###############################################################################################################
        # Init Attributes
        ###############################################################################################################
        if data is not None:
            self.data = data
            self.datalist = data.columns[1:]
        else:
            # Data Reader
            pass
        self.time_col = time_col

        ###############################################################################################################
        # Create Widgets
        ###############################################################################################################

        # Create Data selector
        self.create_data_selector(self.win, [0, 1])

        # Create LineContainer
        self.line_container = LineContainer(self.win)
        self.line_container.container.grid(row=1, column=1)

        # Create Figure
        self.fig, ax = plt.subplots(2, 1, gridspec_kw={'height_ratios': [10, 1]}, figsize=(10, 6))
        self.fig.set_facecolor('grey')

        # Create Canvas
        self.canvas = PlottingCanvas(self.win, self.fig, [0, 0])

        ###############################################################################################################
        # Initialize
        ###############################################################################################################
        self.init_pic_main(ax[0])
        self.init_pic_summary(ax[1], main_col)

        self.bind_canvas_events()
        self.update_main_picture()

        self.win.mainloop()

    def init_pic_main(self,ax):
        self.pic_main = ax
        self.pic_main.set_ylim(0, 10)
        self.pic_main.set_yticks([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        self.pic_main.set_facecolor('grey')
        self.pic_main.grid(True)
        self.pic_main.start = tk.DoubleVar(value=0)
        self.pic_main.disp_step = tk.DoubleVar(value=300)
        self.pic_main.move_step = tk.DoubleVar(value=60)
        # Vertical lines container
        self.pic_main.verticals = {'left': VerticalLine(self.pic_main.start.get(), self.pic_main, self.canvas.update,
                                                        linestyle='-'),
                                   'right': VerticalLine(self.pic_main.start.get() + self.pic_main.disp_step.get(),
                                                         self.pic_main, self.canvas.update,
                                                         linestyle=':')}

    def init_pic_summary(self,ax,main_col):
        self.pic_summary = ax
        if main_col is not None \
                and main_col in self.datalist:
            self.pic_summary.plot(self.data[self.time_col], self.data[main_col])
        # Vertical lines container
        self.pic_summary.verticals = {'left': VerticalLine(0, self.pic_summary, self.canvas.update, y=[-30000,30000],
                                                           linestyle='-',color='green'),
                                      'right': VerticalLine(0, self.pic_summary, self.canvas.update, y=[-30000,30000],
                                                            linestyle=':',color='green')}

    def bind_canvas_events(self):
        # motion_notify_event scroll_event button_press_event draw_event
        self.canvas.cbind('motion_notify_event', self._canvas_cb_move)
        self.canvas.cbind('button_press_event', self._canvas_cb_click)
        self.canvas.cbind('scroll_event', self._canvas_cb_scroll)

    def _canvas_cb_move(self,event):
        x = event.xdata
        if event.inaxes == self.pic_main:
            if event.button == MouseButton.LEFT:
                self.pic_main.verticals['left'].update_xdata(x)
                self.line_container.update_all_ywhenx(x,action='left')
            elif event.button == MouseButton.RIGHT:
                self.pic_main.verticals['right'].update_xdata(x)
                self.line_container.update_all_ywhenx(x, action='right')
        elif event.inaxes == self.pic_summary:
            if event.button == MouseButton.LEFT:
                self.pic_summary.verticals['left'].update_xdata(x)
                self.pic_summary.verticals['right'].update_xdata(x+self.pic_main.disp_step.get())
                self.pic_main.start.set(event.xdata)
        self.update_main_picture()

    def _canvas_cb_click(self, event):
        x = event.xdata
        if event.inaxes == self.pic_main:
            if event.button == MouseButton.LEFT:
                self.pic_main.verticals['left'].update_xdata(x)
                self.line_container.update_all_ywhenx(x,action='left')
            elif event.button == MouseButton.RIGHT:
                self.pic_main.verticals['right'].update_xdata(x)
                self.line_container.update_all_ywhenx(x, action='right')
        elif event.inaxes == self.pic_summary:
            if event.button == MouseButton.LEFT:
                self.pic_summary.verticals['left'].update_xdata(x)
                self.pic_summary.verticals['right'].update_xdata(x + self.pic_main.disp_step.get())
                self.pic_main.start.set(x)
        self.update_main_picture()

    def _canvas_cb_scroll(self, event):
        if event.inaxes == self.pic_summary:
            tmp = self.pic_main.disp_step.get()
            if event.button == 'up':
                self.pic_main.disp_step.set(tmp*1.5)
            elif event.button == 'down':
                self.pic_main.disp_step.set(tmp / 1.5)
            tmp = self.pic_main.start.get()
            self.pic_summary.verticals['left'].update_xdata(tmp)
            self.pic_summary.verticals['right'].update_xdata(tmp + self.pic_main.disp_step.get())
        self.update_main_picture()


    def create_canvas(self, master, grid_pos):
        pass
        # container = ttk.LabelFrame(master, text='플로터')
        # container.grid(row=grid_pos[0], column=grid_pos[1],rowspan=2)
        #
        # self.canvas = FigureCanvasTkAgg(self.fig, master=container)
        # self.canvas.get_tk_widget().grid(row=0, column=0)
        #
        # time_widget = ttk.LabelFrame(container, text='시간축')
        # time_widget.grid(row=1, column=0)
        #
        # def move_pic(where=None):
        #     if where == 'left':
        #         tmpstep = -self.mp_mv_step.get()
        #     elif where == 'right':
        #         tmpstep = self.mp_mv_step.get()
        #     else:
        #         tmpstep = 0
        #     self.mp_start.set(self.mp_start.get() + tmpstep)
        #     self.update_main_picture()
        #
        # time_scale = ttk.LabelFrame(time_widget,text='scale')
        # time_scale.grid(row=0,column=0,columnspan=2)
        # ttk.Button(time_scale, text='<<', command=lambda: move_pic(where='left')).grid(row=0, column=0)
        # ttk.Button(time_scale, text='>>', command=lambda: move_pic(where='right')).grid(row=0, column=2)
        #
        # timemax = self.data[self.time_col][len(self.data) - 1]
        # ttk.Scale(time_scale, orient=tk.HORIZONTAL, length=400, variable=self.mp_start, from_=0.0, to=timemax).grid(
        #     row=0, column=1)
        #
        # time_setter = ttk.LabelFrame(time_widget,text='setter')
        # time_setter.grid(row=1,column=0)
        #
        #
        # def set_div_time():
        #     self.mp_disp_step.set(float(timestep.get()))
        #     self.update_main_picture()
        # timestep = tk.StringVar(value=self.mp_disp_step.get())
        # ttk.Entry(time_setter,textvariable=timestep).grid(row=0,column=0)
        # ttk.Button(time_setter, text='한칸당 초 update',command=set_div_time).grid(row=0,column=1)
        # def set_move_time():
        #     self.mp_mv_step.set(float(timestep_mv.get()))
        #     self.update_main_picture()
        #
        # timestep_mv = tk.StringVar(value=self.mp_mv_step.get())
        # ttk.Entry(time_setter,textvariable=timestep_mv).grid(row=1,column=0)
        # ttk.Button(time_setter, text='이동속도 update',command=set_move_time).grid(row=1,column=1)
        #
        # time_result = ttk.LabelFrame(time_widget,text='result')
        # time_result.grid(row=1,column=1)
        #
        # ttk.Label(time_result, text='한칸당(sec/div) : ').grid(row=1, column=0)
        # ttk.Label(time_result, textvariable=self.mp_disp_step).grid(row=1, column=1)
        # ttk.Label(time_result, text='이동속도(sec/click) : ').grid(row=2, column=0)
        # ttk.Label(time_result, textvariable=self.mp_mv_step).grid(row=2, column=1)
        #
        # tmp = lambda x: self.update_main_picture()
        # self.ani = FuncAnimation(self.fig, tmp, interval=2000)

    def create_data_selector(self,master, grid_pos):#,draw_at_once=False):
        container = ttk.LabelFrame(master, text='데이터 리스트')
        container.grid(row=grid_pos[0], column=grid_pos[1])

        choosers = ttk.LabelFrame(container, text='선택스')
        choosers.pack()

        dselected = tk.StringVar(value=self.datalist[0])
        ttk.Combobox(choosers, value=list(self.datalist), textvariable=dselected).grid(row=0, column=0)
        ttk.Button(choosers, text='Add',
                   command=lambda: self.add_col(self.pic_main, dselected.get())).grid(row=0, column=1)

        # if draw_at_once:
        #     for i, dat in enumerate(self.datalist):
        #         self.add_col(dat)

    def update_main_picture(self):
        start = self.pic_main.start.get()
        end = start + self.pic_main.disp_step.get()
        self.pic_main.set_xlim(start, end)
        self.canvas.update()

    def update_plot(self):
        pass
        # start = self.mp_start.get()
        # end = start + self.mp_disp_step.get()
        # self.main_pic.set_xlim(start, end)
        #
        # self.sub_vertical_lines['left'].update_xdata(start)
        # self.sub_vertical_lines['right'].update_xdata(end)
        #
        # self.canvas.draw()


    def add_col(self,ax,col, **kwargs):
        self.line_container.add_linewidget(ax, self.data, col, self.canvas.update, time_col=self.time_col, **kwargs)

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
    data['dat1'] = 2 * np.sin(2 * np.pi * 0.5 * data['time']) + data['time']
    data['dat2'] = 2 * np.sin(2 * np.pi * 0.5 * data['time']) + 1 * np.cos(2 * np.pi * 3 * data['time'])
    data['dat3'] = 0.3 * np.random.randn(dlen) + data['dat2']
    data['dat4'] = 0.2 * np.random.randn(dlen) + data['dat3']
    data['dat5'] = 0.1 * np.random.randn(dlen) + data['dat4']

    a = TimeSeriesViewer(data,main_col='dat1')