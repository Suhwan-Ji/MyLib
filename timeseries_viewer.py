# import tkinter as tk
# from tkinter import ttk
import numpy as np
# #import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.gridspec as grid_spec
# from matplotlib.animation import FuncAnimation
from matplotlib.backend_bases import MouseButton
from func_util import *
from line_manager import *

mpl.rcParams['path.simplify'] = True
mpl.rcParams['path.simplify_threshold'] = 0.99
mpl.rcParams['agg.path.chunksize'] = 10000


class TimeSeriesViewer():
    def __init__(self, data=None, time_col='Time', main_col=None, predraw_col=None, draw_at_once=False):
        self.win = tk.Tk()
        self.win.title('TimeSeriesViewer_JSH')
        self.win.minsize(width=1400,height=900)
        #self.win.resizable(width=False,height=False)

        ###############################################################################################################
        # Init Attributes
        ###############################################################################################################
        if data is not None:
            self.data = data
            self.datalist = data.columns[1:]
        else:
            # Launch Data Reader
            print('Data 없이 런칭하기는 구현 안됨')
            self.win.destroy()
            return
        self.time_col = time_col

        ###############################################################################################################
        # Create Widgets
        ###############################################################################################################
        # Create Figure
        self.fig = plt.figure(figsize=(10, 8))
        self.fig.set_facecolor('grey')

        #figgrid = grid_spec.GridSpec(nrows=2,ncols=1,figure=self.fig)
        figgrid = self.fig.add_gridspec(2,1,height_ratios=[12,1],left=0.05,top=0.97,bottom=0.04)#,hspace=0)width_ratios=[5,1],
        self.pic_main_container = self.fig.add_subplot(figgrid[0])
        self.pic_main_container.tick_params(axis="x", labelbottom=False)
        self.pic_main_container.tick_params(axis="y", labelleft=False)
        maingrid = grid_spec.GridSpecFromSubplotSpec(2,1,figgrid[0],height_ratios=[8,1],hspace=0)

        self.pic_main = self.fig.add_subplot(maingrid[0])
        self.pic_main.tick_params(axis="x", labelbottom=False)
        self.pic_main.tick_params(axis="y", labelleft=False)
        self.pic_main.x_left = 0
        self.pic_main.x_right = 0
        self.pic_main.x_reference = 0
        self.pic_main.x_now = 0

        self.pic_boolean = self.fig.add_subplot(maingrid[1],sharex=self.pic_main,sharey=self.pic_main)
        self.pic_boolean.tick_params(axis="y", labelleft=False)
        self.pic_summary = self.fig.add_subplot(figgrid[1])
        self.pic_summary.x_left = 0
        self.pic_summary.x_right = 0
        self.pic_summary.x_now = 0

        # Create Data selector
        self.create_data_selector(self.win, [0, 1])

        # Create LineContainer
        self.line_container = LineContainer(self.win,[1, 1])
        #self.line_container.container.grid(row=1, column=1)

        # Create Canvas
        self.canvas = PlottingCanvas(self.win, self.fig, [0, 0])

        # Test
        self.button_test = tk.Button(self.win, text='Test',command=self._test)
        self.button_test.grid(row=2,column=2)

        ###############################################################################################################
        # Initialize
        ###############################################################################################################
        self._init_pic_main()
        self._init_pic_boolean()
        self._init_pic_summary(main_col)

        self._bind_canvas_events()
        self.update_pictures()

        self._initial_draw(predraw_col=predraw_col, draw_at_once=draw_at_once)

        #self.win.focus_set(True)
        self.win.mainloop()

    def _init_pic_main(self):
        self.pic_main.set_ylim(0, 10)
        self.pic_main.set_yticks([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        self.pic_main.set_facecolor('#03030f')
        self.pic_main.grid(True,color='grey', linestyle=':', linewidth=0.2)
        self.pic_main.start = tk.DoubleVar(value=0)
        self.pic_main.start_reference = tk.DoubleVar(value=0)
        self.pic_main.disp_step = tk.DoubleVar(value=30)
        # Vertical lines container
        self.pic_main.verticals = {'left': VerticalLine(self.pic_main.start.get(), self.pic_main, self.canvas.update,
                                                        linestyle='-',color='red'),
                                   'right': VerticalLine(self.pic_main.start.get() + self.pic_main.disp_step.get(),
                                                         self.pic_main, self.canvas.update,
                                                         linestyle=':',color='red')}
    def _init_pic_boolean(self):
        self.pic_boolean.set_ylim(0, 10)
        self.pic_boolean.set_yticks([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        self.pic_boolean.set_facecolor('#08080f')
        self.pic_boolean.grid(True,color='grey', linestyle=':', linewidth=0.2)
        self.pic_boolean.verticals = {'left': VerticalLine(self.pic_main.start.get(), self.pic_boolean, self.canvas.update,
                                                        linestyle='-',color='red'),
                                   'right': VerticalLine(self.pic_main.start.get() + self.pic_main.disp_step.get(),
                                                         self.pic_boolean, self.canvas.update,
                                                         linestyle=':',color='red')}

    def _init_pic_summary(self,main_col):
        if (main_col is None) or (main_col not in self.datalist):
            main_col = self.datalist[0]

        self.pic_summary.plot(self.data[self.time_col], self.data[main_col], color='forestgreen')
        # Vertical lines container
        self.pic_summary.verticals = {'left': VerticalLine(0, self.pic_summary, self.canvas.update, y=[-30000, 30000],
                                                           linestyle='-', color='darkblue'),
                                      'right': VerticalLine(0, self.pic_summary, self.canvas.update, y=[-30000, 30000],
                                                            linestyle=':', color='darkblue')}

    def _initial_draw(self, draw_at_once=False, predraw_col=None):
        if draw_at_once:
            for i, col in enumerate(self.datalist):
                self.add_col(self.pic_main, col)
        elif predraw_col is not None:
            if not isiter(predraw_col):
                dlist = [predraw_col]
            else:
                dlist = predraw_col
            for col in dlist:
                if col in self.datalist:
                    self.add_col(self.pic_main, col)

    def _bind_canvas_events(self):
        # motion_notify_event scroll_event button_press_event draw_event
        self.canvas.cbind('motion_notify_event', self._canvas_cb_move)
        self.canvas.cbind('button_press_event', self._canvas_cb_click)
        self.canvas.cbind('button_release_event', self._canvas_cb_release)
        self.canvas.cbind('scroll_event', self._canvas_cb_scroll)

    def _canvas_cb_move(self,event):
        pic = event.inaxes
        if (pic == self.pic_main) \
                or (pic == self.pic_boolean):
            pic = self.pic_main
            pic.x_now = event.xdata
            if event.button == MouseButton.LEFT:
                pic.x_left = pic.x_now
                self.line_container.update_selected(pic.x_left,action='left')
            elif event.button == MouseButton.RIGHT:
                pic.x_right = pic.x_now
                self.line_container.update_selected(pic.x_right, action='right')
            elif event.button == MouseButton.MIDDLE:
                deltax = pic.x_now - pic.x_reference
                start = self.pic_main.start_reference.get() - deltax
                self.pic_main.start_reference.set(self.pic_main.start_reference.get() - deltax)
                self.pic_main.start.set(start)
        elif pic == self.pic_summary:
            pic.x_now = event.xdata
            if event.button == MouseButton.LEFT:
                pic.x_left = self.pic_summary.x_now
                self.pic_main.start.set(pic.x_left)
        self.update_pictures()

    def _canvas_cb_click(self, event):
        pic = event.inaxes
        if (pic == self.pic_main) \
                or (pic == self.pic_boolean):
            pic = self.pic_main
            pic.x_now = event.xdata
            if event.button == MouseButton.LEFT:
                pic.x_left = pic.x_now
                self.line_container.update_selected(pic.x_left,action='left')
            elif event.button == MouseButton.RIGHT:
                pic.x_right = pic.x_now
                self.line_container.update_selected(pic.x_right, action='right')
            elif event.button == MouseButton.MIDDLE:
                pic.x_reference = pic.x_now  # 드래그 시작위치
                pic.start_reference.set(pic.start.get())

        elif event.inaxes == self.pic_summary:
            self.pic_summary.x_now = event.xdata
            if event.button == MouseButton.LEFT:
                pic.x_left = pic.x_now
                self.pic_main.start.set(pic.x_left)
        self.update_pictures()

    def _canvas_cb_release(self, event):
        # pic = event.inaxes
        # if (pic == self.pic_main) \
        #     or (pic == self.pic_boolean):
        #     pic = self.pic_main
        #     if event.button == MouseButton.MIDDLE:
        #         pic.x_now = event.xdata
        #         deltax = pic.x_now - pic.x_reference
        #         start = self.pic_main.start_reference.get() - deltax
        #         self.pic_main.start.set(start)
        # self.update_pictures()
        pass

    def _canvas_cb_scroll(self, event):
        tmp = self.pic_main.disp_step.get()
        if event.button == 'up':
            self.pic_main.disp_step.set(tmp*1.5)
        elif event.button == 'down':
            self.pic_main.disp_step.set(tmp / 1.5)
        self.update_pictures()

    def create_data_selector(self,master, grid_pos):
        container = ttk.LabelFrame(master, text='데이터 리스트')
        container.grid(row=grid_pos[0], column=grid_pos[1])

        choosers = ttk.LabelFrame(container, text='선택스')
        choosers.pack()

        dselected = tk.StringVar(value=self.datalist[0])
        ttk.Combobox(choosers, value=list(self.datalist), textvariable=dselected).grid(row=0, column=0, rowspan=2)
        ttk.Button(choosers, text='MainAdd',
                   command=lambda: self.add_col(self.pic_main, dselected.get())).grid(row=0, column=1)
        ttk.Button(choosers, text='BoolAdd',
                   command=lambda: self.add_col(self.pic_boolean, dselected.get())).grid(row=1, column=1)

    def update_pictures(self):
        self._update_main_picture()
        self._update_boolean_picture()
        self._update_summary_picture()

        self.canvas.update()

    def _update_main_picture(self):
        start = self.pic_main.start.get()
        end = start + self.pic_main.disp_step.get()
        self.pic_main.set_xlim(start, end)
        self.pic_main.set_xticklabels(list(map(time_format_plot,self.pic_main.get_xticks())),rotation=10)

        self.pic_main.verticals['left'].update_xdata(self.pic_main.x_left)
        self.pic_main.verticals['right'].update_xdata(self.pic_main.x_right)

    def _update_boolean_picture(self):
        self.pic_boolean.verticals['left'].update_xdata(self.pic_main.x_left)
        self.pic_boolean.verticals['right'].update_xdata(self.pic_main.x_right)

    def _update_summary_picture(self):
        self.pic_summary.verticals['left'].update_xdata(self.pic_main.start.get())
        self.pic_summary.verticals['right'].update_xdata(self.pic_main.start.get()
                                                         + self.pic_main.disp_step.get())

    def add_col(self, ax, col):
        self.line_container.add_linewidget(ax, self.data, col, self.canvas.update, time_col=self.time_col,\
                                           alpha=0.7, drawstyle='steps-post',linewidth=1.5)#marker='o',markersize=1,

    def _test(self):
        # print('Main Pic : ',self.pic_main.lines)
        # print('bool Pic : ',self.pic_boolean.lines)
        # print(self.line_container.list_linewidget['dat1'].axes)
        # self.pic_main.lines.remove(self.line_container.list_linewidget['dat1'])
        # self.line_container.list_linewidget['dat1']._axes = self.pic_boolean
        # self.pic_boolean.add_line(self.line_container.list_linewidget['dat1'])
        # self.line_container.list_linewidget['dat1']._update_line()
        # print('Action!')
        # print('Main Pic : ', self.pic_main.lines)
        # print('bool Pic : ', self.pic_boolean.lines)
        # print(self.line_container.list_linewidget['dat1'].axes)
        print(dir(self.line_container.list_linewidget['dat1']))
        self.line_container.list_linewidget['dat1'].set_fillstyle('bottom')

if __name__ == '__main__':
    import pandas as pd
    import numpy as np
    data = pd.DataFrame()
    dlen = 3000
    Ts = 0.1
    data['Time'] = np.arange(0, dlen * Ts, Ts)
    data['dat1'] = 2 * np.sin(2 * np.pi * 0.5 * data['Time']) + data['Time']
    data['dat2'] = 2 * np.sin(2 * np.pi * 0.5 * data['Time']) + 1 * np.cos(2 * np.pi * 3 * data['Time'])
    data['dat3'] = 0.3 * np.random.randn(dlen) + data['dat2']
    data['dat4'] = 0.2 * np.random.randn(dlen) + data['dat3']
    data['dat5'] = 0.1 * np.random.randn(dlen) + data['dat4']

    a = TimeSeriesViewer(data,main_col='dat1',predraw_col=['dat1','dat2'])#,draw_at_once=True)