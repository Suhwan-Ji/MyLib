#from func_util import LimitedList
import matplotlib.lines
import tkinter as tk
from tkinter import ttk
import pandas as pd
import numpy as np
from func_util import time_format_plot

def time_format(x):
    hour, rest = np.divmod(x, 3600)
    minute, second = np.divmod(rest, 60)
    # second, rest = np.divmod(rest, 100)
    return f"{int(hour)}시간 {int(minute)}분\n{second:.3f}초"


class LineManager(matplotlib.lines.Line2D):
    def __init__(self, x, y, func_line_update, offset=0, gain=1, position=0, scale=1, **kwargs):
        matplotlib.lines.Line2D.__init__(self, x, y, **kwargs)

        self.func_line_update = func_line_update
        self.raw_ydata = self.get_ydata()
        self.offset = offset
        self.gain = gain
        self.position = position
        self.scale = scale

        self._update_line()

    def get_value_whenx(self, x, which='raw'):
        index = self._find_closest_index(x)
        if which == 'modified':
            return self._calc_modified_ydata(self.raw_ydata[index])
        elif which == 'drawing':
            return self.get_ydata()[index]
        else:
            return self.raw_ydata[index]

    def _find_closest_index(self, x):
        # 주어진 x에 가장 가까운 데이터 인덱스를 리턴
        xdata = np.array(self.get_xdata())
        if x >= xdata[-1]:
            index = len(xdata) - 1
        elif x < xdata[0]:
            index = 0
        else:
            index = np.argmin(xdata < x) - 1
            if index < 0:
                index = 0
        return index

    def _calc_modified_ydata(self, y):
        return y * self.gain + self.offset # 값 하나에 대해 Modified Data 얻기

    def get_modified_ydata(self):
        # Returns Modified Line
        return self.raw_ydata * self.gain + self.offset  # 유저가 세팅한 값 계산

    def _update_line(self):
        tmp = self.get_modified_ydata()  # 계산값 우선적용
        tmp = tmp / self.scale + self.position  # Scale, Pos적용
        self.set_ydata(tmp)
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


class LineWidget(LineManager):
    init_data = pd.DataFrame()
    init_data['time'] = np.arange(300)
    init_data['var'] = np.random.randn(300)

    # init_list_poition = [x * 0.1 for x in range(100)]
    init_list_scale = [0.1, 0.2, 0.5, 1, 2, 5, 10, 20, 50, 100, 200, 500, 1000, 2000, 10000]

    def __init__(self, master, ax, func_line_update, func_destroy, data_col='var', time_col='time', data=None, **kwargs):
        if data is None:
            data = LineWidget.init_data
        LineManager.__init__(self, data[time_col], data[data_col], func_line_update, **kwargs)

        # Data Auto Scaling
        data_max = np.max(self.get_modified_ydata())
        data_min = np.min(self.get_modified_ydata())
        data_range = data_max - data_min
        if data_range > 1.1: # Flag 데이터는 Scale 하지않음
            index_scale = np.argmax(np.array(LineWidget.init_list_scale) > (data_range/5))
            scaler = LineWidget.init_list_scale[index_scale]
            self.set_lm_value('scale',scaler)
            positioner = abs(data_min) // scaler
            self.set_lm_value('position', positioner)

        self.data_name = data_col
        self.list_scale = LineWidget.init_list_scale
        self.pic = ax

        # init Indicators
        self.label_left = self.pic.annotate('', (0,0), xycoords='data', fontsize=12)#, fontweight='bold')
        self.label_right = self.pic.annotate('', (0,0), xycoords='data', fontsize=12)
        self.label_localmax = self.pic.annotate('', (0, 0),
                                                xytext=(-30, 30), textcoords='offset pixels',
                                                arrowprops=dict(facecolor='white', shrink=0.05),
                                                fontsize=12,
                                                horizontalalignment='right', verticalalignment='top')

        # # 라인하나마다 전부 그리게되어있으므로 위로 올려야함
        # self.label_time_left = self.pic.annotate('', (0, 0), xycoords='data',
        #                                          xytext=(0, 12), textcoords='offset pixels',
        #                                          color='white', fontsize=10)
        # self.label_time_right = self.pic.annotate('', (0, 0), xycoords='data',
        #                                           xytext=(0, 12), textcoords='offset pixels',
        #                                           color='white', fontsize=10)
        # self.label_time_delta = self.pic.annotate('', (0, 0), xycoords='data',
        #                                           xytext=(0, 0), textcoords='offset pixels',
        #                                           color='white', fontsize=10)

        if 'color' in kwargs:
            self.label_left.set_c(kwargs['color'])
            self.label_right.set_c(kwargs['color'])
            self.label_localmax.set_c(kwargs['color'])
            #self.label_localmax.set_arrowstyle(facecolor=kwargs['color'])

        self.x_selected_left = 0
        self.x_selected_right = 0

        self.func_destroy = lambda:func_destroy(self.data_name)

        self.manager = tk.LabelFrame(master, text=self.data_name)#, labelanchor='w')
        self.manager.pack()

        def _button_show_callback():
            self.toggle_visible()
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
            self._update_indicator()
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

        ttk.Button(self.manager, text='del',command=self.func_destroy,width=3).grid(row=0,column=5)
        self._update_indicator()

    def toggle_visible(self):
        if self.get_visible():
            self.set_visible(False)
            self.label_left.set_visible(False)
            self.label_right.set_visible(False)
            self.label_localmax.set_visible(False)

            # self.label_time_left.set_visible(False)
            # self.label_time_right.set_visible(False)
            # self.label_time_delta.set_visible(False)
        else:
            self.set_visible(True)
            self.label_left.set_visible(True)
            self.label_right.set_visible(True)
            self.label_localmax.set_visible(True)

            # self.label_time_left.set_visible(True)
            # self.label_time_right.set_visible(True)
            # self.label_time_delta.set_visible(True)
        self.func_line_update()
        self._update_indicator()

    def update_selected_x(self,x,action=None):
        if action=='left':
            self.x_selected_left = x
        elif action=='right':
            self.x_selected_right = x
        self._update_indicator()

    def _update_indicator(self):
        if not self.get_visible():
            return 0
        # Vertical Line value
        # 리팩토링 필요
        # Left Line
        tmpx = self.x_selected_left
        tmpy = self.get_value_whenx(tmpx ,which='modified')
        self.label_left.xy = (tmpx, 0)
        self.label_left.set_text(f'{tmpy:.1f}')
        tmpy = self.get_value_whenx(tmpx, which='drawing')
        if tmpy >= 9.7:
            tmpy = 9.7
        elif tmpy <= 0:
            tmpy = 0
        self.label_left.set_position((tmpx, tmpy))

        # self.label_time_left.set_text(time_format_plot(tmpx))
        # self.label_time_left.xy = (tmpx,10)

        # Right Line
        tmpx = self.x_selected_right
        tmpy = self.get_value_whenx(tmpx, which='modified')
        self.label_right.xy = (tmpx,0)
        self.label_right.set_text(f'{tmpy:.1f}')
        tmpy = self.get_value_whenx(tmpx, which='drawing')
        if tmpy >= 9.7:
            tmpy = 9.7
        elif tmpy <= 0:
            tmpy = 0
        self.label_right.set_position((tmpx, tmpy))

        # self.label_time_right.set_text(time_format_plot(tmpx))
        # self.label_time_right.xy = (tmpx, 10)

        # Local Max
        data_selected = self.get_data_selected()
        if len(data_selected) > 0:
            index_local_max = pd.Series.idxmax(data_selected)
            y = self.get_ydata()[index_local_max]
            t = self.get_xdata()[index_local_max]
            tmpy = self.get_modified_ydata()[index_local_max]
            self.label_localmax.xy = (t, y)
            self.label_localmax.set_text(f'Max:{tmpy:.2f}')
            self.label_localmax.set_visible(True)

            # self.label_time_delta.xy = (np.average([self.x_selected_right,self.x_selected_left]), 10)
            # self.label_time_delta.set_text(time_format_plot(abs(self.x_selected_right - self.x_selected_left)))
            # self.label_time_delta.set_visible(True)
        else:
            self.label_localmax.set_visible(False)
            # self.label_time_delta.set_visible(False)

    def get_data_selected(self):
        index_min = self._find_closest_index(np.minimum(self.x_selected_left,self.x_selected_right))
        index_max = self._find_closest_index(np.maximum(self.x_selected_left, self.x_selected_right))
        y = self.get_modified_ydata()[index_min:index_max]
        return y

    def remove_self(self):
        pass

    def __del__(self):
        print(f'{self.data_name} has been deleted')


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

        # Time indicator 올리고 삭제
        self.time_container = tk.LabelFrame(self.container, text='Times', bd=2)
        self.time_container.grid(row=0)
        self._add_timeindicator(self.time_container)

        self.label_time_left = None
        self.label_time_right = None
        self.label_time_delta = None

        self.widget_container = tk.LabelFrame(self.container, text='Widgets', bd=2)
        self.widget_container.grid(row=1,columnspan=3)

        self.canvas = tk.Canvas(self.widget_container, width=300, height=600)
        self.bar = tk.Scrollbar(self.widget_container)
        self.bar["command"] = self.canvas.yview
        self.bar_H = tk.Scrollbar(self.widget_container,orient=tk.HORIZONTAL)
        self.bar_H["command"] = self.canvas.xview

        self.canvas.grid(row=0,column=0)
        self.bar.grid(row=0,column=1,sticky=tk.N+tk.S)
        self.bar_H.grid(row=1,column=0,columnspan=2,sticky=tk.W+tk.E)

        self.dframe = tk.Frame(self.canvas)

        self.canvas.create_window(0, 0, window=self.dframe)
        self._update_widget()

    def init_time_label(self, pic):
        # Time indicator
        self.label_time_left = pic.annotate('', (0, 0), xycoords='data',
                                                 xytext=(0, 12), textcoords='offset pixels',
                                                 color='white', fontsize=10)
        self.label_time_right = pic.annotate('', (0, 0), xycoords='data',
                                                  xytext=(0, 12), textcoords='offset pixels',
                                                  color='white', fontsize=10)
        self.label_time_delta = pic.annotate('', (0, 0), xycoords='data',
                                                  xytext=(0, 0), textcoords='offset pixels',
                                                  color='white', fontsize=10)
        self.label_time_delta.set_visible(False)

    # Time indicator 올리고 삭제
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

            tmp = LineWidget(self.dframe, ax, func_line_update, self.remove_linewidget,
                             data_col=data_name, time_col=time_col, data=data,
                             color=color,**kwargs)

            self.list_linewidget[data_name] = tmp
            ax.add_line(tmp)
            self._update_widget()
            func_line_update()
        #return self.list_linewidget

    def remove_linewidget(self,col):
        if col in self.list_linewidget.keys():
            self.list_linewidget[col].remove()
            self.list_linewidget[col].manager.destroy()
            del self.list_linewidget[col]
        self._update_widget()

    def _update_widget(self):
        self.canvas.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox('all'),
                              yscrollcommand=self.bar.set,
                              xscrollcommand=self.bar_H.set)

    def update_selected(self,x,action=None):
        for line in self.list_linewidget.values():
            line.update_selected_x(x,action=action)

        # Time indicator 올리고 삭제
        if len(self.list_linewidget) > 0:
            self.time_selected_left.set(f'Start : \n{time_format(line.x_selected_left)}')
            self.time_selected_right.set(f'End : \n{time_format(line.x_selected_right)}')
            tmp = abs(line.x_selected_right - line.x_selected_left)
            self.time_selected_delta.set(f'Delata : \n{time_format(tmp)}')

        self.label_time_left.set_text(time_format_plot(line.x_selected_left))
        self.label_time_left.xy = (line.x_selected_left,10)

        self.label_time_right.set_text(time_format_plot(line.x_selected_right))
        self.label_time_right.xy = (line.x_selected_right, 10)

        self.label_time_delta.xy = (np.average([line.x_selected_right, line.x_selected_left]), 10)
        self.label_time_delta.set_text(time_format_plot(abs(line.x_selected_right - line.x_selected_left)))
        self.label_time_delta.set_visible(True)
    def __del__(self):
        print('LineContainer has been deleted')


class VerticalLine(matplotlib.lines.Line2D):
    def __init__(self, x, ax, func_line_update,y=[-1,11], **kwargs):
        matplotlib.lines.Line2D.__init__(self, [x,x], y, **kwargs)
        ax.add_line(self)
        self.func_line_update = func_line_update

    def update_xdata(self,x):
        self.set_xdata([x,x])

    def __del__(self):
        print('VerticalLine has been deleted')