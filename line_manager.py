from func_util import LimitedList
#import matplotlib
import matplotlib.lines
import tkinter as tk
from tkinter import ttk


class LineManager(matplotlib.lines.Line2D):
    def __init__(self, x, y, scalelist=[1], poslist=[0], init_scale=1, init_position=5, offset=0, gain=1, **kwargs):
        matplotlib.lines.Line2D.__init__(self, x, y, **kwargs)

        self.yscalelist = LimitedList(scalelist, init_scale)
        self.yposlist = LimitedList(poslist, init_position)
        self.raw_ydata = self.get_ydata()
        self.offset = offset
        self.gain = gain

        self._update_line()

    def _update_line(self):
        # 계산값 우선적용
        tmpdata = self.raw_ydata * self.gain + self.offset
        # Scale, Pos적용
        tmpdata = tmpdata * self.yscalelist.get_now() + self.yposlist.get_now()
        self.set_ydata(tmpdata)

    def change_state(self, item, method=None, step=1):
        if item == 'position':
            tmplist = self.yposlist
        elif item == 'scale':
            tmplist = self.yscalelist

        if method == '+':
            tmplist._next(step)
        elif method == '-':
            tmplist._before(step)
        self._update_line()

    def set_value(self, item, value):
        if item == 'gain':
            self.gain = value
        elif item == 'offset':
            self.offset = value
        self._update_line()

    def toggle_line(self):
        tmp = self.get_visible()
        self.set_visible(not tmp)
    def link_line(self,ax):
        ax.add_line(self)
    def set_style(self):
        pass

    def destroy(self):
        self.remove()
        pass


class LineWidget(LineManager):
    def __init__(self, master, data_col='var', time_col='time', data=None, **kwargs):
        self.data_name = data_col
        self.linemanager = LineManager(data[time_col], data[data_col], **kwargs)

        self.manager = tk.LabelFrame(master, text=self.data_name)
        self.manager.pack()

        self.button_show = ttk.Button(self.manager, text='show', width=5)
        self.button_show.config(command=self.linemanager.toggle_line)
        self.button_show.grid(row=0, column=0)

        def _update_lineitem(spinbox):
            tmp = float(spinbox.get())
            spinbox.lm.set_value(tmp)

        self.frame_position = tk.LabelFrame(self.manager, text='Position')
        self.frame_position.grid(row=0, column=2)

        tmplm = self.linemanager.yposlist
        tmpdat = [str(a) for a in tmplm.dlist]
        self.spin1 = ttk.Spinbox(self.frame_position, width=5, state='readonly')
        self.spin1.config(command=lambda: _update_lineitem(self.spin1))
        self.spin1.config(values=tmpdat)  # tmplist.dlist)
        self.spin1.lm = tmplm
        self.spin1.grid(row=0, column=0)
        self.spin1.set(tmplm.get_now())

        self.frame_scale = tk.LabelFrame(self.manager, text='Scale')
        self.frame_scale.grid(row=0, column=3)

        tmplm = self.linemanager.yscalelist
        tmpdat = [str(a) for a in tmplm.dlist]
        self.spin2 = ttk.Spinbox(self.frame_scale, width=5, state='readonly')
        self.spin2.config(command=lambda: _update_lineitem(self.spin2))
        self.spin2.config(values=tmpdat)
        self.spin2.lm = tmplm
        self.spin2.grid(row=0, column=0)
        self.spin2.set(tmplm.get_now())
    def link_line(self,ax):
        self.linemanager.link_line(ax)


class LineContainer():
    def __init__(self, master):
        self.lw_list = []
        self.container = tk.LabelFrame(master, text='Lines', bd=2)
        self.container.pack()
        self.canvas = tk.Canvas(self.container, width=200, height=400)
        self.bar = tk.Scrollbar(self.container)
        self.bar["command"] = self.canvas.yview
        self.canvas.pack(side='left')  # fill='both', expand=True, side='left')
        self.bar.pack(fill='y', side='right')

        self.dframe = tk.Frame(self.canvas)

        self.canvas.create_window(0, 0, window=self.dframe)
        self.canvas.update_idletasks()

        self.canvas.configure(scrollregion=self.canvas.bbox('all'),
                              yscrollcommand=self.bar.set)

    def add_lw(self, data, data_name,ax,**kwargs):
        tmp = LineWidget(self.dframe, data_col=data_name, time_col='time', data=data,**kwargs)
        self.lw_list.append(tmp)
        tmp.link_line(ax)

        self.canvas.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox('all'),
                              yscrollcommand=self.bar.set)
    def link_line(self,ax):
        pass