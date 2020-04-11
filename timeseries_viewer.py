from func_util import *
from line_manager import *
from PlottingCanvas import PlottingCanvas


class TimeSeriesViewer():
    def __init__(self, data=None, time_col='Time', main_col=None, predraw_col=None, draw_at_once=False, Ts=0.1):
        self.win = tk.Tk()
        self.win.title('TimeSeriesViewer_JSH')
        self.win.minsize(width=1800,height=900)
        #self.win.resizable(width=False,height=False)

        self.optiontab = ttk.Notebook(self.win)
        self.optiontab.grid(row=0,column=1)
        frame1 = tk.Frame(self.optiontab)
        frame2 = tk.Frame(self.optiontab)
        self.optiontab.add(frame1, text='파일 읽기')
        self.optiontab.add(frame2, text='Line관리')

        ###############################################################################################################
        # Init Attributes
        ###############################################################################################################
        self.data = None
        self.datalist = None
        self.time_col = None

        ###############################################################################################################
        # Create Widgets
        ###############################################################################################################
        # Create Data selector
        self.dataselector = DataSelector(frame2, [0, 0])

        # Create LineContainer
        self.line_container = LineContainer(frame2, [1, 0])

        # Create Canvas
        self.canvas = PlottingCanvas(self.win, self.line_container, [0, 0])

        # Test
        self.button_test = tk.Button(self.win, text='Test',command=self._test)
        self.button_test.grid(row=2,column=2)
        self.button_test = tk.Button(self.win, text='clearTest',command=self._clear_test)
        self.button_test.grid(row=2,column=3)

#        LineConfigurator()
        ###############################################################################################################
        # Initialize
        ###############################################################################################################
        self.pic_main = self.canvas.pic_main
        self.pic_boolean = self.canvas.pic_boolean
        self.pic_summary = self.canvas.pic_summary
        self.pic_analysis = self.canvas.pic_analysis

        # Main Picture에 TimeLabel 추가, 이부분 좀 꼬인듯
        self.line_container.init_time_label(self.canvas.pic_main)

        #self.win.focus_set(True)

        if data is not None:
            self.read_data(data, time_col, main_col, Ts)
            self._initial_draw(predraw_col=predraw_col, draw_at_once=draw_at_once)
            # 데이터가 있을경우 두번째 페이지 바로 선택되기 구현 필요함

        self.win.mainloop()

    def read_data(self, data, time_col, main_col, Ts):
        self.data = data
        self.datalist = data.columns[1:]
        self.Ts = Ts
        self.time_col = time_col

        self.dataselector.set_datalist(self.datalist)
        self.dataselector.bind_button_main(lambda x:self.add_col(self.pic_main, x))
        self.dataselector.bind_button_bool(lambda x: self.add_col(self.pic_boolean, x))

        if (main_col is None) or (main_col not in self.datalist):
            main_col = self.datalist[0]
        self.canvas.pic_summary.plot(self.data[self.time_col], self.data[main_col], color='forestgreen')
        self.canvas.pic_summary.set_ylim(0,1000)

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

    def add_col(self, ax, col):
        self.line_container.add_linewidget(ax, self.data, col, self.canvas.update, time_col=self.time_col,\
                                           alpha=0.5, drawstyle='steps-post',linewidth=1.5)#marker='o',markersize=1,

    def _test(self):
        data = self.line_container.list_linewidget['dat2'].get_data_selected()
        length = len(data)
        n = np.arange(-length/2,length/2,1)
        f = n / length / self.Ts
        F = np.fft.fftshift(np.fft.fft(data))
        self.pic_analysis.plot(f,abs(F),'-ro',markersize=1)#,linestyle='')
        self.pic_analysis.grid(True)
        self.pic_analysis.set_yscale('log')
        self.pic_analysis.set_xticks(np.linspace(0,f[-1],20))
        self.pic_analysis.set_xticklabels(list(map(lambda x:np.round(x,decimals=2), self.pic_analysis.get_xticks())), rotation=20)
        self.pic_analysis.set_xlim([0, f[-1]])
        self.canvas.update()

    def _clear_test(self):
        self.pic_analysis.cla()
        self.canvas.update()

if __name__ == '__main__':
    import pandas as pd
    import numpy as np
    data = pd.DataFrame()
    dlen = 30000
    Ts = 0.01
    data['Time'] = np.arange(0, dlen * Ts, Ts)
    data['dat1'] = 2 * np.sin(2 * np.pi * 2 * data['Time']) + data['Time']
    data['dat2'] = 2 * np.sin(2 * np.pi * 1 * data['Time']) + 5 * np.cos(2 * np.pi * 3 * data['Time']) + 8 * np.cos(2 * np.pi * 12 * data['Time'])\
                   + 0.8 * np.random.randn(dlen)
    data['dat3'] = 0.3 * np.random.randn(dlen) + data['dat2']
    data['dat4'] = 0.2 * np.random.randn(dlen) + data['dat3']
    data['dat5'] = 0.1 * np.random.randn(dlen) + data['dat4']

    a = TimeSeriesViewer(data,main_col='dat1',predraw_col=['dat1','dat2'],Ts=Ts)#,draw_at_once=True)