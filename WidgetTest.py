import tkinter as tk
from tkinter import ttk

class LineController():
    def __init__(self,master,data_name='var'):
        manager = tk.Frame(master)
        manager.pack()

        name = tk.Label(manager, text=data_name).grid(row=0, column=0, rowspan=4, sticky=tk.N + tk.S)
        on_off = ttk.Button(manager, text='On/Off', width=5).grid(row=0, column=1)

        self.position = tk.LabelFrame(manager,text='Position')
        self.position.grid(row=0,column=1)
        pos_10up = ttk.Button(self.position,text='+',width=3).grid(row=0,column=0)
        pos_1up = ttk.Button(self.position,text='++',width=3).grid(row=0,column=1)
        pos_val = ttk.Label(self.position,text=' ').grid(row=1,column=0,columnspan=2)
        pos_1down = ttk.Button(self.position,text='-',width=3).grid(row=2,column=0)
        pos_10down = ttk.Button(self.position,text='--',width=3).grid(row=2,column=1)

        scale = tk.LabelFrame(manager,text='Scale')
        scale.grid(row=0,column=2)
        scale_up = ttk.Button(scale,text='+',width=3).grid(row=0,column=0)
        scale_val = ttk.Label(scale, text=' ').grid(row=1, column=0)
        scale_down = ttk.Button(scale,text='-',width=3).grid(row=2,column=0)
    def get_buttonlist(self):
        print(self.position.winfo_children())

win = tk.Tk()
win.geometry("640x400+100+100")
container = tk.LabelFrame(win,text='최상위',bd=2)#,text='variable manager')
container.pack()#grid(row=0, column=0)

canvas =  tk.Canvas(container,width=200,height=400)
bar = tk.Scrollbar(container)
bar ["command"]=canvas.yview
canvas.pack(side='left')#fill='both', expand=True, side='left')
bar.pack(fill='y', side='right')

datalist = tk.Frame(canvas)

canvas.create_window(0, 0, window=datalist)
canvas.update_idletasks()

canvas.configure(scrollregion=canvas.bbox('all'),
                 yscrollcommand=bar.set)
# for dname in data:
#     LineController(datalist,dname)
    # manager = tk.LabelFrame(datalist)
    # manager.pack()
    # name = tk.Label(manager,text=dname).grid(row=0,column=0,rowspan=4,sticky=tk.N+tk.S)
    # on_off = ttk.Button(manager,text='On/Off',width=5).grid(row=0,column=1)
    #
    # position = tk.LabelFrame(manager,text='Position')
    # position.grid(row=0,column=1)
    # pos_10up = ttk.Button(position,text='+',width=3).grid(row=0,column=0)
    # pos_1up = ttk.Button(position,text='++',width=3).grid(row=0,column=1)
    # pos_val = ttk.Label(position,text=' ').grid(row=1,column=0,columnspan=2)
    # pos_1down = ttk.Button(position,text='-',width=3).grid(row=2,column=0)
    # pos_10down = ttk.Button(position,text='--',width=3).grid(row=2,column=1)
    #
    # scale = tk.LabelFrame(manager,text='Scale')
    # scale.grid(row=0,column=2)
    # scale_up = ttk.Button(scale,text='+',width=3).grid(row=0,column=0)
    # scale_val = ttk.Label(scale, text=' ').grid(row=1, column=0)
    # scale_down = ttk.Button(scale,text='-',width=3).grid(row=2,column=0)

#canvas.create_window(0, 0, window=datalist)# anchor='nw',

# canvas.update_idletasks()
#
# canvas.configure(scrollregion=canvas.bbox('all'),
#                  yscrollcommand=bar.set)
def add_data(data):
    a = LineController(datalist, data)
    a.get_buttonlist()
    canvas.update_idletasks()
    canvas.configure(scrollregion=canvas.bbox('all'),
                     yscrollcommand=bar.set)


data = ['var1','var2','var3','var4','var1','var2','var3','var4','var1','var2','var3','var4','var1','var2','var3','var4']
for dname in data:
    add_data(dname)
win.mainloop()

