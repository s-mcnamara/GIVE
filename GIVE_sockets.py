#
# GIVE_sockets plugin to return socket info and store
# the results in a SQLite database table
#

import volatility.plugins.common as common
import volatility.plugins.sockets as Socks
import volatility.protos as protos
import sqlite3
import os

class GIVE_Sockets(Socks.Sockets):
    """GIVE plugin to store socket information in a SQLite database"""

    def __init__(self, config, *args, **kwargs):
	print "In give_sockets constructor"
        Socks.Sockets.__init__(self, config, *args, **kwargs)
	config.add_option('CASENUM', short_option = '-cn', default = None,
	    cache_invalidator = False,help = 'GIVE Case Number',action = 'store', type = 'str')
	config.add_option('DBFILE', short_option = '-df', default = None,
	    cache_invalidator = False,help = 'GIVE database file',action = 'store', type = 'str')
        print "CASENUM: ",self._config.cn
	print "DBFILE: ",self._config.df

    def render_text(self, outfd, data):
	print "In GIVE_Sockets render_text method"
        conn = sqlite3.connect(os.getenv('GIVEDB') + '/' + self._config.df)
        cursor = conn.cursor()
	cmd = "CREATE TABLE SOCKETS_%s (PID INT, PORT INT, PROTO TEXT, ADDRESS TEXT, CREATETIME TEXT)"\
	   % self._config.cn
	#print "Create table command: ",cmd
        cursor.execute(cmd)

        for sock in data:
	    cmd = "INSERT INTO SOCKETS_%s VALUES (%u,%u,'%s','%s','%s')" % (self._config.cn,
               int(sock.Pid),int(sock.LocalPort),str(protos.protos.get(sock.Protocol.v(), "-")),
                str(sock.LocalIpAddress),str(sock.CreateTime))
	    #print cmd
            cursor.execute(cmd)

        conn.commit()
        conn.close()
