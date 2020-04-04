import tkinter as tk
from tkinter import ttk
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.gridspec as grid_spec
from matplotlib.backend_bases import MouseButton

from line_manager import VerticalLine
from func_util import time_format_plot


class PlottingCanvas():
    def __init__(self, master,line_container, grid_pos):
        mpl.rcParams['path.simplify'] = True
        mpl.rcParams['path.simplify_threshold'] = 0.99
        mpl.rcParams['agg.path.chunksize'] = 10000

        # Create Figure
        self.fig = plt.figure(figsize=(14, 8))
        self.fig.set_facecolor('grey')

        container = ttk.LabelFrame(master, text='플로터')
        container.grid(row=grid_pos[0], column=grid_pos[1], rowspan=2)

        self.canvas = FigureCanvasTkAgg(self.fig, master=container)
        self.canvas.get_tk_widget().grid(row=0, column=0)

        figgrid = self.fig.add_gridspec(2,2,height_ratios=[12,1],width_ratios=[1,5],
                                        left=0.05,top=0.97, bottom=0.04, wspace=0.1)
        maingrid = grid_spec.GridSpecFromSubplotSpec(2, 1, figgrid[0, :], height_ratios=[8,1], hspace=0)

        self.line_container = line_container

        self.pic_main = self.fig.add_subplot(maingrid[0])
        self.pic_main.tick_params(axis="x", labelbottom=False)
        self.pic_main.tick_params(axis="y", labelleft=False)
        self.pic_main.x_left = 0
        self.pic_main.x_right = 0
        self.pic_main.x_reference = 0
        self.pic_main.x_now = 0

        self.pic_boolean = self.fig.add_subplot(maingrid[1],sharex=self.pic_main,sharey=self.pic_main)
        self.pic_boolean.tick_params(axis="y", labelleft=False)

        self.pic_summary = self.fig.add_subplot(figgrid[1,0])
        self.pic_summary.set_title('Summary')
        self.pic_summary.x_left = 0
        self.pic_summary.x_right = 0
        self.pic_summary.x_now = 0

        self.pic_analysis = self.fig.add_subplot(figgrid[1,1])
        self.pic_analysis.set_title('Analysis')

        self.init_pictures()

        self._bind_canvas_events()
        self.update_pictures()

    def init_pictures(self):
        self._init_pic_main()
        self._init_pic_boolean()
        self._init_pic_summary()

    def _init_pic_main(self):
        self.pic_main.set_ylim(0, 10)
        self.pic_main.set_yticks([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        self.pic_main.set_facecolor('#03030f')
        self.pic_main.grid(True,color='grey', linestyle=':', linewidth=0.2)
        self.pic_main.start = tk.DoubleVar(value=0)
        self.pic_main.start_reference = tk.DoubleVar(value=0)
        self.pic_main.disp_step = tk.DoubleVar(value=30)
        # Vertical lines container
        self.pic_main.verticals = {'left': VerticalLine(self.pic_main.start.get(), self.pic_main, self.update,
                                                        linestyle='-',color='red'),
                                   'right': VerticalLine(self.pic_main.start.get() + self.pic_main.disp_step.get(),
                                                         self.pic_main, self.update,
                                                         linestyle=':',color='red')}

    def _init_pic_boolean(self):
        self.pic_boolean.set_ylim(0, 10)
        self.pic_boolean.set_yticks([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        self.pic_boolean.set_facecolor('#08080f')
        self.pic_boolean.grid(True,color='grey', linestyle=':', linewidth=0.2)
        self.pic_boolean.verticals = {'left': VerticalLine(self.pic_main.start.get(), self.pic_boolean, self.canvas.draw_idle,
                                                        linestyle='-',color='red'),
                                   'right': VerticalLine(self.pic_main.start.get() + self.pic_main.disp_step.get(),
                                                         self.pic_boolean, self.canvas.draw_idle,
                                                         linestyle=':',color='red')}

    def _init_pic_summary(self):
        # Vertical lines container
        self.pic_summary.verticals = {'left': VerticalLine(0, self.pic_summary, self.update, y=[-30000, 30000],
                                                           linestyle='-', color='darkblue'),
                                      'right': VerticalLine(0, self.pic_summary, self.update, y=[-30000, 30000],
                                                            linestyle=':', color='darkblue')}
    def update_pictures(self):
        self._update_main_picture()
        self._update_boolean_picture()
        self._update_summary_picture()

        self.canvas.draw_idle()


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

    def update(self):
        self.canvas.draw_idle()

    def _bind_canvas_events(self):
        # motion_notify_event scroll_event button_press_event draw_event
        self.canvas.mpl_connect('motion_notify_event', self._canvas_cb_move)
        self.canvas.mpl_connect('button_press_event', self._canvas_cb_click)
        self.canvas.mpl_connect('button_release_event', self._canvas_cb_release)
        self.canvas.mpl_connect('scroll_event', self._canvas_cb_scroll)

    def _canvas_cb_move(self, event):
        pic = event.inaxes
        if (pic == self.pic_main) \
                or (pic == self.pic_boolean):
            pic = self.pic_main
            pic.x_now = event.xdata
            if event.button == MouseButton.LEFT:
                pic.x_left = pic.x_now
                self.line_container.update_selected(pic.x_left, action='left')
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
                self.line_container.update_selected(pic.x_left, action='left')
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
        pass

    def _canvas_cb_scroll(self, event):
        if (event.inaxes == self.pic_main) \
                or (event.inaxes == self.pic_boolean):  # main에서 스크롤시, 현재위치 기준으로 핀치
            tmp = self.pic_main.disp_step.get()
            xlen = self.pic_main.x_now - self.pic_main.start.get()
            if event.button == 'up':
                self.pic_main.disp_step.set(tmp * 1.5)
                self.pic_main.start.set(self.pic_main.x_now - xlen * 1.5)
            elif event.button == 'down':
                self.pic_main.disp_step.set(tmp / 1.5)
                self.pic_main.start.set(self.pic_main.x_now - xlen / 1.5)
        elif event.inaxes == self.pic_summary:  # summary에서 스크롤시, step만 변경
            tmp = self.pic_main.disp_step.get()
            if event.button == 'up':
                self.pic_main.disp_step.set(tmp * 1.5)
            elif event.button == 'down':
                self.pic_main.disp_step.set(tmp / 1.5)
        self.update_pictures()

    def __del__(self):
        print('PlottingCanvas has been deleted')
