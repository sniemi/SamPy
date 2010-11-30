#
#MODULE spss_tk_util
#
#***********************************************************************
"""

   **PURPOSE** --
   A module for entry widgets

   **DEVELOPER** --
   Greg Wenzel

   **MODIFICATION HISTORY** --
   Initial implementation              GWW       07/07/00
   Code review changes                 GWW       07/18/00
   Remove duplicate parameter          drc       01/16/02
   Create only one error popup
    per error                          drc       07/01/03
   fix file_list_box                   drc       03/01/04
"""
#***********************************************************************

from exceptions import *
from boolean import *
import os

__version__ = "3/1/04"


#The following does not currently import on VMS because the version
#of python on VMS does not contain Tkinter.  So, it's in a try block.
#the calling program must determine if gui functions are allowed.
try:
   from Tkinter import *
   GUI_AVAILABLE = true
except:
   GUI_AVAILABLE = false

if GUI_AVAILABLE:

    class SpssEntry(Entry):
        """Entry widget for data entry.
           master       - is the main window.
           name_value   - serves as a title for the error 
                          popup "<name_value> Error!".
           value        - is the initial value to appear in entry field.
           validate_fun - is the function to act in the data entered and/or
                          provide validation. Must act on string data and
                          return the proper type to match format.
           format       - is the format of data in entry field default is '%s'
           bg_error     - color to highlight if validate_fun returns exception.
           other parameters are standard tkinter Entry widget parameters.
        """

        def __init__(self,master,value,validate_fun,
            format              = '%s',
            name_value          = '',
            bg_error            = 'red',
            background          = 'lightgrey',
            foreground          = 'black',
            fg_error            = 'white',
            highlightbackground = '#d9d9d9',
            highlightcolor      = 'Black',
            justify             = 'left',
            insertbackground    = 'Black',
            state               = 'normal',
            width               = 15):

            #call sub class __init__ to start creation of object.
            Entry.__init__(self,master,
                width               = width,
                background          = background,
                foreground          = foreground,
                justify             = justify,
                insertbackground    = insertbackground,
                state               = state)

            self.last_error    = None          #exception text from failed 
            self.format        = format        #data format default is '%s'
            self.name_value    = name_value    #string to describe entry.
            self.validate_fun  = validate_fun  #validation function
            self.error         = false         #error state of entry field
            self.bg_error      = bg_error      #color of background for 
                                               #error in input.
            self.fg_error      = fg_error      #color of foreground for 
                                               #error in input.
            self.fg_default    = foreground    #default NO error foreground
            self.bg_default    = background    #default NO error background
            self.value         = value         #initial field value.
            self.value_default = value         #default field value.

            self.insert(0,self.format % self.value_default)
            self.set_value()

            #define binding to set and validate the value upon leaving
            #the entry field.
            self.bind("<Leave>",self.set_value)
            self.bind("<Tab>",self.set_value)

            #define binding to set and validate the value back to the default
            #upon a Control-r event.
            self.bind("<Control-r>",self.reset)

        def reset(self,event=None):
            """Resets the value of the entry field to the default value."""
            self.delete(0,END)
            self.insert(0,self.format % self.value_default)
            self.set_value()

        def set_value(self,event=None):
            """Sets the value of the entry field and attitude attribute
            to the value in the field"""
            try:
                self.value = apply(self.validate_fun,[self.get()])
                self.delete(0,END)
                self.insert(0,self.format % self.value)
                self.set_error_state(false)
            except Exception,self.last_error:
                if not self.error:
                    self.set_error_state(true)
                    title_text = "%s Error!" % self.name_value
                    error_message = Error_Window(self,self.last_error,
                                                 title = title_text)

        def get_error_state(self):
            """sets error state of entry widget.
            """
            self.set_value()
            return self.error
      
        def set_error_state(self,on):
            """sets error state of entry widget.
            """
            if on:
                self.error = true 
                self['background']  = self.bg_error
                self['foreground']  = self.fg_error
            else:
                self.error = false
                self['background'] = self.bg_default
                self['foreground'] = self.fg_default


    class IntEntry(SpssEntry):
        """entry widget for integer values bounded by
           max_value and min_value.
        """ 
        def __init__(self,master,value,
            format              = '%i',
            max_value           =  None,
            min_value           =  None,
            name_value          =  '',
            bg_error            = 'red',
            background          = 'lightgrey',
            foreground          = 'black',
            fg_error            = 'white',
            highlightbackground = '#d9d9d9',
            highlightcolor      = 'Black',
            justify             = 'left',
            insertbackground    = 'Black',
            state               = 'normal',
            width               = None):

                self.format             = format
                self.value              = value
                self.max_value          = max_value
                self.min_value          = min_value
                self.name_value         = name_value

                if width is not None:
                    self.width          = width
                elif width is None and max_value is not None:
                    self.width          = len(format % max_value)
                else:
                    self.width          = 15
        
                SpssEntry.__init__(self,master,self.value,self.validate,
                    format              = self.format,
                    name_value          = name_value,
                    bg_error            = bg_error,
                    background          = background,
                    foreground          = foreground,
                    fg_error            = fg_error,
                    highlightbackground = highlightbackground,
                    highlightcolor      = highlightcolor,
                    justify             = justify,
                    insertbackground    = insertbackground,
                    state               = state,
                    width               = self.width)

        def get(self,event=None):
            """get integer value from field"""
            self.value = int("%s" % SpssEntry.get(self))
            return self.value
       
        def validate(self,event=None):
            """validate field. set background to self.bg_error
            if error in input"""

            self.get()
            if self.value is not None:
                if self.value > self.max_value or self.value < self.min_value:
                    error =  '\n%s must be between %s and %s.\n' %\
                       (self.name_value,self.format,self.format)
                    error = error % (self.min_value,self.max_value)
                    raise IOError(error)

            return self.value

    class FloatEntry(SpssEntry):
        """entry widget for float values bounded by
           max_value and min_value.
        """ 
        def __init__(self,master,value,
            format              = '%f',
            name_value          =  '',
            max_value           =  None,
            min_value           =  None,
            bg_error            = 'red',
            background          = 'lightgrey',
            foreground          = 'black',
            fg_error            = 'white',
            highlightbackground = '#d9d9d9',
            highlightcolor      = 'Black',
            justify             = 'left',
            insertbackground    = 'Black',
            state               = 'normal',
            width               = None):

                self.format             = format
                self.value              = value
                self.max_value          = max_value
                self.min_value          = min_value
                self.name_value         = name_value

                if width is not None:
                    self.width          = width
                elif width is None and max_value is not None:
                    self.width          = len(format % max_value)
                else:
                    self.width          = 15
        
                SpssEntry.__init__(self,master,self.value,self.validate,
                    format              = self.format,
                    bg_error            = bg_error,
                    background          = background,
                    foreground          = foreground,
                    fg_error            = fg_error,
                    highlightbackground = highlightbackground,
                    highlightcolor      = highlightcolor,
                    justify             = justify,
                    insertbackground    = insertbackground,
                    state               = state,
                    width               = self.width)

        def get(self,event=None):
            """get float value from field"""
            self.value = float("%s" % SpssEntry.get(self))
            return self.value

        def validate(self,event=None):
            """validate field. set background to self.bg_error
            if error in input"""

            self.get()
            if self.value is not None:
                if self.value > self.max_value or self.value < self.min_value:
                    error =  '\n%s must be between %s and %s.\n' %\
                        (self.name_value,self.format,self.format)
                    error = error % (self.min_value,self.max_value)
                    raise IOError(error)
            return self.value

    class file_list_box(Frame):
        """entry widget for file names.  creates a what you see is what 
           you get box. ie. the only visable entry is the active one.
           requires a tuple (<list of files>, <selected file>)
           <file_name_only> - if false full path is listed else only file name.
        """ 
        def __init__(self,master,list_tuple,
            file_name_only=false,
            width  = None):
            Frame.__init__(self,master)
            
            self.width = width
            if self.width is None:
                self.width = 40
            self.file_list = list_tuple[0]
            if list_tuple[1]:
               index_selection = self.file_list.index(list_tuple[1])
            else:
               index_selection = 0

            #define scroll bar intention is to use arrows to
            #navigate selections.
            scrollbar      = Scrollbar(self,orient=VERTICAL)
            scrollbar.config(command=self.yview)
            scrollbar.pack(side=RIGHT, fill=Y)
 
            #define a entry box 1 row in height
            self.entry_box = Listbox(self,width= self.width,height=1,
                yscrollcommand=scrollbar.set, exportselection=0)
            for file_path in self.file_list:
                if file_name_only:
                    file_name = os.path.basename(file_path)
                else:
                    file_name = file_path
                if self.file_list.index(file_path) == index_selection:
                    file_name = file_name + "   -Default "
                if len(file_name) > self.width:
                    self.width = len(file_name)
                self.entry_box.insert(END,file_name)
            self.entry_box['width'] = self.width
            self.entry_box.select_set(index_selection)
            self.entry_box.activate(index_selection)
            self.entry_box.see(index_selection)
            self.reset_index = index_selection
            self.entry_box.pack(side=LEFT, fill=X, expand=1)

        #force viewed element to be selected and active index.  what you
        #see in field is what you get\!

        def yview(self, *args):
            apply(self.entry_box.yview, args)
            current_selection_tup = self.entry_box.curselection()
            if current_selection_tup:
                index = int(current_selection_tup[0])
                index_new = int(float(args[1])) + index
                if index_new >= 0 and \
                index_new < self.entry_box.size():
                    self.entry_box.select_clear(index)
                    self.entry_box.select_set("%s" % index_new)
                    self.entry_box.activate("%s" % index_new)

        def get(self,event=None):
            """returns the value of the current selection"""

            if self.file_list:
               return self.file_list[int(
                  self.entry_box.curselection()[0])]
            else:
               return ''

        def reset(self,event=None):
            """resets the selected field to the default value"""
            current_selection_tup = self.entry_box.curselection()
            if current_selection_tup:
                index = int(current_selection_tup[0])
                self.entry_box.select_clear(index)
                self.entry_box.select_set("%s" % self.reset_index)
                self.entry_box.see("%s" % self.reset_index)
                self.entry_box.activate("%s" % self.reset_index)

    class Error_Window(Toplevel):
        """Error window class with ok button."""

        def __init__(self, parent,text_value,title = "ERROR !!!"):

            Toplevel.__init__(self, parent)

            self.transient(parent)
            self.parent = parent
            self.title(title)

            #create an ok button.
            Label(self, text=text_value).pack()
            b = Button(self, text="OK", command=self.ok)
            b.pack()

            self.geometry("+%d+%d" % (parent.winfo_rootx()+50,
                                  parent.winfo_rooty()+50))

            #set binding to ok button to allow <CR> to close window.
            b.focus_set()
            b.bind("<Return>",self.ok)

            #if window destroyed by other than ok button use ok function."
            self.protocol("WM_DELETE_WINDOW", self.ok)

            #wait until window is visible then grab control 
            #of keyboard commands.
            self.wait_visibility(self)
            self.grab_set()

            self.wait_window(self)

        def ok(self,event=None):
            """destroys error message window"""

            self.parent.focus_set()
            self.withdraw()
            self.update_idletasks()
            self.destroy()

