#
# GIVE_svcscan plugin to return a list of services from the memory image and store
# the results in a SQLite database
#
import volatility.malware.svcscan as svcscan
import volatility.utils as utils
import volatility.obj as obj
import volatility.plugins.common as common
import volatility.win32.tasks as tasks
import volatility.debug as debug
import volatility.plugins.registry.registryapi as registryapi

class GIVE_SvcScan(svcscan.SvcScan):
    "GIVE plugin to Scan for Windows services"

    def __init__(self, config, *args, **kwargs):
        print "In GIVE_svcscan constructor"
        #svcscan.SvcScan.__init__(self, config, *args, **kwargs)
	config.add_option('CASENUM', short_option = '-cn', default = None,
	    cache_invalidator = False,help = 'GIVE Case Number',action = 'store', type = 'str')
	config.add_option('DBFILE', short_option = '-df', default = None,
	    cache_invalidator = False,help = 'GIVE database file',action = 'store', type = 'str')
        print "CASENUM: ",self._config.cn
	print "DBFILE: ",self._config.df

    def render_text(self, outfd, data):
        conn = sqlite3.connect(os.getenv('GIVEDB') + '/' + self._config.df)
        cursor = conn.cursor()
	cmd = "CREATE TABLE SVCSCAN_%s (ORDER INT, PID INT, SVCNAME TEXT, \
	DISPNAME TEXT, SVCTYPE TEXT, SVCSTATE TEXT, BINPATH TEXT)" % self._config.cn
        print "Create table command: ",cmd
        cursor.execute(cmd)
        for rec in data:
	    if str(rec.State) = 'SERVICE_STOPPED':
	        BinPath = '-'
		PID = 0
	    else:
		BinPath = str(rec.Binary)
		PID = int(rec.Pid)
	    cmd = "INSERT INTO SVCSCAN_%s VALUES (%u,%u,'%s','%s','%s','%s','%s')" \
               % (self._config.cn,int(rec.Order),PID,str(rec.ServiceName.dereference()),
		  str(rec.DisplayName.dereference()),str(rec.Type),str(rec.State),BinPath)
	    print cmd
	    cursor.execute(cmd)


        conn.commit()
        conn.close()
