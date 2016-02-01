#
# GIVE_pslist plugin to return a process list from the memory image and store
# the results in a SQLite database
#

import volatility.win32.tasks as tasks
import volatility.plugins.common as common 
import volatility.plugins.taskmods as taskmods
import sqlite3
import os
import datetime

class GIVE_pslist(taskmods.PSList):
    """GIVE plugin to store pslist in a SQLite database"""

    def __init__(self, config, *args, **kwargs):
        print "In GIVE_pslist constructor"
        taskmods.PSList.__init__(self, config, *args, **kwargs)
	config.add_option('CASENUM', short_option = '-cn', default = None,
	    cache_invalidator = False,help = 'GIVE Case Number',action = 'store', type = 'str')
	config.add_option('DBFILE', short_option = '-df', default = None,
	    cache_invalidator = False,help = 'GIVE database file',action = 'store', type = 'str')
        print "CASENUM: ",self._config.cn
	print "DBFILE: ",self._config.df

    def render_text(self, outfd, data):
        conn = sqlite3.connect(os.getenv('GIVEDB') + '/' + self._config.df)
        cursor = conn.cursor()
	cmd = "CREATE TABLE PSLIST_%s (PID INT PRIMARY KEY, \
	OFFSET INT, IMGNAME TEXT, PPID INT, THREADS INT, HANDLES INT, \
	SESSID INT, CREATETIME TEXT, EXITTIME TEXT)" % self._config.cn
        print "Create table command: ",cmd
        cursor.execute(cmd)
        for task in data:
            # PHYSICAL_OFFSET must STRICTLY only be used in the results.  If it's used for anything else,
            # it needs to have cache_invalidator set to True in the options
            if not self._config.PHYSICAL_OFFSET:
                offset = task.obj_offset
            else:
                offset = task.obj_vm.vtop(task.obj_offset)
            #print task.UniqueProcessId, " ",task.ImageFileName
	    cmd = "INSERT INTO PSLIST_%s VALUES (%u,%u,'%s',%u,%u,%u,%u,'%s','%s')" \
               % (self._config.cn, int(task.UniqueProcessId),int(offset),str(task.ImageFileName),
                 int(task.InheritedFromUniqueProcessId),int(task.ActiveThreads),
                 int(task.ObjectTable.HandleCount),int(task.SessionId),
                 str(task.CreateTime or ''),str(task.ExitTime or ''))
            #print cmd
	    cursor.execute(cmd)

        conn.commit()
        conn.close()
