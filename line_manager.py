from func_util import LimitedList
import matplotlib.lines
import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
import numpy as np

def time_format(x):
    hour, rest = np.divmod(x, 3600)
    minute, second = np.divmod(rest, 60)
    # second, rest = np.divmod(rest, 100)
    return f"{int(hour)}시간 {int(minute)}분\n{second:.3f}초"

def time_format_plot(x):
    hour, rest = np.divmod(x, 3600)
    minute, rest = np.divmod(rest, 60)
    second = rest // 1
    rest = rest % 1 * 1000
    return f"{int(hour):02d}:{int(minute):02d}:{int(second):02d}:{int(rest):02d}"


class LineManager(matplotlib.lines.Line2D):
    def __init__(self, x, y, func_line_update, offset=0, gain=1, position=0, scale=1, **kwargs):
        matplotlib.lines.Line2D.__init__(self, x, y, **kwargs)

        self.func_line_update = func_line_update
        self.raw_ydata = self.get_ydata()
        self.modified_ydata = self.raw_ydata
        self.offset = offset
        self.gain = gain
        self.position = position
        self.scale = scale

        self.x_selected_left = 0
        self.x_selected_right = 0

        self._update_line()

    def get_value_whenx(self,x,which='raw'):
        index = np.argmin(np.array(self.get_xdata()) < x) - 1
        try:
            if which == 'modified':
                return self.modified_ydata[index]
            else:
                return self.raw_ydata[index]
        except:
            return 0

    #     print(get_data_selected(which))
    #
    # def get_data_selected(self,which='raw'):
    #     start = np.minimum(self.x_selected_left,self.x_selected_right)
    #     end = np.maximum(self.x_selected_left, self.x_selected_right)
    #     index_start = np.argmin(np.array(self.get_xdata()) < start) - 1
    #     index_end = np.argmin(np.array(self.get_xdata()) < end) - 1
    #     if which == 'modified':
    #         return self.modified_ydata[index_start:index_end]
    #     else:
    #         return self.raw_ydata[index_start:index_end]

    def _update_modified_line(self):
        # 유저가 세팅한 값 계산
        self.modified_ydata = self.raw_ydata * self.gain + self.offset

    def _update_visual_line(self):
        # 플로팅될 값 계산
        tmpdata = self.modified_ydata / self.scale + self.position
        self.set_ydata(tmpdata)

    def _update_line(self):
        # 계산값 우선적용
        self._update_modified_line()
        # Scale, Pos적용
        self._update_visual_line()
        self.func_line_update()

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
        self.func_line_update()

    # def set_style(self,**kwargs):
    #     if 'drawstyle' in kwargs:
    #         self.set_drawstyle(kwargs['drawstyle'])
    #     if 'color' in kwargs:
    #         self.set_color(kwargs['color'])
    #

class LineWidget(LineManager):
    init_data = pd.DataFrame()
    init_data['time'] = np.arange(300)
    init_data['var'] = np.random.randn(300)

    # init_list_poition = [x * 0.1 for x in range(100)]
    init_list_scale = [0.1, 0.2, 0.5, 1, 5, 10, 20, 50, 100, 200, 500, 1000, 2000, 10000]

    def __init__(self, master, func_line_update, func_destroy, data_col='var', time_col='time', data=None, **kwargs):
        if data is None:
            data = LineWidget.init_data
        LineManager.__init__(self, data[time_col], data[data_col], func_line_update, **kwargs)

        self.data_name = data_col
        self.list_scale = LineWidget.init_list_scale

        self.func_destroy = lambda:func_destroy(self.data_name)

        self.manager = tk.LabelFrame(master, text=self.data_name)#, labelanchor='w')
        self.manager.pack()

        def _button_show_callback():
            self.toggle_line()
            if self.get_visible():
                self.button_show.config(background=self.get_color())
            else:
                self.button_show.config(background='grey')

        self.button_show = tk.Button(self.manager, text='show', width=6, bg=self.get_color())
        self.button_show.config(command=_button_show_callback)
        self.button_show.grid(row=0, column=0)


        def _button_apply_callback():
            if self.entry1.instate(['readonly']):
                self.entry1.state(['!readonly'])
                self.entry2.state(['!readonly'])
                self.button_apply.config(text='apply >')
            elif self.entry1.instate(['!readonly']):
                self.entry1.state(['readonly'])
                self.entry2.state(['readonly'])
                self.set_lm_value('gain',float(self.entry1.get()))
                self.set_lm_value('offset', float(self.entry2.get()))
                self.button_apply.config(text='modify >')

        self.button_apply = tk.Button(self.manager, text='modify >', width=6)
        self.button_apply.config(command=_button_apply_callback)
        self.button_apply.grid(row=1, column=0)

        def _update_lineitem(item,spinbox):
            tmp = float(spinbox.get())
            self.set_lm_value(item,tmp)

        self.frame_position = tk.LabelFrame(self.manager, text='Position')
        self.frame_position.grid(row=0, column=2)
        self.spin1 = ttk.Spinbox(self.frame_position, from_=0, to=10.0,increment=0.2, width=5, state='readonly')
        self.spin1.config(command=lambda: _update_lineitem('position', self.spin1))
        self.spin1.grid(row=0, column=0)
        self.spin1.set(self.get_lm_value('position'))

        self.frame_gain = tk.LabelFrame(self.manager, text='(* gain)')
        self.frame_gain.grid(row=1, column=2)

        self.entry1 = ttk.Entry(self.frame_gain, width=5)
        self.entry1.grid(row=0, column=0)
        self.entry1.insert(0,string=str(self.get_lm_value('gain')))
        self.entry1.state(['readonly'])

        self.frame_scale = tk.LabelFrame(self.manager, text='한칸당')
        self.frame_scale.grid(row=0, column=3)
        self.spin2 = ttk.Spinbox(self.frame_scale, values=self.list_scale, width=5, state='readonly')
        self.spin2.config(command=lambda: _update_lineitem('scale', self.spin2))
        self.spin2.grid(row=0, column=0)
        self.spin2.set(self.get_lm_value('scale'))

        self.frame_offset = tk.LabelFrame(self.manager, text='(+ offset)')
        self.frame_offset.grid(row=1, column=3)

        self.entry2 = ttk.Entry(self.frame_offset, width=5)
        self.entry2.grid(row=0, column=0)
        self.entry2.insert(0, string=str(self.get_lm_value('offset')))
        self.entry2.state(['readonly'])

        self.display_frame = ttk.LabelFrame(self.manager)
        self.display_frame.grid(row=0,column=4, rowspan=2,sticky=tk.N+tk.S)
        # self.current_yvalue = tk.StringVar(value="cur : ")
        # tk.Label(self.display_frame,textvariable=self.current_yvalue,
        #          width=15, anchor='w').grid(row=0,column=0)
        self.left_yvalue = tk.StringVar(value="left : ")
        tk.Label(self.display_frame, textvariable=self.left_yvalue,
                 width=12, anchor='w').grid(row=0, column=0,sticky=tk.W) # justify=tk.LEFT
        self.right_yvalue = tk.StringVar(value="right : ")
        tk.Label(self.display_frame, textvariable=self.right_yvalue,
                 width=12, anchor='w').grid(row=1, column=0,sticky=tk.W)

        ttk.Button(self.manager, text='del',command=self.func_destroy,width=3).grid(row=0,column=5)

    def update_selected_x(self,x,action=None):
        if action=='left':
            self.left_yvalue.set(f'left : {self.get_value_whenx(x,which="modified"):.3f}')
            self.x_selected_left = x
        elif action=='right':
            self.right_yvalue.set(f'right : {self.get_value_whenx(x,which="modified"):.3f}')
            self.x_selected_right = x
        # else:
        #     self.current_yvalue.set(f'cur : {self.get_rawy_whenx(x):.3f}')

    def remove_self(self):
        pass
        # self.remove()
        # self.manager.destroy()

    def __del__(self):
        print(f'{self.data_name} has been deleted')

    def link_line(self, ax):
        self.linemanager.link_line(ax)


class LineContainer():
    list_color = [
        '#ff3333',
        '#ff7632',
        '#ffba32',
        '#aaff00',
        '#55fe32',
        '#33dcfe',
        '#7732fe',
        '#ff32fe',
        '#990066',
        '#660022',
    ]
    def __init__(self, master,grid_pos):
        self.list_linewidget = {}
        self.container = tk.LabelFrame(master, text='Lines', bd=2)
        self.container.grid(row=grid_pos[0], column=grid_pos[1])

        self.time_container = tk.LabelFrame(self.container, text='Times', bd=2)
        self.time_container.grid(row=0)
        self._add_timeindicator(self.time_container)

        self.widget_container = tk.LabelFrame(self.container, text='Widgets', bd=2)
        self.widget_container.grid(row=1,columnspan=3)

        self.canvas = tk.Canvas(self.widget_container, width=300, height=600)
        self.bar = tk.Scrollbar(self.widget_container)
        self.bar["command"] = self.canvas.yview
        self.bar_H = tk.Scrollbar(self.widget_container,orient=tk.HORIZONTAL)
        self.bar_H["command"] = self.canvas.xview

        self.canvas.grid(row=0,column=0)#pack(side='left')  # fill='both', expand=True, side='left')
        self.bar.grid(row=0,column=1,sticky=tk.N+tk.S)#.pack(fill='y', side='right')
        self.bar_H.grid(row=1,column=0,columnspan=2,sticky=tk.W+tk.E)#pack(fill='y', side='bottom')

        self.dframe = tk.Frame(self.canvas)

        self.canvas.create_window(0, 0, window=self.dframe)
        self._update_widget()

    def _add_timeindicator(self,master):
        self.time_selected_left = tk.StringVar(value='Start : \n\n')
        self.time_selected_right = tk.StringVar(value='End : \n\n')
        self.time_selected_delta = tk.StringVar(value='Delata : \n\n')
        ttk.Label(master,textvariable=self.time_selected_left,
                  width=12, anchor='w').grid(row=0, column=0)
        ttk.Label(master, textvariable=self.time_selected_right,
                  width=12, anchor='w').grid(row=0, column=1)
        ttk.Label(master, textvariable=self.time_selected_delta,
                  width=12, anchor='w').grid(row=0, column=2)

    def add_linewidget(self, ax, data, data_name, func_line_update, time_col='time', **kwargs):
        if data_name not in self.list_linewidget.keys():
            tmplen = len(LineContainer.list_color)
            orderlen = len(self.list_linewidget)%tmplen
            color = LineContainer.list_color[orderlen]

            tmp = LineWidget(self.dframe, func_line_update, self.remove_linewidget,
                             data_col=data_name, time_col=time_col, data=data,
                             color=color,**kwargs)

            self.list_linewidget[data_name] = tmp
            ax.add_line(tmp)
            self._update_widget()
            func_line_update()

    def remove_linewidget(self,col):
        if col in self.list_linewidget.keys():
            self.list_linewidget[col].remove()
            self.list_linewidget[col].manager.destroy()
            del self.list_linewidget[col]
        self._update_widget()
        #print(self.list_linewidget)

    def _update_widget(self):
        self.canvas.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox('all'),
                              yscrollcommand=self.bar.set,
                              xscrollcommand=self.bar_H.set)

    def update_selected(self,x,action=None):
        for line in self.list_linewidget.values():
            line.update_selected_x(x,action=action)
        if len(self.list_linewidget) > 0:
            self.time_selected_left.set(f'Start : \n{time_format(line.x_selected_left)}')
            self.time_selected_right.set(f'End : \n{time_format(line.x_selected_right)}')
            tmp = abs(line.x_selected_right - line.x_selected_left)
            self.time_selected_delta.set(f'Delata : \n{time_format(tmp)}')

    def __del__(self):
        print('LineContainer has been deleted')


class VerticalLine(matplotlib.lines.Line2D):
    def __init__(self, x, ax, func_line_update,y=[-1,11], **kwargs):
        matplotlib.lines.Line2D.__init__(self, [x,x], y, **kwargs)
        ax.add_line(self)
        self.func_line_update = func_line_update
        #self.func_line_update()

    def update_xdata(self,x):
        self.set_xdata([x,x])
        #self.func_line_update()

    def __del__(self):
        print('VerticalLine has been deleted')


class PlottingCanvas():
    def __init__(self,master,fig, grid_pos):
        container = ttk.LabelFrame(master, text='플로터')
        container.grid(row=grid_pos[0], column=grid_pos[1], rowspan=2)

        self.canvas = FigureCanvasTkAgg(fig, master=container)
        self.canvas.get_tk_widget().grid(row=0, column=0)

    def update(self):
        self.canvas.draw_idle()

    def cbind(self, id, func):
        self.canvas.mpl_connect(id, func)

    def __del__(self):
        print('PlottingCanvas has been deleted')
