#!/usr/bin/python3
# -*- coding: utf-8 -*-

try:
    import tkinter as tk
    import tkinter.ttk as ttk
except:
    import Tkinter as tk
    import ttk as ttk

class VerticalScrollFrame(ttk.Frame):
    """A ttk frame allowing vertical scrolling only.
    Use the '.interior' attribute to place widgets inside the scrollable frame.

    Adapted from https://gist.github.com/EugeneBakin/76c8f9bcec5b390e45df.
    Amendments:
    1. Original logic for configuring the interior frame and canvas
       scrollregion left canvas regions exposed (not suppose to) and allowed
       vertical scrolling even when canvas height is greater than the canvas
       required height, respectively. I have provided a new logic to
       resolve these issues.
    2. Provided options to configure the styles of the ttk widgets.
    3. Tested in Python 3.5.2 (default, Nov 23 2017, 16:37:01),
                 Python 2.7.12 (default, Dec  4 2017, 14:50:18) and
                 [GCC 5.4.0 20160609] on linux.

    Author: Sunbear
    Website: https://github.com/sunbearc22
    Created on: 2018-02-26
    Amended on: 2018-03-01 - corrected __configure_canvas_interiorframe() logic.  
    """

    
    def __init__(self, parent, *args, **options):
        """
        WIDGET-SPECIFIC OPTIONS:
           style, pri_background, sec_background, arrowcolor,
           mainborderwidth, interiorborderwidth, mainrelief, interiorrelief 
        """
        # Extract key and value from **options using Python3 "pop" function:
        #   pop(key[, default])
        style          = options.pop('style',ttk.Style())
        pri_background = options.pop('pri_background','light grey')
        sec_background = options.pop('sec_background','grey70')
        arrowcolor     = options.pop('arrowcolor','black')
        mainborderwidth     = options.pop('mainborderwidth', 0)
        interiorborderwidth = options.pop('interiorborderwidth', 0)
        mainrelief          = options.pop('mainrelief', 'flat')
        interiorrelief      = options.pop('interiorrelief', 'flat')

        ttk.Frame.__init__(self, parent, style='main.TFrame',
                           borderwidth=mainborderwidth, relief=mainrelief)

        self.__setStyle(style, pri_background, sec_background, arrowcolor)

        self.__createWidgets(mainborderwidth, interiorborderwidth,
                             mainrelief, interiorrelief,
                             pri_background)
        self.__setBindings()


    def __setStyle(self, style, pri_background, sec_background, arrowcolor):
        '''Setup stylenames of outer frame, interior frame and verticle
           scrollbar'''        
        style.configure('main.TFrame', background=pri_background)
        style.configure('interior.TFrame', background=pri_background)
        style.configure('canvas.Vertical.TScrollbar', background=pri_background,
                        troughcolor=sec_background, arrowcolor=arrowcolor)

        style.map('canvas.Vertical.TScrollbar',
            background=[('active',pri_background),('!active',pri_background)],
            arrowcolor=[('active',arrowcolor),('!active',arrowcolor)])


    def __createWidgets(self, mainborderwidth, interiorborderwidth,
                        mainrelief, interiorrelief, pri_background):
        '''Create widgets of the scroll frame.'''
        self.vscrollbar = ttk.Scrollbar(self, orient='vertical',
                                        style='canvas.Vertical.TScrollbar')
        self.vscrollbar.pack(side='right', fill='y', expand='false')
        self.canvas = tk.Canvas(self,
                                bd=0, #no border
                                highlightthickness=0, #no focus highlight
                                yscrollcommand=self.vscrollbar.set,#use self.vscrollbar
                                background=pri_background #improves resizing appearance
                                )
        self.canvas.pack(side='left', fill='both', expand='true')
        self.vscrollbar.config(command=self.canvas.yview)

        # reset the view
        self.canvas.xview_moveto(0)
        self.canvas.yview_moveto(0)

        # create a frame inside the canvas which will be scrolled with it
        self.interior = ttk.Frame(self.canvas,
                                  style='interior.TFrame',
                                  borderwidth=interiorborderwidth,
                                  relief=interiorrelief)
        self.interior_id = self.canvas.create_window(0, 0,
                                                     window=self.interior,
                                                     anchor='nw')


    def __setBindings(self):
        '''Activate binding to configure scroll frame widgets.'''
        self.canvas.bind('<Configure>',self.__configure_canvas_interiorframe)
        

    def __configure_canvas_interiorframe(self, event):
        '''Configure the interior frame size and the canvas scrollregion'''
        #Force the update of .winfo_width() and winfo_height()
        self.canvas.update_idletasks() 

        #Internal parameters 
        interiorReqHeight= self.interior.winfo_reqheight()
        canvasWidth    = self.canvas.winfo_width()
        canvasHeight   = self.canvas.winfo_height()

        #Set interior frame width to canvas current width
        self.canvas.itemconfigure(self.interior_id, width=canvasWidth)
        
        # Set interior frame height and canvas scrollregion
        if canvasHeight > interiorReqHeight:
            #print('canvasHeight > interiorReqHeight')
            self.canvas.itemconfigure(self.interior_id,  height=canvasHeight)
            self.canvas.config(scrollregion="0 0 {0} {1}".
                               format(canvasWidth, canvasHeight))
        else:
            #print('canvasHeight <= interiorReqHeight')
            self.canvas.itemconfigure(self.interior_id, height=interiorReqHeight)
            self.canvas.config(scrollregion="0 0 {0} {1}".
                               format(canvasWidth, interiorReqHeight))


class App(ttk.Frame):

    def __init__(self, parent, *args, **kwargs):
        BG0 = '#aabfe0' #Blue scheme
        BG1 = '#4e88e5' #Blue scheme

        ttk.Frame.__init__(self, parent=None, style='App.TFrame', borderwidth=0,
                           relief='raised', width=390, height=390)
        self.parent = parent
        self.parent.title('VerticalScrollFrame')
        self.parent.geometry('300x350')
        
        self.setStyle()
        self.createWidgets(BG0, BG1)
        
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)


    def setStyle(self):
        style = ttk.Style()
        style.configure('App.TFrame', background='pink')


    def createWidgets(self, BG0, BG1):
        self.frame = VerticalScrollFrame(self,
                                        pri_background=BG1,
                                        sec_background=BG0,
                                        arrowcolor='white',
                                        mainborderwidth=10,
                                        interiorborderwidth=10,
                                        mainrelief='raised',
                                        interiorrelief='sunken'
                                        )
        self.frame.grid(row=0, column=0, sticky='nsew')

        text="Shrink the window to activate the scrollbar."
        self.label = tk.Label(background='white', text=text)
        self.label.grid(row=1, column=0, sticky='nsew')

        buttons = []
        for i in range(10):
            buttons.append(ttk.Button(self.frame.interior,
                                      text="Button " + str(i)))
            buttons[-1].grid(row=i, column=0, sticky='nsew')

        '''self.textbox = tk.Text(self.frame.interior,
                                width=30,
                                height=8,
                                foreground='white',
                                background='grey',
                                borderwidth=3,
                                relief='sunken')
        self.textbox.grid(row=1, column=0, sticky='nsew')'''
               

if __name__ == '__main__':
    root = tk.Tk()
    app = App(root)
    app.grid(row=0, column=0, sticky='nsew')
    root.rowconfigure(0, weight=1)
    root.columnconfigure(0, weight=1)

    root.mainloop()

