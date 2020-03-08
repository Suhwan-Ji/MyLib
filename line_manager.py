from func_util import LimitedList
import matplotlib


class LineManager(matplotlib.lines.Line2D):
    def __init__(self, x, y, scalelist=[1], poslist=[0], scale=1, offset=0, gain=1, **kwargs):
        matplotlib.lines.Line2D.__init__(self, x, y, **kwargs)

        self.yscalelist = LimitedList(scalelist, scale)
        self.yposlist = LimitedList(poslist, poslist[0])
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

    def set_style(self):
        pass

    def destroy(self):
        self.remove()
        pass