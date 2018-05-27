import tkinter
import tkinter.ttk
import tkinter as tk


class VSFrame(tk.Frame):
    """A pure Tkinter scrollable frame that actually works!
    * Use the 'interior' attribute to place widgets inside the scrollable frame
    * Construct and pack/place/grid normally
    * This frame only allows vertical scrolling

    """
    def __init__(self, parent,fheight = 200, width = 330, *args, **kw):
        self.parent = parent
        tk.Frame.__init__(self, parent, *args, **kw)

        # create a canvas object and a vertical scrollbar for scrolling it
        vscrollbar = tk.Scrollbar(self, orient=tk.VERTICAL)

        vscrollbar.pack(fill=tk.Y, side=tk.RIGHT, expand=tk.FALSE)
        canvas = tk.Canvas(self,
            bd = 0, 
            highlightthickness = 0,
            yscrollcommand=vscrollbar.set,
            height = fheight,
            width = width,
            background = "black"
        )
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.TRUE)
        vscrollbar.config(command=canvas.yview)

        # reset the view
        canvas.xview_moveto(0)
        canvas.yview_moveto(0)

        # create a frame inside the canvas which will be scrolled with it
        self.interior = interior = tk.Frame(canvas,bg = "black",width = width)
        interior_id = canvas.create_window(0, 0, window=interior,
                                           anchor=tk.NW)


        # track changes to the canvas and frame width and sync them,
        # also updating the scrollbar
        def _configure_interior(event):
            ''' TODO Internal Function Description
            '''
            # update the scrollbars to match the size of the inner frame
            size = (interior.winfo_reqwidth(), interior.winfo_reqheight())
            canvas.config(scrollregion="0 0 %s %s" % size)
            if interior.winfo_reqwidth() != canvas.winfo_width():
                # update the canvas's width to fit the inner frame
                canvas.config(width=interior.winfo_reqwidth())
                
        interior.bind('<Configure>', _configure_interior)


        def _configure_canvas(event):
            ''' TODO Internal Function Description
            '''
            if interior.winfo_reqwidth() != canvas.winfo_width():
                # update the inner frame's width to fill the canvas
                canvas.itemconfigure(interior_id, width=canvas.winfo_width())
                
        canvas.bind('<Configure>', _configure_canvas)


        def _scrollwheel(event):
            ''' TODO Internal Function Description
            '''
            print("caught scroll",event.widget)
            return 'break'

        vscrollbar.bind('<Button-4>', _scrollwheel)
        vscrollbar.bind('<Button-5>', _scrollwheel)
