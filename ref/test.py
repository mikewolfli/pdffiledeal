#coding=utf-8
'''
Created on 2016年9月7日

@author: 10256603
'''
import tkinter
root = tkinter.Tk()
top = tkinter.Toplevel(root)
top.overrideredirect(1) #removes border but undesirably from taskbar too (usually for non toplevel windows)
root.attributes("-alpha",0.0)

#toplevel follows root taskbar events (minimize, restore)
def onRootIconify(event): top.withdraw()
root.bind("<Unmap>", onRootIconify)
def onRootDeiconify(event): top.deiconify()
root.bind("<Map>", onRootDeiconify)

window = tkinter.Frame(master=top)
window.mainloop()