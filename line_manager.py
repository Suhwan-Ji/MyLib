from func_util import LimitedList
#import matplotlib
import matplotlib.lines
import tkinter as tk
from tkinter import ttk
import pandas as pd
import numpy as np


class LineManager(matplotlib.lines.Line2D):
    def __init__(self, x, y, offset=0, gain=1, position=5, scale=1, **kwargs):
        matplotlib.lines.Line2D.__init__(self, x, y, **kwargs)

        self.raw_ydata = self.get_ydata()
        self.modified_ydata = None
        self.offset = offset
        self.gain = gain
        self.position = position
        self.scale = scale

        self._update_line()

    def _update_modified_line(self):
        # 유저가 세팅한 값 계산
        self.modified_ydata = self.raw_ydata * self.gain + self.offset

    def _update_visual_line(self):
        # 플로팅될 값 계산
        tmpdata = self.modified_ydata * self.scale + self.position
        self.set_ydata(tmpdata)

    def _update_line(self):
        # 계산값 우선적용
        self._update_modified_line()
        # Scale, Pos적용
        self._update_visual_line()

    def set_lm_value(self, item, value):
        if item == 'gain':
            self.gain = value
        elif item == 'offset':
            self.offset = value
        elif item == 'position':
            self.position = value
        elif item == 'scale':
            self.scale = value
        self._update_line()

    def get_lm_value(self, item):
        tmp = 0
        if item == 'gain':
            tmp = self.gain
        elif item == 'offset':
            tmp = self.offset
        elif item == 'position':
            tmp = self.position
        elif item == 'scale':
            tmp = self.scale
        return tmp

    def toggle_line(self):
        tmp = self.get_visible()
        self.set_visible(not tmp)

    def set_style(self):
        pass

    def destroy(self):
        self.remove()
        pass


class LineWidget(LineManager):
    init_data = pd.DataFrame()
    init_data['time'] = np.arange(300)
    init_data['var'] = np.random.randn(300)

    init_list_poition = [x * 0.1 for x in range(100)]
    init_list_scale = [10 ** x for x in np.arange(-2, 3, 1, dtype=float)]

    def __init__(self, master, func_line_update, data_col='var', time_col='time', data=None, **kwargs):
        if data is None:
            data = LineWidget.init_data
        LineManager.__init__(self, data[time_col], data[data_col], **kwargs)

        self.data_name = data_col
        self.func_line_update = func_line_update
        self.list_position = LineWidget.init_list_poition
        self.list_scale = LineWidget.init_list_scale

        self.manager = tk.LabelFrame(master, text=self.data_name)
        self.manager.pack()

        self.button_show = ttk.Button(self.manager, text='show', width=5)
        self.button_show.config(command=self.toggle_line)
        self.button_show.grid(row=0, column=0)

        def _update_lineitem(item,spinbox):
            tmp = float(spinbox.get())
            self.set_lm_value(item,tmp)
            self.func_line_update()
            print('{0} is now : {1}'.format(item, self.get_lm_value(item)))

        self.frame_position = tk.LabelFrame(self.manager, text='Position')
        self.frame_position.grid(row=0, column=2)
        self.spin1 = ttk.Spinbox(self.frame_position, values=self.list_position, width=5, state='readonly')
        self.spin1.config(values=self.list_position)
        self.spin1.config(command=lambda: _update_lineitem('position', self.spin1))
        self.spin1.grid(row=0, column=0)
        self.spin1.set(self.get_lm_value('position'))

        self.frame_scale = tk.LabelFrame(self.manager, text='Scale')
        self.frame_scale.grid(row=0, column=3)
        self.spin2 = ttk.Spinbox(self.frame_scale, values=self.list_scale, width=5, state='readonly')
        # self.spin2.config(values = [str(x) for x in self.list_scale])
        self.spin2.config(command=lambda: _update_lineitem('scale', self.spin2))
        self.spin2.grid(row=0, column=0)
        self.spin2.set(self.get_lm_value('scale'))

    def remove_self(self):
        pass
        # self.remove()
        # self.manager.destroy()

    def __del__(self):
        print(f'{self.data_name} is been deleted')

    def link_line(self, ax):
        self.linemanager.link_line(ax)


class LineContainer():
    def __init__(self, master):
        self.list_linewidget = {}
        self.container = tk.LabelFrame(master, text='Lines', bd=2)
        self.container.pack()
        self.canvas = tk.Canvas(self.container, width=400, height=800)
        self.bar = tk.Scrollbar(self.container)
        self.bar["command"] = self.canvas.yview
        self.canvas.pack(side='left')  # fill='both', expand=True, side='left')
        self.bar.pack(fill='y', side='right')

        self.dframe = tk.Frame(self.canvas)

        self.canvas.create_window(0, 0, window=self.dframe)
        self._update_widget()

    def add_linewidget(self, data, data_name, func_line_update, time_col='time', **kwargs):
        if data_name not in self.list_linewidget.keys():
            tmp = LineWidget(self.dframe, func_line_update, data_col=data_name, time_col=time_col, data=data, **kwargs)
            # delbutton = ttk.Button(self.dframe,text='del',command=lambda:self.remove_linewidget(data_name),width=5)
            # delbutton.grid(row=0,column=1)
            # tmp = {'linewidget':tmp, 'delbutton':delbutton}

            self.list_linewidget[data_name] = tmp
            self._update_widget()
            print(self.list_linewidget)
            return tmp

        return None

    def remove_linewidget(self,col):
        self.list_linewidget[col]['linewidget'].remove_self()
        self.list_linewidget[col]['delbutton'].destroy()
        del self.list_linewidget[col]
        #self._update_widget()
        #print(self.list_linewidget)


    def _update_widget(self):
        self.canvas.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox('all'),
                              yscrollcommand=self.bar.set)

    # def remove_linewidget(self,data_name):
    #     del self.list_linewidget[data_name]

    def link_line(self, ax):
        pass
