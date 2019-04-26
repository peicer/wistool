# coding: utf-8
'''
Created on 2018年9月29日

@author: lili
'''
import wx
from wx.lib import plot as wxplot
class PlotExample(wx.Panel):
    def __init__(self,parent,csize=(200,2000)):
        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY, size=csize)
        self.scroll = wx.ScrolledWindow(self, -1)
        self.scroll.SetScrollbars(2, 2, csize[0]/2, csize[1]/2)
        self.panel = wxplot.PlotCanvas(self.scroll,size=csize)
        # Edit panel-wide settings
        axes_pen = wx.Pen(wx.BLUE, 1)
        self.panel.axesPen = axes_pen
        self.panel.enableAxes = (True, True, True, True)
        self.panel.enableAxesValues = (True, True,True,False)
        self.panel.enableTicks = (True, True, True, False)
#         self.panel.showScrollbars=True
#         self.panel._ticks(20, 70, 5)
    
    
    def plot(self,xx,yy):    
        # Generate some Data
        x_data = xx
        y_data = yy

        # most items require data as a list of (x, y) pairs:
        #    [[1x, y1], [x2, y2], [x3, y3], ..., [xn, yn]]
        xy_data = list(zip(x_data, y_data))
        

        # Create your Poly object(s).
        # Use keyword args to set display properties.
        line = wxplot.PolySpline(
            xy_data,
            colour=wx.Colour(128, 128, 0),   # Color: olive
            width=1,
        )

        # create your graphics object
        graphics = wxplot.PlotGraphics([line])
        self.panel.xSpec = (50.0,125.0)
        self.panel.ySpec = (3000.0,1000.0)
       # draw the graphics object on the canvas
        self.panel.Draw(graphics)


# if __name__ == '__main__':
#     app = wx.App()
#     frame = PlotExample()
#     frame.Show()
#     app.MainLoop()