#encoding=gbk
'''
Created on 2013-12-23

@author: liang
'''
#import wx
import os
import sys
import img
from pxls import pxls
from wx.xrc import *
from wishelper import *
import wx.grid
from wx.adv import AboutDialogInfo,AboutBox
from wx.grid import Grid
from wxplot import PlotExample

TBFLAGS = ( wx.TB_HORIZONTAL
            | wx.NO_BORDER
            | wx.TB_FLAT
            | wx.TB_TEXT
            #| wx.TB_HORZ_LAYOUT
            )
class myapp(wx.App):
    def __init__(self,argv=None):
        self.fnm=None
        if argv !=None and len(argv)>1:
            self.fnm=argv[1]
#             for arg in argv:
#                 print arg
        wx.App.__init__(self)
        
    def OnInit(self):
        #self.apppath=sys.argv[0]
        self.apppath, appfilename = os.path.split(os.path.abspath(sys.argv[0]))
        #print(dirname,filename)
        if os.path.isdir(self.apppath):
            self.apppath=self.apppath+'\\'
        print(self.apppath)
        self.res=XmlResource(self.apppath+'reer.xrc')
        self.frame=self.res.LoadFrame(None,'ID_WXFRAME')
        self.frame.SetIcon(img.oszillograph.Icon)
        self.frame.SetSize((800,600))
        #self.frame.SetTitle('WIS工具')
        self.notebk=XRCCTRL(self.frame,'ID_NOTEBOOK')
        self.channelwin=XRCCTRL(self.notebk,'ID_channel')
        self.channelpanel=XRCCTRL(self.notebk,'ID_PANEL')
        self.listchannel=XRCCTRL(self.notebk,'ID_LISTBOX')
        self.listflow=XRCCTRL(self.notebk,'ID_LISTBOX1')
        self.listtable=XRCCTRL(self.notebk,'ID_LISTBOX2')
        self.viewflow=XRCCTRL(self.notebk,'ID_TEXTCTRL')
        self.viewtab=XRCCTRL(self.notebk,'ID_GRID')
        self.viewtab.EnableEditing(False)
        self.frame.Bind(wx.EVT_LISTBOX,self.showflow,id=XRCID('ID_LISTBOX1'))
        self.frame.Bind(wx.EVT_LISTBOX,self.showtable,id=XRCID('ID_LISTBOX2'))
        self.frame.Bind(wx.EVT_LISTBOX,self.showchannel,id=XRCID('ID_LISTBOX'))
        
        #self.notebk.SetPageText(0,'曲线')
        #self.notebk.SetPageText(1,'流数据')
        #self.notebk.SetPageText(2,'表数据')
        self.actch_data=None
        self.act_filename=""
        self.AddToolbar()
        dt = MyFileDropTarget(self)
        self.frame.SetDropTarget(dt)
        self.frame.Show()
        self.wish=None
        #print os.environ
        if self.fnm :
            self.openWisfile(self.fnm)

        return True
    def AddToolbar(self):
        self.toolb = self.frame.CreateToolBar(TBFLAGS)
        self.statub=self.frame.CreateStatusBar(2)
        tsize = (28,28)
        self.toolb.SetToolBitmapSize(tsize)
        #openimg=wx.Image(self.apppath+'folder.ico',wx.BITMAP_TYPE_ICO,index=5)
#         expimg=wx.Image(self.apppath+'export1.ico',wx.BITMAP_TYPE_ICO,index=5)
#         savimg=wx.Image(self.apppath+'disk_yellow.ico',wx.BITMAP_TYPE_ICO,index=5)
#         aboimg=wx.Image(self.apppath+'about.ico',wx.BITMAP_TYPE_ICO,index=5)
        openimg=img.folder.Image
        expimg=img.export1.Image
        savimg=img.disk_yellow.Image
        aboimg=img.about.Image
        
        self.toolb.AddTool(100,'打开WIS',openimg.ConvertToBitmap(),wx.NullBitmap,wx.ITEM_NORMAL,shortHelp="打开WIS文件", longHelp="打开WIS文件")
        self.tsav=self.toolb.AddTool(200,' 保存 ',savimg.ConvertToBitmap(),wx.NullBitmap,wx.ITEM_NORMAL,shortHelp="保存文件",longHelp="保存文件")
        self.toolb.AddSeparator()
        self.toolb.AddTool(300,'导出TXT',expimg.ConvertToBitmap(),wx.NullBitmap,wx.ITEM_NORMAL,shortHelp="WIS曲线导出TXT",longHelp="WIS曲线导出TXT")
        self.toolb.AddTool(400,'关于',aboimg.ConvertToBitmap(),wx.NullBitmap,wx.ITEM_NORMAL,shortHelp="关于",longHelp="关于本工具")
        self.toolb.Realize()
        
        #tb.AddTool(20, "Open", open_bmp, shortHelpString ="Open", longHelpString="Long help for 'Open'")
        self.Bind(wx.EVT_TOOL, self.OnOpenTool, id=100)
        self.Bind(wx.EVT_TOOL, self.OnSaveTool, id=200)
        self.Bind(wx.EVT_TOOL, self.OnSaveTXT, id=300)
        self.Bind(wx.EVT_TOOL, self.AboutMe, id=400)
    
    def showflow(self,evt):
        
        self.viewflow.SetValue(self.wish.readflow(evt.GetString()))
        self.toolb.SetToolShortHelp(200,u'保存流数据['+evt.GetString()+']')
        #sav=self.toolb.FindById(200)
        #self.tsav.SetLabel('保存流数据['+evt.GetString()+']')
        #self.toolb.Realize()
        
    def showtable(self,evt):
        self.viewtab.ClearGrid()
        tabdata=self.wish.readtable(evt.GetString())
        print (len(tabdata[0]))
        if len(tabdata[0])>0: 
    
            gtable=CustomDataTable()
            gtable.colLabels=tabdata[0]
            gtable.data=tabdata[1:]
            self.viewtab.SetTable(gtable,True)
            self.viewtab.ForceRefresh()
            self.toolb.SetToolShortHelp(200,u'保存表数据['+evt.GetString()+']')
            #self.toolb.FindById(200).SetLabel('保存表数据['+evt.GetString()+']')
            #self.toolb.Realize()
    def showchannel(self,evt):
        self.createchannelwin(evt.GetString())
            
    def createchannelwin(self,chn):
        newspwin=wx.SplitterWindow(self.channelwin,wx.ID_ANY,style=wx.SP_3DBORDER|wx.SP_3DSASH|wx.NO_BORDER)
        xgrid=Grid(newspwin,wx.ID_ANY,style=wx.SUNKEN_BORDER)
        xgrid.SetRowLabelSize(0)
        xtable=CustomDataTable()
        xtable.colLabels=['深度',chn]
        xx,yy=self.wish.readchannel(chn)
        self.actch_data=(xx,yy)
        xtable.data=list(zip(xx[:500],yy[:500]))
        xgrid.SetTable(xtable,True)
        xgrid.ForceRefresh()
        
        
        xpan=wx.Panel(newspwin,wx.ID_ANY,style=wx.SUNKEN_BORDER)
        self.toolb.SetToolShortHelp(200,u'保存曲线数据['+chn+']')
        mpl=PlotExample(xpan,(400,4000))
        mpl.plot(yy, xx)
#         mpl.Show()
        
#         MPL=MPL_Panel_base(xpan,(400,4000))
#         
#         #MPL.Figure.set_figheight(20)
#         #MPL.set_psize(500, 3000)
#         #MPL.xticker(10.0,2.0)
        BoxSizer=wx.BoxSizer(wx.VERTICAL) 
        BoxSizer.Add(mpl,proportion =1, border = 1,flag = wx.ALL|wx.EXPAND)
        xpan.SetSizer(BoxSizer)
        xpan.Fit()
#         MPL.cla()
#         MPL.plot(yy,xx,'red')
#         MPL.yticker(50.0, 25.0)
#         MPL.xticker(10, 5)
#         MPL.xlim(50,150)
#         MPL.ylim(4000, 1000)
#         MPL.grid()
#         dd=MPL.pl.gca().xaxis
        #dd.set_label_position('top')
#         MPL.UpdatePlot()

        #MPL.Update()
        #wx.StaticText(xpan, -1, chn, (5,5))
        
        newspwin.SetMinimumPaneSize(20)
        newspwin.SplitVertically(xgrid, xpan, 180)
        old=self.channelwin.GetWindow2()
        self.channelwin.ReplaceWindow(old,newspwin)
        old.Destroy()
        newspwin.Show(True)
    def OnOpenTool(self,evt):
        filDlg=wx.FileDialog(self.frame,'选择WIS文件',wildcard="WIS文件 (*.wis)|*.wis")
        if filDlg.ShowModal()==wx.ID_OK:
            self.act_filename=filDlg.GetPath()
            self.openWisfile(self.act_filename)
        filDlg.Destroy()
    def OnSaveTool(self,evt):
        pg=self.notebk.GetSelection()
        if pg==1:
           stda=self.viewflow.GetValue()
           filDlg=wx.FileDialog(self.frame,'保存流',defaultFile=self.listflow.GetStringSelection(),wildcard="TXT文件 (*.txt)|*.txt",style = wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
           if filDlg.ShowModal()==wx.ID_OK:
                flname=filDlg.GetPath()
                if not os.path.splitext(flname)[1]: #如果没有文件名后缀
                     flname = flname + '.txt'
                self.SaveFile(flname,stda)
           filDlg.Destroy()
        elif pg==2:
            tabdata={}
            for tab in self.listtable.Strings:
               tabdata[tab]=self.wish.readtable(tab)
               
            filDlg=wx.FileDialog(self.frame,'保存表',defaultFile='table',wildcard="Excel文件 (*.xls)|*.xls",style = wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
            if filDlg.ShowModal()==wx.ID_OK:
                flname=filDlg.GetPath()
                if not os.path.splitext(flname)[1]: #如果没有文件名后缀
                    flname = flname + '.xls'
                pxls.savedata(flname, tabdata)
            filDlg.Destroy()
        else:
            tabdata={}
            chn=self.listchannel.GetStringSelection()
            if self.actch_data:
                tabdata[chn]=list(zip(self.actch_data[0],self.actch_data[1]))
                tabdata[chn].insert(0, ('深度',chn))
                
            filDlg=wx.FileDialog(self.frame,'保存通道',defaultFile=chn,wildcard="Excel文件 (*.xls)|*.xls",style = wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
            if filDlg.ShowModal()==wx.ID_OK:
                flname=filDlg.GetPath()
                if not os.path.splitext(flname)[1]: #如果没有文件名后缀
                    flname = flname + '.xls'
                pxls.savedata(flname, tabdata)
            filDlg.Destroy()            

           
    def SaveFile(self,fn,st):
        f = open(fn, 'w')
        f.write(st)
        f.close()
                
    def OnSaveTXT(self,evt):
        if self.wish :
            self.wish.channel2txt(os.path.splitext(self.act_filename)[0]+'.txt')
    def AboutMe(self,evt):
        info=AboutDialogInfo()
        info.SetName("测井WIS查看小工具")
        info.SetVersion("1.0 Beta")
        info.SetDescription("此工具用于测井WIS格式文件的查看，可导出曲线和其它参数数据.")
        info.SetCopyright("(C) 2014 liliang <ll4_cq@petrochina.com.cn>")
        AboutBox(info)

    def openWisfile(self,finame):
        self.wish=wishelper(open(finame,"rb"))
        print (self.wish.headerinfo)
        print ([xx for xx in self.wish.flowlist])
        self.listflow.Set(sorted(self.wish.flowlist.keys()))
        self.listchannel.Set(sorted(self.wish.channellist.keys()))
        self.listtable.Set(sorted(self.wish.tablelist.keys()))
        #print self.wish.tablelist
    def setgridlabel(self,labs):
        y=0
        for lv in labs:
             self.viewtab.SetColLabelValue(y,lv)
             y=y+1    
             

class CustomDataTable(wx.grid.GridTableBase):
    def __init__(self):
        wx.grid.GridTableBase.__init__(self)
        self.colLabels = []
        self.data = []
  
    #--------------------------------------------------
    # required methods for the wxPyGridTableBase interface

    def GetNumberRows(self):
        return len(self.data) 

    def GetNumberCols(self):
        return len(self.data[0])

    def IsEmptyCell(self, row, col):
        try:
            return not self.data[row][col]
        except IndexError:
            return True

    # Get/Set values in the table.  The Python version of these
    # methods can handle any data-type, (as long as the Editor and
    # Renderer understands the type too,) not just strings as in the
    # C++ version.
    def GetValue(self, row, col):
        try:
            return self.data[row][col]
        except IndexError:
            return ''

    def SetValue(self, row, col, value):
        def innerSetValue(row, col, value):
            try:
                if value==None:
                    value=''
                self.data[row][col] = value
            except IndexError:
                # add a new row
                self.data.append([''] * self.GetNumberCols())
                innerSetValue(row, col, value)

                # tell the grid we've added a row
                msg = wx.grid.GridTableMessage(self,            # The table
                        wx.grid.GRIDTABLE_NOTIFY_ROWS_APPENDED, # what we did to it
                        1                                       # how many
                        )

                self.GetView().ProcessTableMessage(msg)
        innerSetValue(row, col, value) 

    #--------------------------------------------------
    # Some optional methods
    # Called when the grid needs to display labels
    def GetColLabelValue(self, col):
        return self.colLabels[col]
            
class MyFileDropTarget(wx.FileDropTarget):
    def __init__(self, window):
        wx.FileDropTarget.__init__(self)
        self.window = window

    def OnDropFiles(self, x, y, filenames):
#         print filenames
        for file in filenames:
            self.window.openWisfile(file)
            
                    
if __name__ == '__main__':
    app = myapp(sys.argv)
    app.MainLoop()