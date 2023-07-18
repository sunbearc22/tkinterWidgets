#!/usr/bin/python3
# -*- coding: utf-8 -*-

import tkinter as tk
import tkinter.ttk as ttk
import platform


class AutoScrollbar(ttk.Scrollbar):
    """
    class created on 08 August 1998 by Fredrik Lundh
    http://effbot.org/zone/tkinter-autoscrollbar.htm
    """
    # a scrollbar that hides itself if it's not needed.  only
    # works if used with the .Grid geometry manager.
    def set(self, lo, hi):
        if float(lo) <= 0.0 and float(hi) >= 1.0:
            self.tk.call("grid", "remove", self)
        else:
            self.grid()
        ttk.Scrollbar.set(self, lo, hi)

    def pack(self, **kw):
        raise tk.TclError("cannot use pack with this widget")

    def place(self, **kw):
        raise tk.TclError("cannot use place with this widget")


class VerticalScrollFrame(ttk.Frame):
    """A ttk frame allowing vertical scrolling only.
    Use the '.interior' attribute to place widgets inside the scrollable frame.
    """

    def __init__(self, parent, **options):
        """
        WIDGET-SPECIFIC OPTIONS:
           style, background, troughcolor, arrowcolor,
           mainborderwidth, interiorborderwidth, mainrelief, interiorrelief 
        """
        # Extract key and value from **options using Python3 "pop" function:
        #   pop(key[, default])
        style = options.pop('style', ttk.Style())
        background = options.pop('background', 'light grey')
        troughcolor = options.pop('troughcolor', 'grey70')
        arrowcolor = options.pop('arrowcolor', 'black')
        mainborderwidth = options.pop('mainborderwidth', 0)
        interiorborderwidth = options.pop('interiorborderwidth', 0)
        mainrelief = options.pop('mainrelief', 'flat')
        interiorrelief = options.pop('interiorrelief', 'flat')

        def _set_style():
            """Setup stylenames of outer frame, interior frame and vertical
            scrollbar."""
            style.configure('main.TFrame', background=background)
            style.configure('interior.TFrame', background=background)
            style.configure('canvas.Vertical.TScrollbar', background=background,
                            troughcolor=troughcolor, arrowcolor=arrowcolor)
            style.configure('canvas.Horizontal.TScrollbar',
                            background=background,
                            troughcolor=troughcolor, arrowcolor=arrowcolor)
            style.map('canvas.Vertical.TScrollbar',
                      background=[('active', background),
                                  ('!active', background)],
                      arrowcolor=[('active', arrowcolor),
                                  ('!active', arrowcolor)])
            style.map('canvas.Horizontal.TScrollbar',
                      background=[('active', background),
                                  ('!active', background)],
                      arrowcolor=[('active', arrowcolor),
                                  ('!active', arrowcolor)])

        ttk.Frame.__init__(self, parent, style='main.TFrame',
                           borderwidth=mainborderwidth, relief=mainrelief)
        _set_style()
        self._create_widgets(interiorborderwidth, interiorrelief, background)
        self._set_bindings()

    def _create_widgets(self, interiorborderwidth, interiorrelief, background):
        """Create widgets of the scroll frame."""
        self.vscrollbar = AutoScrollbar(self, orient='vertical',
                                        style='canvas.Vertical.TScrollbar')
        self.hscrollbar = AutoScrollbar(self, orient='horizontal',
                                        style='canvas.Horizontal.TScrollbar',
                                        )
        self.canvas = tk.Canvas(self,
                                bd=0,  # no border
                                highlightthickness=0,  # no focus highlight
                                yscrollcommand=self.vscrollbar.set,  # use self.vscrollbar
                                xscrollcommand=self.hscrollbar.set,  # use self.vscrollbar
                                background=background  # improves resizing appearance
                                )
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.canvas.grid(row=0, column=0, sticky='nsew')
        self.vscrollbar.grid(row=0, column=1, sticky='nsew')
        self.hscrollbar.grid(row=1, column=0, sticky='nsew')
        self.vscrollbar.config(command=self.canvas.yview)
        self.hscrollbar.config(command=self.canvas.xview)

        # reset the view
        self.canvas.xview_moveto(0)
        self.canvas.yview_moveto(0)

        # create a frame inside the canvas which will be scrolled with it
        self.interior = ttk.Frame(self.canvas,
                                  style='interior.TFrame',
                                  borderwidth=interiorborderwidth,
                                  relief=interiorrelief,
                                  )
        self.interior_id = self.canvas.create_window(0, 0,
                                                     window=self.interior,
                                                     anchor='nw',
                                                     tags='interior',
                                                     )

    def _set_bindings(self):
        """Activate binding to configure scroll frame widgets."""
        # Internal parameters
        interior = self.interior
        canvas = self.canvas
        interior_id = self.interior_id

        def _configure_interior(event):
            # update the scrollbars to match the size of the inner frame
            canvas.config(scrollregion=(0, 0, interior.winfo_reqwidth(),
                                        interior.winfo_reqheight())
                          )
            if interior.winfo_reqwidth() != canvas.winfo_width():
                # update the canvas's width to fit the inner frame
                canvas.config(width=interior.winfo_reqwidth())

        def _configure_canvas(event):
            if interior.winfo_reqwidth() != canvas.winfo_width():
                # update the inner frame's width to fill the canvas
                canvas.itemconfigure(interior_id, width=canvas.winfo_reqwidth())

        def _bind_to_mousewheel_linuxos(event):
            canvas.bind_all(
                sequence='<Button-4>',
                func=lambda event: canvas.yview_scroll(-1, 'units'),
            )
            canvas.bind_all(
                sequence='<Button-5>',
                func=lambda event: canvas.yview_scroll(1, 'units'),
            )

        def _unbind_from_mousewheel_linuxos(event):
            canvas.unbind_all(sequence="<Button-4>")
            canvas.unbind_all(sequence="<Button-5>")

        def _bind_to_mousewheel_winos(event):
            canvas.bind_all(
                sequence="<MouseWheel>",
                func=canvas.yview_scroll(int(-1*(event.delta/120)), "units"))

        def _unbind_from_mousewheel_winos(event):
            canvas.unbind_all(sequence="<MouseWheel>")

        interior.bind('<Configure>', _configure_interior)
        canvas.bind('<Configure>', _configure_canvas)
        system = platform.system()
        if system in ["Linux"]:
            canvas.bind('<Enter>', _bind_to_mousewheel_linuxos)
            canvas.bind('<Leave>', _unbind_from_mousewheel_linuxos)
        elif system in ["Windows"]:
            canvas.bind('<Enter>', _bind_to_mousewheel_winos)
            canvas.bind('<Leave>', _unbind_from_mousewheel_winos)
