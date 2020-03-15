# import tkinter as tk
# from tkinter import ttk
# import numpy as np
# #import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
# from matplotlib.animation import FuncAnimation
from matplotlib.backend_bases import MouseButton
from func_util import *
from line_manager import *

mpl.rcParams['path.simplify'] = True
mpl.rcParams['path.simplify_threshold'] = 0.99
mpl.rcParams['agg.path.chunksize'] = 10000


class TimeSeriesViewer():
    def __init__(self, data=None, time_col='time', main_col=None, predraw_col=None, draw_at_once=False):
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
            # Launch Data Reader
            pass
        self.time_col = time_col

        ###############################################################################################################
        # Create Widgets
        ###############################################################################################################
        # Create Figure
        self.fig, ax = plt.subplots(2, 1, gridspec_kw={'height_ratios': [10, 1]}, figsize=(10, 6))
        self.fig.set_facecolor('grey')
        self.pic_main = ax[0]
        self.pic_summary = ax[1]

        # Create Data selector
        self.create_data_selector(self.win, [0, 1])

        # Create LineContainer
        self.line_container = LineContainer(self.win,[1, 1])
        #self.line_container.container.grid(row=1, column=1)

        # Create Canvas
        self.canvas = PlottingCanvas(self.win, self.fig, [0, 0])

        ###############################################################################################################
        # Initialize
        ###############################################################################################################
        self._init_pic_main()
        self._init_pic_summary(main_col)

        self._bind_canvas_events()
        self.update_main_picture()

        self._initial_draw(predraw_col=predraw_col, draw_at_once=draw_at_once)


        self.win.mainloop()

    def _init_pic_main(self):
        self.pic_main.set_ylim(0, 10)
        self.pic_main.set_yticks([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        self.pic_main.set_facecolor('grey')
        self.pic_main.grid(True)
        self.pic_main.start = tk.DoubleVar(value=0)
        self.pic_main.disp_step = tk.DoubleVar(value=30)
        self.pic_main.move_step = tk.DoubleVar(value=10)
        # Vertical lines container
        self.pic_main.verticals = {'left': VerticalLine(self.pic_main.start.get(), self.pic_main, self.canvas.update,
                                                        linestyle='-',color='darkblue'),
                                   'right': VerticalLine(self.pic_main.start.get() + self.pic_main.disp_step.get(),
                                                         self.pic_main, self.canvas.update,
                                                         linestyle=':',color='darkblue')}

    def _init_pic_summary(self,main_col):
        if (main_col is None) or (main_col not in self.datalist):
            main_col = self.datalist[0]

        self.pic_summary.plot(self.data[self.time_col], self.data[main_col], color='darkblue')
        # Vertical lines container
        self.pic_summary.verticals = {'left': VerticalLine(0, self.pic_summary, self.canvas.update, y=[-30000, 30000],
                                                           linestyle='-', color='green'),
                                      'right': VerticalLine(0, self.pic_summary, self.canvas.update, y=[-30000, 30000],
                                                            linestyle=':', color='green')}

    def _initial_draw(self, draw_at_once=False, predraw_col=None):
        if draw_at_once:
            for i, col in enumerate(self.datalist):
                self.add_col(self.pic_main, col)
        elif predraw_col is not None:
            print(predraw_col)
            if not isiter(predraw_col):
                print('not iter')
                dlist = [predraw_col]
            else:
                print('iter')
                dlist = predraw_col
            for col in dlist:
                print(col)
                if col in self.datalist:
                    print('add')
                    self.add_col(self.pic_main, col)

    def _bind_canvas_events(self):
        # motion_notify_event scroll_event button_press_event draw_event
        self.canvas.cbind('motion_notify_event', self._canvas_cb_move)
        self.canvas.cbind('button_press_event', self._canvas_cb_click)
        self.canvas.cbind('scroll_event', self._canvas_cb_scroll)

    def _canvas_cb_move(self,event):
        if event.inaxes == self.pic_main:
            x = event.xdata
            if event.button == MouseButton.LEFT:
                self.pic_main.verticals['left'].update_xdata(x)
                self.line_container.update_all_ywhenx(x,action='left')
            elif event.button == MouseButton.RIGHT:
                self.pic_main.verticals['right'].update_xdata(x)
                self.line_container.update_all_ywhenx(x, action='right')
        elif event.inaxes == self.pic_summary:
            x = event.xdata
            if event.button == MouseButton.LEFT:
                self.pic_summary.verticals['left'].update_xdata(x)
                self.pic_summary.verticals['right'].update_xdata(x+self.pic_main.disp_step.get())
                self.pic_main.start.set(event.xdata)
        self.update_main_picture()

    def _canvas_cb_click(self, event):
        if event.inaxes == self.pic_main:
            x = event.xdata
            if event.button == MouseButton.LEFT:
                self.pic_main.verticals['left'].update_xdata(x)
                self.line_container.update_all_ywhenx(x,action='left')
            elif event.button == MouseButton.RIGHT:
                self.pic_main.verticals['right'].update_xdata(x)
                self.line_container.update_all_ywhenx(x, action='right')
        elif event.inaxes == self.pic_summary:
            x = event.xdata
            if event.button == MouseButton.LEFT:
                self.pic_summary.verticals['left'].update_xdata(x)
                self.pic_summary.verticals['right'].update_xdata(x + self.pic_main.disp_step.get())
                self.pic_main.start.set(x)
        self.update_main_picture()

    def _canvas_cb_scroll(self, event):
        #if event.inaxes == self.pic_summary:
        tmp = self.pic_main.disp_step.get()
        if event.button == 'up':
            self.pic_main.disp_step.set(tmp*1.5)
        elif event.button == 'down':
            self.pic_main.disp_step.set(tmp / 1.5)
        tmp = self.pic_main.start.get()
        self.pic_summary.verticals['left'].update_xdata(tmp)
        self.pic_summary.verticals['right'].update_xdata(tmp + self.pic_main.disp_step.get())
        self.update_main_picture()

    def create_data_selector(self,master, grid_pos):
        container = ttk.LabelFrame(master, text='데이터 리스트')
        container.grid(row=grid_pos[0], column=grid_pos[1])

        choosers = ttk.LabelFrame(container, text='선택스')
        choosers.pack()

        dselected = tk.StringVar(value=self.datalist[0])
        ttk.Combobox(choosers, value=list(self.datalist), textvariable=dselected).grid(row=0, column=0)
        ttk.Button(choosers, text='Add',
                   command=lambda: self.add_col(self.pic_main, dselected.get())).grid(row=0, column=1)

    def update_main_picture(self):
        start = self.pic_main.start.get()
        end = start + self.pic_main.disp_step.get()
        self.pic_main.set_xlim(start, end)
        self.canvas.update()

    def add_col(self,ax,col):
        self.line_container.add_linewidget(ax, self.data, col, self.canvas.update, time_col=self.time_col,\
                                           alpha=0.5, drawstyle='steps-post')#marker='o',markersize=1,

if __name__ == '__main__':
    import pandas as pd
    import numpy as np
    data = pd.DataFrame()
    dlen = 3000
    Ts = 0.1
    data['time'] = np.arange(0, dlen * Ts, Ts)
    data['dat1'] = 2 * np.sin(2 * np.pi * 0.5 * data['time']) + data['time']
    data['dat2'] = 2 * np.sin(2 * np.pi * 0.5 * data['time']) + 1 * np.cos(2 * np.pi * 3 * data['time'])
    data['dat3'] = 0.3 * np.random.randn(dlen) + data['dat2']
    data['dat4'] = 0.2 * np.random.randn(dlen) + data['dat3']
    data['dat5'] = 0.1 * np.random.randn(dlen) + data['dat4']
    data['dat6'] = 0.1 * np.random.randn(dlen) + data['dat4']
    data['dat7'] = 0.1 * np.random.randn(dlen) + data['dat4']
    data['dat8'] = 0.1 * np.random.randn(dlen) + data['dat4']
    data['dat9'] = 0.1 * np.random.randn(dlen) + data['dat4']
    data['dat10'] = 0.1 * np.random.randn(dlen) + data['dat4']
    data['dat11'] = 0.1 * np.random.randn(dlen) + data['dat4']
    data['dat12'] = 0.1 * np.random.randn(dlen) + data['dat4']
    data['dat13'] = 0.1 * np.random.randn(dlen) + data['dat4']
    data['dat14'] = 0.1 * np.random.randn(dlen) + data['dat4']
    data['dat15'] = 0.1 * np.random.randn(dlen) + data['dat4']
    data['dat16'] = 0.1 * np.random.randn(dlen) + data['dat4']
    data['dat17'] = 0.1 * np.random.randn(dlen) + data['dat4']
    data['dat18'] = 0.1 * np.random.randn(dlen) + data['dat4']
    data['dat19'] = 0.1 * np.random.randn(dlen) + data['dat4']
    data['dat20'] = 0.1 * np.random.randn(dlen) + data['dat4']
    data['dat21'] = 0.1 * np.random.randn(dlen) + data['dat4']
    data['dat22'] = 0.1 * np.random.randn(dlen) + data['dat4']
    data['dat23'] = 0.1 * np.random.randn(dlen) + data['dat4']
    data['dat24'] = 0.1 * np.random.randn(dlen) + data['dat4']
    data['dat25'] = 0.1 * np.random.randn(dlen) + data['dat4']
    data['dat26'] = 0.1 * np.random.randn(dlen) + data['dat4']
    data['dat27'] = 0.1 * np.random.randn(dlen) + data['dat4']
    data['dat28'] = 0.1 * np.random.randn(dlen) + data['dat4']

    a = TimeSeriesViewer(data,main_col='dat1',predraw_col=['dat1','dat2'])#,draw_at_once=True)