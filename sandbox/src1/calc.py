# a tiny Tkinter calculator (improved v.1.2)
# tested with Python25    vegaseat    01apr2007

"""
calculator has a layout like this ...
<   display   >
7  8  9  *  C
4  5  6  /  M->
1  2  3  -  ->M
0  .  =  +  neg
"""

import Tkinter as tk

def click(key):
    global memory
    if key == '=':
        # avoid division by integer
        if '/' in entry.get() and '.' not in entry.get():
            entry.insert(tk.END, ".0")
        # guard against the bad guys abusing eval()
        str1 = "-+0123456789."
        if entry.get()[0] not in str1:
            entry.insert(tk.END, "first char not in " + str1)
        # here comes the calculation part
        try:
            result = eval(entry.get())
            entry.insert(tk.END, " = " + str(result))
        except:
            entry.insert(tk.END, "--> Error!")
    elif key == 'C':
        entry.delete(0, tk.END)  # clear entry
    elif key == '->M':
        memory = entry.get()
        # extract the result
        if '=' in memory:
            ix = memory.find('=')
            memory = memory[ix+2:]
        root.title('M=' + memory)
    elif key == 'M->':
        entry.insert(tk.END, memory)
    elif key == 'neg':
        if '=' in entry.get():
            entry.delete(0, tk.END)
        try:
            if entry.get()[0] == '-':
                entry.delete(0)
            else:
                entry.insert(0, '-')
        except IndexError:
            pass
    else:
        # previous calculation has been done, clear entry
        if '=' in entry.get():
            entry.delete(0, tk.END)
        entry.insert(tk.END, key)

root = tk.Tk()
root.title("Tiny Tk Calculator")

btn_list = [
'7',  '8',  '9',  '*',  'C',
'4',  '5',  '6',  '/',  'M->',
'1',  '2',  '3',  '-',  '->M',
'0',  '.',  '=',  '+',  'neg' ]

# create all buttons with a loop
r = 1
c = 0
for b in btn_list:
    rel = 'ridge'
    cmd = lambda x=b: click(x)
    tk.Button(root,text=b,width=5,relief=rel,command=cmd).grid(row=r,column=c)
    #print b, r, c  # test
    c += 1
    if c > 4:
        c = 0
        r += 1

# use Entry widget for an editable display
entry = tk.Entry(root, width=33, bg="yellow")
entry.grid(row=0, column=0, columnspan=5)

root.mainloop()
