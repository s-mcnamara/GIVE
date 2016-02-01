#
# GIVE_handles plugin to return handles for each process and store
# the results in a SQLite database table
#

import volatility.scan as scan
import volatility.plugins.common as common
import volatility.cache as cache
import volatility.utils as utils
import volatility.obj as obj
import volatility.debug as debug #pylint: disable-msg=W0611
import volatility.plugins.connscan as CScan
import sqlite3
import os

class GIVE_ConnScan(CScan.ConnScan):
    """ GIVE plugin to get network connections """

    def __init__(self, config, *args, **kwargs):
        print "In GIVE_connscan constructor"
	common.AbstractWindowsCommand.__init__(self, config, *args, **kwargs)
	config.add_option('CASENUM', short_option = '-cn', default = None,
	    cache_invalidator = False,help = 'GIVE Case Number',action = 'store', type = 'str')
	config.add_option('DBFILE', short_option = '-df', default = None,
	    cache_invalidator = False,help = 'GIVE database file',action = 'store', type = 'str')
        print "CASENUM: ",self._config.cn
	print "DBFILE: ",self._config.df

    def render_text(self, outfd, data):
        print "In GIVE_ConnScan render_text method"
        conn = sqlite3.connect(os.getenv('GIVEDB') + '/' + self._config.df)
        cursor = conn.cursor()
	cmd = "CREATE TABLE CONNSCAN_%s (PID INT, LOCALIP TEXT, LOCALPORT INT,\
 REMOTEIP TEXT, REMOTEPORT INT)" % self._config.cn
	print "Create table command: ",cmd
        cursor.execute(cmd)


        for tcp_obj in data:
            cmd = "INSERT INTO CONNSCAN_%s VALUES (%u,'%s',%u,'%s',%u)" \
		% (self._config.cn, int(tcp_obj.Pid),str(tcp_obj.LocalIpAddress),
		int(tcp_obj.LocalPort),str(tcp_obj.RemoteIpAddress),int(tcp_obj.RemotePort))
            cursor.execute(cmd)

        conn.commit()
        conn.close()
