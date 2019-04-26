#encoding=gb18030
from struct import *
import numpy as np
import re
import xml.etree.cElementTree as ET 
#import simplejson
'''
Created on 2013-12-8

@author: liang
'''

class wishelper:
    '''
    classdocs
    wis File read and write 
    '''
    def __init__(self, fs):
        '''
        Constructor
        '''
        self.datatype='IhlfdsHL'
        self.headfmt="4H4L32s"   #wis文件头信息wis head
        self.objentryfmt="16sl2h4L32s" #对象入口信息object enter
        self.channlefmt="8s16s16s2H2f2H"     #通道信息结构
        self.channle_dimfmt="8s8s16s2f3L2H"  #通道维信息结构
        self.fhd=fs
        self.headerinfo=self.get_header()
        self.get_objectinfo()

    def get_header(self):
        self.fhd.seek(10)
        buff=self.fhd.read(calcsize(self.headfmt))
        hfields=list(unpack(self.headfmt, buff))
        hfields.pop(-1)
        hdinfo={'MachineType':hfields[0],
               'MaxObjectNumber':hfields[1],
               'ObjectNumber':hfields[2],
               'BlockLen':hfields[3],
               'EntryOffset':hfields[4],
               'DataOffset':hfields[5],
               'TimeCreate':hfields[6],
               }
        return hdinfo
        
    def get_objectinfo(self):
        rs1=calcsize(self.objentryfmt)
        self.objlist=[]    #
        self.tablelist={}  #表对象
        self.flowlist={}   #流对象
        self.channellist={}   #通道
        self.channelinfo={} 
        self.tableinfo={} 
        self.flowinfo={} 
        #constmap={}  #常数对象
        for i in range(self.headerinfo['ObjectNumber']):
            self.fhd.seek(rs1*i + self.headerinfo['EntryOffset'])
            buff=self.fhd.read(rs1)
            fields=list(unpack(self.objentryfmt, buff))
            if fields[2]==0:continue
#             print(type(fields[0]))
            dfsss=fields[0].decode('gb18030','ignore').split('\x00')[0] #2019.3.15 曲线名称取空格前面的字符
            fields[0]=dfsss
            if len(fields[0])==0:continue
            fields.pop(-1)
            self.objlist.append(fields)
#             print (fields)
            if fields[2]==1:
#                 fields[4]=fields[4].decode()
#                 print(fields)
                self.channellist[fields[0]]=fields
                self.channelinfo[fields[0]]=self.getchannelinfo(fields[0])
#                 print(self.getchannelinfo(fields[0]))
            if fields[2]==2:
                self.tablelist[fields[0]]=fields
                self.tableinfo[fields[0]]=self.gettabinfo(fields[0])
            if fields[2]==3:
                self.flowlist[fields[0]]=fields
                self.flowinfo[fields[0]]=self.getflowinfo(fields[0])
    
    def gettabs(self):
        return self.tablelist
    def getchanels(self):
        return self.channellist
    def getflows(self):
        return self.flowlist
    
    def get_tabsinfo(self):
        return self.tableinfo
    def get_flowsinfo(self):
        return self.flowinfo    
    def get_channelsinfo(self):
        return self.channelinfo
    def get_depth(self):
        if 'ac' in self.channelinfo.keys():
            return [round(x) for x in self.channelinfo['ac'][3:5]]
        elif 'AC' in self.channelinfo.keys():
            return [round(x) for x in self.channelinfo['AC'][3:5]]
        else:
            return [0,0]
    def trimx(self,ls,po):
#         print(ls)
        return [xx[:xx.find(b'\x00')] for xx in ls[:po]]+ls[po:]
        
    def trim0(self,ls):
#         print(ls)
        return [xx.decode('gb18030','ignore').replace('\x00', '') if type(xx)==bytes else xx for xx in ls]
    def readflow(self,fname):
        '''
        读流对象-解释结论\井斜数据
        '''
        #print self.flowlist[fname]
        self.fhd.seek(self.flowlist[fname][4])    
        fmt="L"
        #print "read to " +str(self.flowlist[fname][4])
        rscx=calcsize(fmt)
        bff=self.fhd.read(rscx)
        flen,=list(unpack(fmt, bff))
        fmt=str(flen) +"s"
        self.fhd.seek(self.flowlist[fname][4]+rscx)
        bff=self.fhd.read(calcsize(fmt))
        fstr,=list(unpack(fmt, bff))
        return fstr.decode('gb18030','ignore')
    
    
    def rptconfig(self,fp,rptname):
        tree = ET.parse(fp)
        root=tree.getroot()
        tmm=self.readflow(rptname)
#         print(tmm)
        if len(tmm)<=10:
            return None
        try:
            sd=tmm.split('\r\n')
    #         print sd
            if len(sd[0])==0:
                return None
            for rpt in root.findall('Format[@RptName="'+rptname+'"]'): 
                if len(rpt.findall('Flag'))>0:
                    bmatch=True
    #                 print (rpt.get('FormatName'),rpt.get('TableName'),rpt.get('StartRow'))
                    for flag in rpt.findall('Flag'):
    #                     print (flag.get('Data'))
    #                     print (sd[int(flag.get('Row'))-1])
                        if sd[int(flag.get('Row'))-1].find(flag.get('Data'),int(flag.get('Col'))-1)==-1:
                            bmatch=False
                            break
                    if bmatch==True:
                        zdd=[]
                        for zd in rpt.findall('Field'):
                            zdd.append([zd.get('Name'),zd.get('StartCol'),zd.get('Width')])
    #                     print (rpt.get('FormatName'))
                        return rpt,zdd
        except Exception as exc:
            return None

    
    def analysis_rpt(self,key,starr,zdd):
        #result={}                    
        #for key in self.flowlist.keys():
            if(key.upper().find('RPT_')==0):
                #rpt=self.rptconfig('resultrpt.cfg', key)
#                 zdd=[]
#                 for zd in rpt.findall('Field'):
#                     zdd.append([zd.get('Name'),zd.get('StartCol'),zd.get('Width')]) 
                #print zdd
                #starr=int(rpt.get('StartRow'))-1
                tmm=self.readflow(key)
                rpttxt=tmm.split('\r\n')[starr:]
                restrpt=[]
                vals ={}
                for rw in rpttxt:
                    if rw.find('-'*10)==0:
                        if len(vals.values())>0:
                            restrpt.append(vals)
                        vals = {}
                        continue
                    if rw.find('最大值')>0:continue
                    #print rw
                    for fld in zdd:
                        tm=rw[int(fld[1])-1 : int(fld[1])-1 + int(fld[2])].strip()
                        
                        if len(tm)>0:  
                            vals[fld[0]]=tm
                        
                    
                        
                return restrpt        
                #result[key]=restrpt
                    
        #return result              
            
    def getflowinfo(self,rnm):
        self.fhd.seek(self.flowlist[rnm][4])    
        fmt="L"
        #print "read to " +str(self.flowlist[fname][4])
        rscx=calcsize(fmt)
        bff=self.fhd.read(rscx)
        flen,=list(unpack(fmt, bff))
        return [self.flowlist[rnm][0],self.flowlist[rnm][4],flen]
        
    def getchannelinfo(self,rnm):
        self.fhd.seek(self.channellist[rnm][4])
        rsc=calcsize(self.channlefmt)
        bff=self.fhd.read(rsc)
#         print ("通道信息",self.trimx(fdac,3)
        fdac=self.trimx(list(unpack(self.channlefmt, bff)),3)
        dimens=fdac[-1]
        rscd=calcsize(self.channle_dimfmt)
        bff=self.fhd.read(rscd)
        fdacm=list(unpack(self.channle_dimfmt, bff))
#         print '维信息',self.trimx(fdacm,3) 
        return [self.channellist[rnm][0],self.channellist[rnm][4],fdac[0].decode('gb18030','ignore'),round(fdacm[3],3),round(fdacm[3],3)+fdacm[5]*float(fdacm[4]),float(fdacm[4]),dimens]
        
    
    def gettabinfo(self,rnm):
        self.fhd.seek(self.tablelist[rnm][4])
        channlefmt="2L"          #表信息
        rsc=calcsize(channlefmt)
        bff=self.fhd.read(rsc)
        if len(bff)<rsc:
            return [self.tablelist[rnm][0],self.tablelist[rnm][4],0,0]
        fdac=list(unpack(channlefmt, bff))
        return [self.tablelist[rnm][0],self.tablelist[rnm][4],fdac[0],fdac[1]]
    
    def readchannel(self,rnm):
        obji=rnm
        print ("通道：" , self.channellist[obji])
        self.fhd.seek(self.channellist[obji][4])
        #channlefmt="8s16s16s2H2f2H"
        rsc=calcsize(self.channlefmt)
        bff=self.fhd.read(rsc)
        fdac=list(unpack(self.channlefmt, bff))
        print ("通道信息",self.trimx(fdac,3))
        #channle_dimfmt="8s8s16s2f3L2H"
        rscd=calcsize(self.channle_dimfmt)
        #print wisfile.tell()
        #wisfile.seek(rsc,os.SEEK_CUR)#紧接着下一位不用seek
        bff=self.fhd.read(rscd)
        fdacm=list(unpack(self.channle_dimfmt, bff))
        print ('维信息',self.trimx(fdacm,3))
         
        datapos=self.channellist[obji][4]+self.headerinfo['BlockLen']  #数据开始位置
        self.fhd.seek(datapos)
        datafmf="f"
        tmprs=calcsize(datafmf)
        ts=calcsize(str(fdacm[5])+'f')
        bigda= np.array (unpack(str(fdacm[5])+'f', self.fhd.read(ts)))
        #print bigda.shape
        dasize=fdacm[5]*tmprs    #数据体总大小
         
        xd = np.arange (round(fdacm[3],3),round(fdacm[3],3)+fdacm[5]*float(fdacm[4]),float(fdacm[4]))
        biga=np.where(bigda>-900,bigda,0)#将小于0的设为0
        #print bigda.shape
        np.round(biga,4,biga)
        return xd,biga
     
    
    def readtable(self,tname):
        obji=tname
        print (self.tablelist[obji])
        self.fhd.seek(self.tablelist[obji][4])
        channlefmt="2L"          #表信息
        rsc=calcsize(channlefmt)
        bff=self.fhd.read(rsc)
        if len(bff)<rsc:
            fdac=[0,0]
        else:
            fdac=list(unpack(channlefmt, bff))
        print ("记录数:%s 字段数:%s" % (fdac[0],fdac[1]))
        print ('--------------------')
        tablefmt="32s2HL"    #字段信息
        rscx=calcsize(tablefmt)
        vlfmt1=''
        cols=[]
        colname=[]
        for xstp in range(fdac[1]): #表字段信息
            #wisfile.seek(rscx,1)
            #print 'read to ' + str(wisfile.tell())
            bff=self.fhd.read(rscx)
            tabcols=self.trimx(list(unpack(tablefmt, bff)),1)
            tm=self.datatype[tabcols[1]-1]
            if tm=='s':tm=str(tabcols[2])+tm
            vlfmt1 +=tm
            colname.append(tabcols[0])
            #print tabcols
            
        cols.append(colname)
        rslen=calcsize(vlfmt1)
        for k in range(fdac[0]):
            bff=self.fhd.read(rslen)
            tbx=self.trim0(list(unpack(vlfmt1, bff)))
            cols.append(tbx)
            #print '-'.join(tbx)
        return cols
    
    def channel2txt(self,fname):   #所有曲线导出txt
        tx=open(fname,'w')
        chandatas=[]
        tx.write("      #DEPTH")
        for chn in sorted(self.channellist.keys()):
            if chn.find('%')==-1:
                chandatas.append(self.readchannel(chn))
                tx.write(' '*(12-len(chn))+chn)
        tx.write("\r\n")
        sf=np.column_stack((chandatas[0][0],chandatas[0][1],chandatas[1][1]))
        
        #sf=str(chandatas[0][1])+' '*(12-len(str(chandatas[0][1])))
        tx.close()
        #for rw in chandatas[0][0]:
            
        

        
    def analysis_zh(self,rest):
            num=0
            szPattern="\s+"
            zhjs=[]
            zhjsm=[]
            for rw in rest.split("\r\n"):
#                 print rw
                if num <=5 :
                    num +=1
                    continue
                elif num>5 :   #and num%2==0 
                    if rw.find('-999')>0:
                        print ('found excep number -999 on line %d' %  num)
                        continue  
                    zhjsm.append(re.split(szPattern, rw)[:-1])     #用不定空格分隔
                    if rw.find('平均值')>0:
                        tms=zhjsm[num-6-2][:6]+zhjsm[num-6][1:]+zhjsm[num-6-2][len(zhjsm[num-6])+6-len(zhjsm[num-6-2]):]
                        zhjs.append(tms)
#                         print tms
                    num +=1
    def analysis_jx(self,rest):
           num=0
           szPattern="\s+"
           for rw in rest.split("\r\n"):
#                 print rw
                if num <=5 :
                    continue
                if num>5 :   #and num%2==0
                    if rw.find('-999')>0:
                        print ('found excep number -999 on line %d' %  num)
                        continue
                    print (re.split(szPattern, rw)[:-1])     #用不定空格分隔
                num +=1
        
        