#!/usr/bin/env python
"""
  fileaction.py 'display' '*.ps' '*.jpg' '*.gif'

creates a GUI with a list of all PostScript, JPEG, and GIF files in
the directory tree with the current working directory as root.
Clicking on one of the filenames in the list launches the display
program, which displays the image file.

As another example,

  fileaction.py 'xanim' '*.mpg' '*.mpeg'

gives an overview of all MPEG files in the directory tree and
the possibility to play selected files with the xanim application.

The general interface is

  fileactionGUI.py command filetype1 filetype2 filetype3 ...
"""

from Tkinter import *
import Pmw, os, sys

class FileActionGUI:
    def __init__(self, parent, file_patterns, command):
        self.master = parent
        self.top = Frame(parent)
        self.top.pack(expand=True, fill='both')
        self.file_patterns = file_patterns
        self.files = self.find_files()

        self.list1 = Pmw.ScrolledListBox(self.top,
             listbox_selectmode='single', # or 'multiple'
             vscrollmode='dynamic', hscrollmode='dynamic',
             listbox_width=min(max([len(f) for f in self.files]),40),
             listbox_height=min(len(self.files),20),
             label_text='files', labelpos='n',
             items=self.files,
             selectioncommand=self.select)
        self.list1.pack(side='top', padx=10, expand=True, fill='both')

        self.command = StringVar(); self.command.set(command)
        Pmw.EntryField(self.top,
            labelpos='w', label_text='process file with',
            entry_width=len(command)+5,
            entry_textvariable=self.command).pack(side='top',pady=3)
        Button(self.top, text='Quit', width=8, command=self.master.destroy).pack(pady=2)

    def select(self):
        file = self.list1.getcurselection()[0]
        cmd = '%s %s &' % (self.command.get(), file)
        os.system(cmd)
        
    def find_files(self):
        from scitools.misc import find
        def check(filepath, arg):
            ext = os.path.splitext(filepath)[1]
            import fnmatch  # Unix shell-style wildcard matching
            for s in self.file_patterns:
                if fnmatch.fnmatch(ext, s):
                    arg.append(filepath)
        files = []
        find(check, os.curdir, files)
        return files
            
if __name__ == '__main__':
    root = Tk()
    Pmw.initialise(root)
    import scitools.misc; scitools.misc.fontscheme3(root)
    try:
        command = sys.argv[1]
        file_patterns = sys.argv[2:]
    except:
        print 'Usage: %s file-command filetype1 filetype2 ...' % sys.argv[0]
        print "Example: fileactionGUI.py 'display' '*.ps' '*.eps' '*.jpg'"
        print 'A GUI with a list of all files matching the specified'
        print 'patterns is launched. By clicking on one of the filenames,'
        print 'the specified command is run with that file as argument.'
        sys.exit(1)
    g = FileActionGUI(root, file_patterns, command)
    root.mainloop()

