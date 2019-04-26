#encoding=gb18030
import cx_Oracle
import types

class dbhelper:
    tabset=['a010_edri@dbri','a013_edri@dbri','doc_spjfc@dbri','logdb.cj03_10_1@dbri','logdb.cj03_10_3@dbri','logdb.cj03_10_2@dbri','logdb.cjsj@dblog','logdb.dzwd@dblog']
    def __init__(self,user='',pwd='',tns='',thread=False):
        self.dbuser=user
        self.dbpwd=pwd
        self.dbtns=tns
        self.thread=thread
        self.conn=None
        self.isclosed=True
        
    def get_con(self,autoc=True):
        try:
            if self.thread:
                self.conn=self.conn=cx_Oracle.connect(self.dbuser,self.dbpwd,self.dbtns,threaded=self.thread)
            else:
                self.conn=cx_Oracle.connect(self.dbuser,self.dbpwd,self.dbtns)
           
#            self.cursor.numbersAsStrings=5
            self.isclosed=False
            self.conn.autocommit=autoc
        except (cx_Oracle.DatabaseError) as exc:
            error, = exc.args
            print(error)
            return False
        return True
    def execute_insert(self,sql,ar=()):
        try:
            cursor=None
            if self.conn is None or self.isclosed: 
                self.get_con()
            cursor=self.conn.cursor()
            if len(ar)>0: 
                cursor.execute(sql,ar)
            else:
                cursor.execute(sql)
            
        except (cx_Oracle.DatabaseError) as exc:
            print (sql)
            error, = exc.args
            print ("Oracle-Error-Code:", error)
            print ("Oracle-Error-Message:", error)
            return False
        return True
    #---在事务中运行，不提交，手动commit
    def execute_trainsert(self,sql,ar=()):
        try:
            cursor=None
            if self.conn is None or self.isclosed: 
                self.get_con(autoc=False)
            cursor=self.conn.cursor()
            if len(ar)>0: 
                cursor.execute(sql,ar)
            else:
                cursor.execute(sql)
        except (cx_Oracle.DatabaseError ,UnicodeEncodeError) as exc:
            print (sql,ar)
            error, = exc.args
            self.conn.rollback()  #回滚事务
            print ("Oracle-Error-Code:", error)
            print ("Oracle-Error-Message:", error)
            return False
        return True        
    def execute_update(self,sql,dt=()):
        try:
            if self.conn is None or self.isclosed: 
                self.get_con()
            self.conn.autocommit=True
            cursor=self.conn.cursor()
            cursor.execute(self.convert_sql(sql),dt)
#            self.conn.commit()
            cursor.close()
        except (cx_Oracle.DatabaseError) as exc:
            error, = exc.args
            print (sql)
            print ("Oracle-Error-Code:", error.code)
            print ("Oracle-Error-Message:", error.message)
    
    def execute_upmany(self,sql,ar):
        try:
            if self.conn is None or self.isclosed: 
                self.get_con()
            cursor=self.conn.cursor()
            if len(ar)>0: 
                cursor.executemany(sql,ar)
        except (cx_Oracle.DatabaseError) as exc:
            print (sql)
            error, = exc.args
            print ("Oracle-Error-Code:", error)
            print ("Oracle-Error-Message:", error)       
    def execute_query(self,sql,ar=()):
        datas=None
        try:
            if self.conn is None or self.isclosed: 
                self.get_con()
            cursor=self.conn.cursor()
            if len(ar)>0: 
                    cursor.execute(sql,ar)
            else:
                    cursor.execute(sql)
            datas=cursor.fetchall()
        except (cx_Oracle.DatabaseError) as exc:
            print (sql)
            error, = exc.args
            print ("Oracle-Error-Code:", error)
            print ("Oracle-Error-Message:", error)
        return datas
    
    def execute_queryjson(self,sql,args=(), one=False):
        try:
            if self.conn is None or self.isclosed: 
                self.get_con()
            cursor=self.conn.cursor()
            cursor.execute(self.convert_sql(sql),args)
            r = [dict((cursor.description[i][0], value) for i, value in enumerate(row)) for row in cursor.fetchall()]
        except (cx_Oracle.DatabaseError) as exc:
            print (sql)
            error, = exc.args
            print ("Oracle-Error-Code:", error.code)
            print ("Oracle-Error-Message:", error.message)
            raise cx_Oracle.DatabaseError
            return None
        return (r[0] if r else None) if one else r
    
    def execute_queryone(self,sql,ar=()):
        data=None
        try:
            if self.conn is None or self.isclosed: 
                self.get_con()
            cursor=self.conn.cursor()
            if len(ar)>0: 
                cursor.execute(sql,ar)
            else:
                cursor.execute(sql)
            #print self.cursor.rowcount
            #if self.cursor.rowcount>0:
            for row in cursor:
                #print row
                data,=row
        except (cx_Oracle.DatabaseError) as exc:
            error, = exc.args
            print (sql,ar)
            print (error.code)
            print (error.message)
            raise cx_Oracle.DatabaseError
            return None
        return data
    def execute_qbob(self,sql):
        try:
            if self.conn is None or self.isclosed: 
                self.get_con()
            cursor=self.conn.cursor()
            cursor.execute(self.convert_sql(sql))
            rr=cursor.__iter__()
        except (cx_Oracle.DatabaseError) as ee:
            print (ee.message)
            raise cx_Oracle.DatabaseError
            return None
        return rr
    def convert_sql(self,sql):
        return sql
#         sqlc=sql
#         #print sqlc
#         if type(sql)==types.:
#             sqlc=sql.encode('gbk')
#         #else:
#             #sqlc=unicode(sql)
#             #print sqlc
#         return sqlc
    
    @staticmethod
    def maketns(ip,port,dbname):
        tns=cx_Oracle.makedsn(ip,port,service_name=dbname)  # 默认是sid，要设置为servicename
        return tns
    def con_commit(self):
        self.conn.commit()
    def closecon(self):   
        if self.conn is not None :
                try:
                    self.conn.close()
                    self.isclosed=True
                except Exception:
                    return None
    def getbinData(self,fi):    
        f1 = open(fi,'rb') #==read file
        data = f1.read() 
        return cx_Oracle.Binary(data)