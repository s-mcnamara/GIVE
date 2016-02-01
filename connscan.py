#
# This file contains the class which handles displaying IP addresses found
# using the connscan plugin
#
import wx
import sys
import os
import sqlite3

class ConnScan(wx.Panel):

    def __init__(self, parent, id=-1):
	print "In ConnScan constructor..."

        wx.Panel.__init__(self, parent, id)

	self.ReadDB = True

        # master sizer for the whole panel
        self.ConnScanSizer = wx.BoxSizer(wx.HORIZONTAL)
	# create the control to display the IP addresses
	self.ConnDetails = wx.ListCtrl(self,style=wx.LC_REPORT,pos=(0,0))
	# add control to sizer
	self.ConnScanSizer.Add(self.ConnDetails,1, wx.EXPAND|wx.ALL)
#
#   	Add columns to the connection details control
#
        self.ConnDetails.InsertColumn(0, "Local IP", width = wx.LIST_AUTOSIZE) 
        self.ConnDetails.InsertColumn(1, "Local Port", width = wx.LIST_AUTOSIZE) 
        self.ConnDetails.InsertColumn(2, "Remote IP", width = wx.LIST_AUTOSIZE)
        self.ConnDetails.InsertColumn(3, "Remote Port", width = wx.LIST_AUTOSIZE)
        self.ConnDetails.InsertColumn(4, "PID", width = wx.LIST_AUTOSIZE)
	self.ConnDetails.InsertColumn(5, "EXE", width = wx.LIST_AUTOSIZE)

        self.SetSizer(self.ConnScanSizer)
        self.SetAutoLayout(1)
#
#	Read in a list of malicious IP addresses to highlight any found
#
	print "Reading in malicious IP addresses..."
	GiveHome = os.getenv('GIVEDB')
        self.MalIPs=set()
	MalIPFN = os.path.join(GiveHome,'ipwarning.txt')
	MalIPFile = open(MalIPFN,'r')
	for line in MalIPFile:
     	    addr = line[0:len(line)-1].strip()
    	    self.MalIPs.add(addr)
	MalIPFile.close()
	print "Have a list of ",len(self.MalIPs)," malicious IP addresses"

    def ShowConnections(self,DBconn):
	print "In ConnScan::ShowConnections"
	if DBconn == None:
	    dlg = wx.MessageDialog(self, "No Database Open", "Error", wx.OK|wx.ICON_EXCLAMATION)
            dlg.ShowModal() # Show it
            dlg.Destroy() # finally destroy it when finished.
#
#	    Read the database if it hasn't been read already
#

	elif self.ReadDB:
	    self.ReadDB = False
            print "Reading database..."
	    print "Checking IP addresses against a list with ",len(self.MalIPs)," entries"
	    cmd = "SELECT * FROM CONNSCAN_%s" % self.GetParent().CaseNum
            cursor = DBconn.execute(cmd)
            for row in cursor:
                #print row[0]," ",row[1]," ",row[2]," ",row[3]," ",row[4]
                itemIDX = self.ConnDetails.InsertStringItem(0,str(row[1]))  # Local IP
                self.ConnDetails.SetStringItem(itemIDX,1,str(row[2]))  # Local Port
                remoteIP = str(row[3])
                self.ConnDetails.SetStringItem(itemIDX,2,str(row[3]))  # Remote IP
                if remoteIP in self.MalIPs:
		    print "Found malicious IP: ",remoteIP
		    self.ConnDetails.SetItemBackgroundColour(itemIDX,wx.RED)
                self.ConnDetails.SetStringItem(itemIDX,3,str(row[4]))  # Remote IP
		self.ConnDetails.SetStringItem(itemIDX,4,str(row[0]))  # PID
#
#		Use PID to retrieve executable name from PSLIST, if not found print "UNKNOW PID"
#
		cmd = "SELECT IMGNAME FROM PSLIST_%s WHERE PID=%u" % (self.GetParent().CaseNum,int(row[0]))
		#print cmd
                cursor2 = DBconn.execute(cmd)
		row2 = cursor2.fetchone()
		if row2 is not None:
		    self.ConnDetails.SetStringItem(itemIDX,5,str(row2[0]))
		else:
		    self.ConnDetails.SetStringItem(itemIDX,5,str('UNKNOWN PID'))  # NO EXE name
		    self.ConnDetails.SetItemBackgroundColour(itemIDX,wx.YELLOW)
