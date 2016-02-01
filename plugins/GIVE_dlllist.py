#
# GIVE_DllList plugin to return DLLs loaded for each process and store
# the results in a SQLite database
#

import volatility.win32.tasks as tasks
import volatility.plugins.common as common 
import volatility.plugins.taskmods as taskmods
import sqlite3
import os
import datetime

class GIVE_DllList(taskmods.DllList):
    """GIVE plugin to store list of DLL's for each process in a SQLite database"""

    def __init__(self, config, *args, **kwargs):
        print "In GIVE_dlllist constructor"
        taskmods.DllList.__init__(self, config, *args, **kwargs)
	config.add_option('CASENUM', short_option = '-cn', default = None,
	    cache_invalidator = False,help = 'GIVE Case Number',action = 'store', type = 'str')
	config.add_option('DBFILE', short_option = '-df', default = None,
	    cache_invalidator = False,help = 'GIVE database file',action = 'store', type = 'str')
        print "CASENUM: ",self._config.cn
	print "DBFILE: ",self._config.df

    def render_text(self, outfd, data):
        print "In GIVE_DllList render_text method"
        conn = sqlite3.connect(os.getenv('GIVEDB') + '/' + self._config.df)
        cursor = conn.cursor()
	cmd = "CREATE TABLE DLLLIST_%s (PID INT, PATH TEXT)" % self._config.cn
	print "Create table command: ",cmd
        cursor.execute(cmd)

        for task in data:
            if task.Peb:
                for m in task.get_load_modules():
		    cmd = "INSERT INTO DLLLIST_%s VALUES (%u,'%s')" % (self._config.cn,
                       int(task.UniqueProcessId),str(m.FullDllName or ''))
		    print cmd
		    cursor.execute(cmd)
            else:
		cmd = "INSERT INTO DLLLIST_%s VALUES (%u,'%s')" % (self._config.cn,
		   int(task.UniqueProcessId),"Unable to read PEB for task")
		print cmd
                cursor.execute(cmd)

        conn.commit()
        conn.close()
