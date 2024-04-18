#!/usr/bin/python3
# -*- coding: utf-8 -*-

import tkinter as tk
import tkinter.ttk as ttk
import platform

__all__ = ["AutoScrollbar", "VerticalScrollFrame"]


class AutoScrollbar(ttk.Scrollbar):
    """
    class created on 08 August 1998 by Fredrik Lundh
    http://effbot.org/zone/tkinter-autoscrollbar.htm

    I added the following Virtual Events to this widget:
    "<<AutoScrollbarOn>>"
    "<<AutoScrollbarOff>>"
    """
    # a scrollbar that hides itself if it's not needed.  only
    # works if used with the .Grid geometry manager.
    def set(self, lo, hi):
        if float(lo) <= 0.0 and float(hi) >= 1.0:
            self.tk.call("grid", "remove", self)
            # I added next line
            self.after_idle(self.event_generate, "<<AutoScrollbarOff>>")
        else:
            self.grid()
            # I added next line
            self.after_idle(self.event_generate, "<<AutoScrollbarOn>>")
        ttk.Scrollbar.set(self, lo, hi)

    def pack(self, **kw):
        raise tk.TclError("cannot use pack with this widget")

    def place(self, **kw):
        raise tk.TclError("cannot use place with this widget")


class VerticalScrollFrame(ttk.Frame):
    """A custom widget allowing mainly vertical scrolling of its
    contents when a mouse pointer is found within it or its vertical
    scrollbar. Horizontal scrolling is allowed only when the mouse pointer is
    located within its horizontal scrollbar. Scrolling is achieved by
    rotating the mousewheel.

    Contents/widgets that are to grid, pack or placed inside this widget must
    be located inside its '.interior' attribute (which is a ttk.Frame
    widget).

    Generated Virtual Events:
    "<<VSFCanvasScrolledUp>>"    - whenever .canvas scrolls up
    "<<VSFCanvasScrolledDown>>"  - whenever .canvas scrolls down
    "<<VSFCanvasScrolledLeft>>"  - whenever .canvas scrolls left
    "<<VSFCanvasScrolledRight>>" - whenever .canvas scrolls right
    """

    def __init__(self, master, **options):
        """
        WIDGET-SPECIFIC OPTIONS:
           style, background, cbackground, ibackground, troughcolor, arrowcolor,
           mainborderwidth, interiorborderwidth, mainrelief, interiorrelief 
        """
        # Extract key and value from **options using Python3 "pop" function:
        #   pop(key[, default])
        style = options.pop('style', ttk.Style())
        background = options.pop('background', '#E4E4E4')
        cbackground = options.pop('cbackground', '#E4E4E4')
        ibackground = options.pop('ibackground', '#E4E4E4')
        troughcolor = options.pop('troughcolor', 'white')
        arrowcolor = options.pop('arrowcolor', 'black')
        mainborderwidth = options.pop('mainborderwidth', 0)
        interiorborderwidth = options.pop('interiorborderwidth', 0)
        mainrelief = options.pop('mainrelief', 'flat')
        interiorrelief = options.pop('interiorrelief', 'flat')

        def _set_style():
            """Setup stylenames of outer frame, interior frame and vertical
            scrollbar."""
            style.configure('main.TFrame', background=background)
            style.configure('interior.TFrame', background=ibackground)
            style.configure('canvas.Vertical.TScrollbar',
                            background=cbackground, troughcolor=troughcolor,
                            arrowcolor=arrowcolor)
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

        ttk.Frame.__init__(self, master, style='main.TFrame',
                           borderwidth=mainborderwidth, relief=mainrelief)
        _set_style()
        self._create_widgets(interiorborderwidth, interiorrelief, cbackground)
        self._set_bindings()

    def _create_widgets(self, interiorborderwidth, interiorrelief, background):
        """Create widgets of the scroll frame."""
        self.vscrollbar = AutoScrollbar(
            self, orient='vertical', style='canvas.Vertical.TScrollbar')
        self.hscrollbar = AutoScrollbar(
            self, orient='horizontal', style='canvas.Horizontal.TScrollbar')
        self.canvas = tk.Canvas(
            self,
            bd=0,  # no border
            highlightthickness=0,  # no focus highlight
            yscrollcommand=self.vscrollbar.set,  # use self.vscrollbar
            xscrollcommand=self.hscrollbar.set,  # use self.hscrollbar
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
        hscrollbar = self.hscrollbar
        system = platform.system()

        def _configure_interior(event):
            # print(f"\ndef _configure_interior(event):")
            # update the scrollbars to match the size of the inner frame
            canvas.config(scrollregion=(0, 0, interior.winfo_reqwidth(),
                                        interior.winfo_reqheight()))
            if interior.winfo_reqwidth() != canvas.winfo_width():
                # update the canvas's width to fit the inner frame
                canvas.config(width=interior.winfo_reqwidth())
                self.update_idletasks()

        def _configure_canvas(event):
            # print(f"\ndef _configure_canvas(event):")
            if interior.winfo_reqwidth() != canvas.winfo_width():
                # update the inner frame's width to fill the canvas
                maxwidth = max([event.width, canvas.winfo_reqwidth()])
                canvas.itemconfigure(interior_id, width=maxwidth)
                self.update_idletasks()

        def _bind_vscrollbar_to_mousewheel_linuxos(event):

            def scrollup(e):
                canvas.yview_scroll(-1, 'units')
                canvas.after_idle(canvas.event_generate,
                                  "<<VSFCanvasScrolledUp>>")

            def scrolldown(e):
                canvas.yview_scroll(1, 'units')
                canvas.after_idle(canvas.event_generate,
                                  "<<VSFCanvasScrolledDown>>")

            canvas.bind_all('<Button-4>', scrollup)
            canvas.bind_all('<Button-5>', scrolldown)

        def _unbind_vscrollbar_to_mousewheel_linuxos(event):
            canvas.unbind_all(sequence="<Button-4>")
            canvas.unbind_all(sequence="<Button-5>")

        def _bind_vscrollbar_to_mousewheel_macos(event):

            def scrollupdown(ev):
                canvas.yview_scroll(int(-1 * ev.delta), "units")
                if ev.delta < 0:
                    canvas.after_idle(canvas.event_generate,
                                      "<<VSFCanvasScrolledDown>>")
                elif ev.delta > 0:
                    canvas.after_idle(canvas.event_generate,
                                      "<<VSFCanvasScrolledUp>>")

            canvas.bind_all('<MouseWheel>', scrollupdown)

        def _bind_vscrollbar_to_mousewheel_winos(event):

            def scrollupdown(ev):
                canvas.yview_scroll(int(-1 * ev.delta/120), "units")
                if ev.delta < 0:
                    canvas.after_idle(canvas.event_generate,
                                      "<<VSFCanvasScrolledDown>>")
                elif ev.delta > 0:
                    canvas.after_idle(canvas.event_generate,
                                      "<<VSFCanvasScrolledUp>>")

            canvas.bind_all('<MouseWheel>', scrollupdown)

        def _unbind_vscrollbar_from_mousewheel(event):
            canvas.unbind_all("<MouseWheel>")

        def _bind_hscrollbar(event):

            if system in ["Linux"]:
                hscrollbar.bind('<Enter>',
                                _bind_hscrollbar_to_mousewheel_linuxos)
                hscrollbar.bind('<Leave>',
                                _unbind_hscrollbar_from_mousewheel_linuxos)
            elif system in ["Darwin"]:
                hscrollbar.bind('<Enter>',
                                _bind_hscrollbar_to_mousewheel_macos)
                hscrollbar.bind('<Leave>',
                                _unbind_hscrollbar_from_mousewheel)
            elif system in ["Windows"]:
                hscrollbar.bind('<Enter>',
                                _bind_hscrollbar_to_mousewheel_winos)
                hscrollbar.bind('<Leave>',
                                _unbind_hscrollbar_from_mousewheel)

        def _unbind_hscrollbar(event):
            hscrollbar.unbind('<Enter>')
            hscrollbar.unbind('<Leave>')

        def _bind_hscrollbar_to_mousewheel_linuxos(event):

            def scrollleft(e):
                canvas.xview_scroll(1, 'units')
                canvas.after_idle(canvas.event_generate,
                                  "<<VSFCanvasScrolledLeft>>")

            def scrollright(e):
                canvas.xview_scroll(-1, 'units')
                canvas.after_idle(canvas.event_generate,
                                  "<<VSFCanvasScrolledRight>>")

            canvas.bind_all('<Button-4>', scrollright)
            canvas.bind_all('<Button-5>', scrollleft)

        def _bind_hscrollbar_to_mousewheel_macos(event):

            def scroll_xsb(ev):
                print(f"{ev.widget=} {ev.delta=} {ev.num=}")
                canvas.xview_scroll(int(-1 * ev.delta), "units")

            event.widget.bind("<MouseWheel>", scroll_xsb)

        def _bind_hscrollbar_to_mousewheel_winos(event):

            def scroll_xsb(ev):
                print(f"{ev.widget=} {ev.delta=} {ev.num=}")
                canvas.xview_scroll(int(-1 * ev.delta/120), "units")

            event.widget.bind("<MouseWheel>", scroll_xsb)

        def _unbind_hscrollbar_from_mousewheel(event):
            hscrollbar.unbind_all("<MouseWheel>")

        def _unbind_hscrollbar_from_mousewheel_linuxos(event):
            hscrollbar.unbind_all("<Button-4>")
            hscrollbar.unbind_all("<Button-5>")

        # Bindings for configure events
        interior.bind('<Configure>', _configure_interior)
        canvas.bind('<Configure>', _configure_canvas)

        # Bindings for vertical scrolling of canvas and vscrollbar
        if system in ["Linux"]:
            canvas.bind('<Enter>', _bind_vscrollbar_to_mousewheel_linuxos)
            canvas.bind('<Leave>', _unbind_vscrollbar_to_mousewheel_linuxos)
        elif system in ["Darwin"]:
            canvas.bind('<Enter>', _bind_vscrollbar_to_mousewheel_macos)
            canvas.bind('<Leave>', _unbind_vscrollbar_from_mousewheel)
        elif system in ["Windows"]:
            canvas.bind('<Enter>', _bind_vscrollbar_to_mousewheel_winos)
            canvas.bind('<Leave>', _unbind_vscrollbar_from_mousewheel)

        # Bindings for vertical scrolling
        hscrollbar.bind("<<AutoScrollbarOn>>", _bind_hscrollbar)
        hscrollbar.bind("<<AutoScrollbarOff>>", _unbind_hscrollbar)


class Example(ttk.Frame):

    def __init__(self, master):
        bg0 = '#aabfe0'  # Blue scheme
        bg1 = '#4e88e5'  # Blue scheme

        super().__init__(master)
        self.master = master
        self.master.title('VerticalScrollFrame')
        self.master.geometry('300x350')
        self.frame = None
        self.label = None
        self.textbox = None
        self.create_widgets(bg0, bg1)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

    def create_widgets(self, bg0, bg1):
        self.frame = VerticalScrollFrame(self,
                                         background=bg1,
                                         troughcolor=bg0,
                                         arrowcolor='white',
                                         scrollbarcolor="grey",
                                         mainborderwidth=10,
                                         interiorborderwidth=10,
                                         mainrelief='raised',
                                         interiorrelief='sunken'
                                         )
        self.frame.grid(row=0, column=0, sticky='nsew')

        text = "Shrink the window to activate the scrollbar."
        self.label = tk.Label(background='white', text=text)
        self.label.grid(row=1, column=0, sticky='nsew')

        buttons = []
        for i in range(10):
            buttons.append(ttk.Button(self.frame.interior,
                                      text="Button " + str(i)))
            buttons[-1].grid(row=i, column=0, sticky='nsew')

        self.textbox = tk.Text(self.frame.interior,
                               width=30,
                               height=8,
                               foreground='white',
                               background='grey',
                               borderwidth=3,
                               relief='sunken')
        self.textbox.grid(row=1, column=0, sticky='nsew')


if __name__ == '__main__':
    root = tk.Tk()
    app = Example(root)
    app.grid(row=0, column=0, sticky='nsew')
    root.rowconfigure(0, weight=1)
    root.columnconfigure(0, weight=1)
    root.mainloop()
