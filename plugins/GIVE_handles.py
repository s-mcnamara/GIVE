#
# GIVE_handles plugin to return handles for each process and store
# the results in a SQLite database table
#
import volatility.plugins.taskmods as taskmods
import volatility.plugins.handles as Hndls
import sqlite3
import os

class GIVE_Handles(Hndls.Handles):
    """GIVE plugin to store list of handles for each process in a SQLite database"""

    def __init__(self, config, *args, **kwargs):
        print "In GIVE_handles constructor"
        Hndls.Handles.__init__(self, config, *args, **kwargs)
	config.add_option('CASENUM', short_option = '-cn', default = None,
	    cache_invalidator = False,help = 'GIVE Case Number',action = 'store', type = 'str')
	config.add_option('DBFILE', short_option = '-df', default = None,
	    cache_invalidator = False,help = 'GIVE database file',action = 'store', type = 'str')
        print "CASENUM: ",self._config.cn
	print "DBFILE: ",self._config.df

    def render_text(self, outfd, data):
        print "In GIVE_Handles render_text method"
        conn = sqlite3.connect(os.getenv('GIVEDB') + '/' + self._config.df)
        cursor = conn.cursor()
	cmd = "CREATE TABLE HANDLES_%s (PID INT, HANDLE INT, TYPE TEXT, DETAILS TEXT)"  % self._config.cn
	print "Create table command: ",cmd
        cursor.execute(cmd)

        if self._config.OBJECT_TYPE:
            object_list = [s for s in self._config.OBJECT_TYPE.split(',')]
        else:
            object_list = []

        for pid, handle, object_type, name in data:
            if object_list and object_type not in object_list:
                continue
            if self._config.SILENT:
                if len(name.replace("'", "")) == 0:
                    continue
            if not self._config.PHYSICAL_OFFSET:
                offset = handle.Body.obj_offset
            else:
                offset = handle.obj_vm.vtop(handle.Body.obj_offset)
	    try:  # object type sometimes is weird Unicode.  If so, make it a blank.
	        ObjType = str(object_type or '') 
            except:
		ObjType = ''

	    cmd = "INSERT INTO HANDLES_%s VALUES (%u,%u,'%s','%s')" \
               % (self._config.cn, int(pid),int(handle.HandleValue),str(ObjType),str(name or ''))
	    #print cmd
            cursor.execute(cmd)

        conn.commit()
        conn.close()
