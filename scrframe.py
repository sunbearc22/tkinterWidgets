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
    """

    
    def __init__(self, parent, *args, **options):
        """
        WIDGET-SPECIFIC OPTIONS:
           style, pri_background, sec_background, arrowcolor,
           outerborderwidth, interiorborderwidth, outerrelief, interiorrelief 
        """
        # Extract key and value from **options using Python3 "pop" function:
        #   pop(key[, default])
        style          = options.pop('style',ttk.Style())
        pri_background = options.pop('pri_background','light grey')
        sec_background = options.pop('sec_background','grey70')
        arrowcolor     = options.pop('arrowcolor','black')
        outerborderwidth    = options.pop('outerborderwidth', 0)
        interiorborderwidth = options.pop('interiorborderwidth', 0)
        outerrelief         = options.pop('outerrelief', 'flat')
        interiorrelief      = options.pop('interiorrelief', 'flat')

        ttk.Frame.__init__(self, parent, style='scr.TFrame',
                           borderwidth=outerborderwidth, relief=outerrelief)

        self.__setStyle(style, pri_background, sec_background, arrowcolor)
        self.__createWidgets(outerborderwidth, interiorborderwidth,
                             outerrelief, interiorrelief,
                             pri_background)
        self.__setBindings()


    def __setStyle(self, style, pri_background, sec_background, arrowcolor):
        '''Setup stylenames of outer frame, interior frame and verticle
           scrollbar'''
        
        style.configure('scr.TFrame', background=pri_background)
        style.configure('scrframe.Vertical.TScrollbar',
                        background=pri_background, troughcolor=sec_background,
                        arrowcolor=arrowcolor)
        style.configure('interior.TFrame', background=pri_background)

        style.map('scrframe.Vertical.TScrollbar',
            background=[('active',pri_background),('!active',pri_background)],
            arrowcolor=[('active',arrowcolor),('!active',arrowcolor)])


    def __createWidgets(self, outerborderwidth, interiorborderwidth,
                        outerrelief, interiorrelief, pri_background):
        '''Create widgets of the scroll frame.'''
        vscrollbar = ttk.Scrollbar(self,
                                   orient='vertical',
                                   style='scrframe.Vertical.TScrollbar')
        vscrollbar.pack(fill='y', side='right', expand='false')
        self.canvas = tk.Canvas(self,
                                bd=0, #no border
                                highlightthickness=0, #no focus highlight
                                yscrollcommand=vscrollbar.set,#use vscrollbar
                                background=pri_background) #improves resizing appearance
        self.canvas.pack(side='left', fill='both', expand='true')
        vscrollbar.config(command=self.canvas.yview)

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
        canvasReqWidth = self.canvas.winfo_reqwidth() #not used
        canvasReqHeight= self.canvas.winfo_reqheight()
        canvasWidth  = self.canvas.winfo_width()
        canvasHeight = self.canvas.winfo_height()

        box=self.canvas.bbox('all')
        print('box = ', box)
        print('Req = ', canvasReqWidth, canvasReqHeight)
        print('Cur = ', canvasWidth, canvasHeight)


        #Set interior frame width to canvas curent width
        self.canvas.itemconfigure(self.interior_id, width=canvasWidth)
        
        # Set interior frame height and canvas scrollregion
        if canvasHeight >= canvasReqHeight:
            self.canvas.itemconfigure(self.interior_id,  height=canvasHeight)
            self.canvas.config(scrollregion="0 0 {0} {1}".
                               format(canvasWidth, canvasHeight))
        else:
            self.canvas.itemconfigure(self.interior_id, height=canvasReqHeight)
            self.canvas.config(scrollregion="0 0 {0} {1}".
                               format(canvasWidth, canvasReqHeight))



if __name__ == "__main__":

    class SampleApp(tk.Tk):
        def __init__(self, *args, **kwargs):
            #BG0 = '#656868' #Dark scheme
            #BG1 = '#424545' #Dark scheme
            BG0 = '#aabfe0' #Blue scheme
            BG1 = '#4e88e5' #Blue scheme
            tk.Tk.__init__(self, *args, **kwargs)
            top = self.winfo_toplevel()
            top.title('VerticalScrollFrame')
            top.geometry('270x330')
            self.frame = VerticalScrollFrame(self,
                                             pri_background=BG1,
                                             sec_background=BG0,
                                             arrowcolor='white',
                                             outerborderwidth=20,
                                             interiorborderwidth=10,
                                             outerrelief='raised',
                                             interiorrelief='sunken'
                                             )
            self.frame.pack(fill='both', expand=1)
            self.label = tk.Label(background='white',
                text="Shrink the window to activate the scrollbar.")
            self.label.pack()
            buttons = []
            for i in range(10):
                buttons.append(ttk.Button(self.frame.interior,
                                          text="Button " + str(i)))
                buttons[-1].pack()

    app = SampleApp()
    app.mainloop()

