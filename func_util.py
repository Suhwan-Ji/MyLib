import numpy as np

def isiter(x):
    """Check whether input is iterable"""
    try:
        iter(x)
        return True
    except:
        return False


class LimitedList():
    '''Entry limited list

    methods:
    - get_index : find index of value in Limited List
    - transform_value : transform input value in to value in Limited List
    - get_now : get currently pointing value
    - _next : get next entry value and move pointer forward
    - _before : get pre entry value and move pointer backward
    '''
    def __init__(self,dlist,init_value=1):
        self.dlist = np.sort(np.array(dlist))
        self.index_max = len(self.dlist)-1
        self.index_now = self.get_index(init_value)
    def transform_value(self,x):
        return self.dlist[(self.dlist <= x)][-1] if x > self.dlist[0] else self.dlist[0]
    def get_index(self,val):
        value = self.transform_value(val)
        return np.where(self.dlist == value)[0][0]
    def set_value(self,value):
        self.index_now = self.get_index(value)
    def get_now(self):
        return self.dlist[self.index_now]
    def _next(self,step=1):
        """get next entry value and move pointer forward

        params:
         - step : how many steps to change in one call
        """
        tmp = self.index_now + step
        self.index_now = tmp if tmp < self.index_max else self.index_max
        return self.get_now()
    def _before(self,step=1):
        """get pre entry value and move pointer backward

        params:
         - step : how many steps to change in one call
        """
        tmp = self.index_now - step
        self.index_now = tmp if tmp > 0 else 0
        return self.get_now()