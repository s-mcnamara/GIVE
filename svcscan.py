#
# This file contains the class which handles displaying services found
# using the svcscan plugin
#
import wx
import sys
import os
import sqlite3

class SvcScan(wx.Panel):

    def __init__(self, parent, id=-1):
	print "In SvcScan constructor..."

        wx.Panel.__init__(self, parent, id)

	self.ReadDB = True

        # master sizer for the whole panel
        self.SvcScanSizer = wx.BoxSizer(wx.HORIZONTAL)
	# create the control to display the IP addresses
	self.SvcDetails = wx.ListCtrl(self,style=wx.LC_REPORT,pos=(0,0))
	# add control to sizer
	self.SvcScanSizer.Add(self.SvcDetails,1, wx.EXPAND|wx.ALL)
#
#   	Add columns to the connection details control
#
        self.SvcDetails.InsertColumn(0, "Order", width = wx.LIST_AUTOSIZE) 
        self.SvcDetails.InsertColumn(1, "PID", width = wx.LIST_AUTOSIZE) 
        self.SvcDetails.InsertColumn(2, "Service Name", width = wx.LIST_AUTOSIZE)
        self.SvcDetails.InsertColumn(3, "Display Name", width = wx.LIST_AUTOSIZE)
        self.SvcDetails.InsertColumn(4, "Service Type", width = wx.LIST_AUTOSIZE)
	self.SvcDetails.InsertColumn(5, "Service State", width = wx.LIST_AUTOSIZE)
	self.SvcDetails.InsertColumn(6, "Binary Path", width = wx.LIST_AUTOSIZE)

        self.SetSizer(self.SvcScanSizer)
        self.SetAutoLayout(1)

    def ShowServices(self,DBconn):
	print "In SvcScan::ShowServices"
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
	    cmd = "SELECT * FROM SVCSCAN_%s" % self.GetParent().CaseNum
            cursor = DBconn.execute(cmd)
            for row in cursor:
                #print row[0]," ",row[1]," ",row[2]," ",row[3]," ",row[4]
                itemIDX = self.SvcDetails.InsertStringItem(0,str(row[0]))  # Order
                self.SvcDetails.SetStringItem(itemIDX,1,str(row[1]))  # PID
                self.SvcDetails.SetStringItem(itemIDX,2,str(row[2]))  # Service Name
                self.SvcDetails.SetStringItem(itemIDX,3,str(row[3]))  # Display Name
		self.SvcDetails.SetStringItem(itemIDX,4,str(row[4]))  # Service Type
		self.SvcDetails.SetStringItem(itemIDX,5,str(row[5]))  # Service State
		self.SvcDetails.SetStringItem(itemIDX,6,str(row[6]))  # Binary Path
