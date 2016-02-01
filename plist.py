#
# This file contains the class which handles the process list, the default
# GIVE window.
#
import wx
import sys
import os
import sqlite3

class PList(wx.Panel):

    def __init__(self, parent, id=-1):

        wx.Panel.__init__(self, parent, id)

        # master sizer for the whole panel
        self.PListSizer = wx.BoxSizer(wx.HORIZONTAL)
	# control on the left
	self.GIVEProcTree = wx.TreeCtrl(self,wx.ID_ANY)
        self.root = self.GIVEProcTree.AddRoot("Process List")
        self.GIVEProcTree.SetPyData(self.root, None)
#
#	Create controls to show process details in the right panel
#
	self.PSDetailTitle = wx.StaticText(self, -1, "Process Details", pos=(120,10))
	self.PSDetails = wx.ListCtrl(self,style=wx.LC_REPORT,pos=(120,30))
        self.DllList = wx.TextCtrl(self, style=wx.TE_MULTILINE,pos=(120,20))
        self.HandleList = wx.ListCtrl(self, style=wx.LC_REPORT,pos=(120,20))
	self.SocketList = wx.ListCtrl(self, style=wx.LC_REPORT,pos=(120,20))
#
#   	Add columns to the process details control
#
        self.PSDetails.InsertColumn(0, "Image", width = wx.LIST_AUTOSIZE) 
        self.PSDetails.InsertColumn(1, "Parent", width = wx.LIST_AUTOSIZE) 
        self.PSDetails.InsertColumn(2, "Threads", width = wx.LIST_AUTOSIZE)
        self.PSDetails.InsertColumn(3, "Handles", width = wx.LIST_AUTOSIZE)

        print "Binding events for the process tree..."
        self.Bind(wx.EVT_TREE_ITEM_EXPANDED, self.OnItemExpanded, self.GIVEProcTree)
        self.Bind(wx.EVT_TREE_ITEM_COLLAPSED, self.OnItemCollapsed, self.GIVEProcTree)
        self.Bind(wx.EVT_TREE_SEL_CHANGED, self.OnSelChanged, self.GIVEProcTree)
        self.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.OnActivate, self.GIVEProcTree)

        self.GIVEProcTree.Bind(wx.EVT_LEFT_DCLICK, self.OnLeftDClick)
        self.GIVEProcTree.Bind(wx.EVT_RIGHT_DOWN, self.OnRightDown)
        self.GIVEProcTree.Bind(wx.EVT_RIGHT_UP, self.OnRightUp)
#
#       Add columns to the handle details control
#
        self.HandleList.InsertColumn(0, "Handle ID", width = wx.LIST_AUTOSIZE) 
        self.HandleList.InsertColumn(1, "Type", width = wx.LIST_AUTOSIZE) 
        self.HandleList.InsertColumn(2, "Details", width = wx.LIST_AUTOSIZE)
#
#       Add columns to the socket details control
#
        self.SocketList.InsertColumn(0, "Port", width = wx.LIST_AUTOSIZE) 
        self.SocketList.InsertColumn(1, "Protocol", width = wx.LIST_AUTOSIZE) 
        self.SocketList.InsertColumn(2, "Address", width = wx.LIST_AUTOSIZE)
 	self.SocketList.InsertColumn(3, "Create Time", width = wx.LIST_AUTOSIZE)
#
#	Add item for right pane and add necessary columns
#
        DetailItem = wx.ListItem()
        DetailItem.SetId(0)
        self.PSDetails.InsertItem(DetailItem)

        DetailSizer = wx.BoxSizer(wx.VERTICAL)
        DetailSizer.Add(self.PSDetailTitle, 1)  # Text control on top
        DetailSizer.Add(self.PSDetails,10,wx.EXPAND|wx.ALL|wx.ALIGN_RIGHT,\
               border=10)  # ListCtrl beneath
        DetailSizer.Add(self.DllList,10,wx.EXPAND|wx.ALL|wx.ALIGN_TOP,\
               border=10)  # Text Control in same place, but HIDE it initially
        self.DllList.Show(False)
        DetailSizer.Add(self.HandleList,10,wx.EXPAND|wx.ALL|wx.ALIGN_TOP,\
               border=10)  # Text Control in same place, but HIDE it initially
        self.HandleList.Show(False)
     	DetailSizer.Add(self.SocketList,10,wx.EXPAND|wx.ALL|wx.ALIGN_TOP,\
               border=10)  # Text Control in same place, but HIDE it initially
        self.SocketList.Show(False)
#
# 	Create sizer for the left side of the panel
# 
        ListBoxSizer = wx.BoxSizer(wx.VERTICAL)
        ListBoxSizer.Add(self.GIVEProcTree, 1, wx.EXPAND|wx.ALL|wx.ALIGN_CENTER,border=5)
#
# 	Create sizer for the entire Plist panel
# 
        self.PListSizer = wx.BoxSizer(wx.HORIZONTAL)
#       self.PanelSizer.Add(self.LeftPanelSizer,1, wx.EXPAND|wx.ALL)
        self.PListSizer.Add(ListBoxSizer,1, wx.EXPAND|wx.ALL)
        self.PListSizer.Add(DetailSizer,3, wx.EXPAND|wx.ALL)
        self.SetSizer(self.PListSizer)
        self.SetAutoLayout(1)
#
#	Read in a list of malicious executable names to highlight any found
#
	print "Reading in a list of common mangling for executable names..."
	GiveHome = os.getenv('GIVEDB')
        self.MalExes=set()
	MalExeFN = os.path.join(GiveHome,'exewarning.txt')
	MalExeFile = open(MalExeFN,'r')
	for line in MalExeFile:
    	    exename = line[0:len(line)-1]
    	    self.MalExes.add(exename)
	MalExeFile.close()

    def OnOpenDB(self,DB,CN):
        print "Reading database for case number ",CN
	self.DBconn = DB
#
# 	Query SQLite db for list of processes, add them to the tree control
#
	cmd = "SELECT PID, IMGNAME FROM PSLIST_%s ORDER BY PID" % CN
	print cmd
        cursor = self.DBconn.execute(cmd)
   
        for row in cursor:
            exe = str(row[1]).lower()
            try:
  	        dot = exe.rindex('.')
	    except:
	        pass
	    else:
                exe = exe[0:dot]  # get name only, remove file type
            child = self.GIVEProcTree.AppendItem(self.root, str(row[0]))
            if exe in self.MalExes:
		self.GIVEProcTree.SetItemBackgroundColour(child,wx.RED)
            self.GIVEProcTree.SetPyData(child, row[0])  # data is int 
            subitem = self.GIVEProcTree.AppendItem(child, "DLLs Loaded")
            self.GIVEProcTree.SetPyData(subitem, row[0])
 	    subitem = self.GIVEProcTree.AppendItem(child, "Process Handles")
            self.GIVEProcTree.SetPyData(subitem, row[0])
	    subitem = self.GIVEProcTree.AppendItem(child, "Sockets")
            self.GIVEProcTree.SetPyData(subitem, row[0])

        self.GIVEProcTree.Expand(self.root)
	# DB.close() db should only be closed in GIVEFrame

#
#   Known bug that widgets don't display until you resize the frame, this is the
#   workaround
#
        #e = wx.SizeEvent(self.GetSize())
        #self.ProcessEvent(e)

        #print "Left Pane Sizer position: ",self.LeftPanelSizer.GetPosition()
        #print "Right Pane Sizer position: ",self.RightPanelSizer.GetPosition()
        self.Show(True) # is this necessary??

	# add to master sizer  IS THIS CORRECT???
        #PListSizer.Add(self.PSDetails, 2, flag=wx.EXPAND | wx.LEFT | wx.RIGHT, border=15) 

        self.PListSizer.AddSpacer(15)   # necessary?
        self.SetSizer(self.PListSizer)
	self.Raise()
	print "Leaving OnOpeDB..."

#        self.Raise()
#        self.SetPosition((0,0))
#        self.Fit()  
#        self.Hide()

    def SelectPID(self,PID,ItemID):
        #PID = int(event.GetString())
        print "Called Select PID with ", PID
#        cursor = GIVEFrame.DBconn.execute("SELECT * FROM PSLIST WHERE PID = ?", (PID,))
	cmd = "SELECT * FROM PSLIST_%s WHERE PID = ?" % self.GetParent().CaseNum
        cursor = self.DBconn.execute(cmd, (PID,))
        result = cursor.fetchone()
#
#       Add results to list control on the right
#
        #print "The process is running ", result[2]
        # doesn't work: self.DetailItem.SetText(str(result[2]))
        # this works: self.PSDetails.DeleteItem(self.DetailItem.GetId())
        #self.PSDetails.DetailItem.SetText(result[2])
        BGcolor = self.GIVEProcTree.GetItemBackgroundColour(ItemID)
        self.PSDetails.SetItemBackgroundColour(0,BGcolor) # match background color
	if BGcolor != wx.NullColour:
 	    self.PSDetails.SetStringItem(0,0,"**" + result[2].upper() + "**")  # Image Name
        else:
            self.PSDetails.SetStringItem(0,0,result[2])  # Image Name
            self.PSDetails.SetItemBackgroundColour(0,wx.WHITE) # force background color back to white
        self.PSDetails.SetStringItem(0,1,str(result[3]))  # Parent PID
        self.PSDetails.SetStringItem(0,2,str(result[4])) # Threads
        self.PSDetails.SetStringItem(0,3,str(result[5])) # Handles

    def ShowYourself(self):
        self.Raise()
        self.SetPosition((0,0))
        self.Fit()
        self.Show()
	e = wx.SizeEvent(self.GetSize())  # cause resize event so widget appears
        self.GetParent().ProcessEvent(e) 

    def OnItemExpanded(self, event):
        itemID = event.GetItem()
        if itemID:
            print "Expanded item ",self.GIVEProcTree.GetItemText(itemID)
            #self.log.WriteText("OnItemExpanded: %s\n" % self.tree.GetItemText(item))

    def OnItemCollapsed(self, event):
        print "In OnItemCollapsed"
        itemID = event.GetItem()
        if itemID:
            print self.GIVEProcTree.GetItemText(itemID)
            #self.log.WriteText("OnItemCollapsed: %s\n" % self.tree.GetItemText(item))
#
#  When the user clicks on a PID, I need to fill in the right-pane info which is in the GIVEFrame in 
#  the other class.  If they click on a sub-item for DLL or Handle info, need to display that instead.
#
    def OnSelChanged(self, event):
        print "In OnSelChanged"
        itemID = event.GetItem()
        BGcolor = self.GIVEProcTree.GetItemBackgroundColour(itemID)
        print "Item text: ",self.GIVEProcTree.GetItemText(itemID).lower(), " color: ",BGcolor
        itemParentID = self.GIVEProcTree.GetItemParent(itemID)
        if itemParentID == self.root:
           print "You selected a process from the process list"
           PID = self.GIVEProcTree.GetPyData(itemID)
           print "You selected PID ",PID
           self.SelectPID(PID,itemID)  # call function to fill in the detail window for the process
           self.DllList.Show(False) # hide DLL list
           self.HandleList.Show(False) # hide handle list
           self.SocketList.Show(False) # hide socket list
           self.PSDetails.Show(True)
           #e = wx.SizeEvent(self.GetSize())  # cause resize event so widget appears
           #self.ProcessEvent(e)  # THIS SHOULD BE A FUNCTION
        else:
	   itemText = self.GIVEProcTree.GetItemText(itemID).lower()  # use this to decide which to display
    	   if itemText == 'dlls loaded':
              print "You selected a DLL list from a process"
              PID = self.GIVEProcTree.GetPyData(itemParentID)
              self.DllList.Clear()  # clear previous results
              #cursor = GIVEFrame.DBconn.execute("SELECT PATH FROM DLLLIST WHERE PID = ?", (PID,))
	      cmd = "SELECT PATH FROM DLLLIST_%s WHERE PID = ?" % self.GetParent().CaseNum
	      cursor = self.DBconn.execute(cmd, (PID,))
              for row in cursor:
                 #print row[0]  # this is the DLL name #
                 self.DllList.AppendText(str(row[0]) + '\n')
              self.PSDetails.Show(False)  # hide the details control, show a new one with DLL info
              self.HandleList.Show(False)
              self.SocketList.Show(False)
              self.DllList.Show(True)
              #e = wx.SizeEvent(self.GetSize())  # cause resize event so widget appears
              #self.ProcessEvent(e)  # THIS SHOULD BE A FUNCTION
	   elif itemText == 'process handles':              
              PID = self.GIVEProcTree.GetPyData(itemParentID)
              print "You selected process handles for PID ",PID
              self.HandleList.DeleteAllItems()  # clear previous results from the widget
              cmd = "SELECT HANDLE,TYPE,DETAILS FROM HANDLES_%s WHERE PID = ?" % self.GetParent().CaseNum
	      cursor = self.DBconn.execute(cmd, (PID,))
              for row in cursor:
                 #print row[0]," ",row[1]," ",row[2]
                 itemIDX = self.HandleList.InsertStringItem(0,str(hex(row[0])))  # Handle ID
                 self.HandleList.SetStringItem(itemIDX,1,str(row[1]))  # Handle Type
                 self.HandleList.SetStringItem(itemIDX,2,str(row[2]))  # Handle Details
              self.PSDetails.Show(False)  # hide the details control, show a new one with handle info
              self.DllList.Show(False)
              self.SocketList.Show(False)
              self.HandleList.Show(True)
              #e = wx.SizeEvent(self.GetSize())  # cause resize event so widget appears
              #self.ProcessEvent(e)  # THIS SHOULD BE A FUNCTION
	   elif itemText == 'sockets':              
              PID = self.GIVEProcTree.GetPyData(itemParentID)
              print "You selected sockets for PID ",PID
              self.SocketList.DeleteAllItems()  # clear previous results from the widget
              cmd = "SELECT PORT,PROTO,ADDRESS,CREATETIME FROM SOCKETS_%s WHERE PID = ?" % self.GetParent().CaseNum
              cursor = self.DBconn.execute(cmd, (PID,))
              for row in cursor:
                 #print row[0]," ",row[1]," ",row[2]
                 itemIDX = self.SocketList.InsertStringItem(0,str(row[0]))  # Port #
                 self.SocketList.SetStringItem(itemIDX,1,str(row[1]))  # Protocol
                 self.SocketList.SetStringItem(itemIDX,2,str(row[2]))  # IP Address
 		 self.SocketList.SetStringItem(itemIDX,3,str(row[3]))  # create date
              self.PSDetails.Show(False)  # hide the details control, show a new one with handle info
              self.DllList.Show(False)
              self.HandleList.Show(False)
              self.SocketList.Show(True)

        e = wx.SizeEvent(self.GetSize())  # cause resize event so widget appears
        self.ProcessEvent(e)  # THIS SHOULD BE A FUNCTION

    def OnActivate(self, event):
        print "In OnActivate"
        #if self.item:
            #self.log.WriteText("OnActivate: %s\n" % self.tree.GetItemText(self.item))

    def OnRightDown(self, event):
        print "In OnRightDown"
        pt = event.GetPosition();
        item, flags = self.GIVEProcTree.HitTest(pt)
        if item:
            self.GIVEProcTree.SelectItem(item)

    def OnRightUp(self, event):
        print "In OnRightUp"
        pt = event.GetPosition();
        item, flags = self.GIVEProcTree.HitTest(pt)
        if item:        
            self.GIVEProcTree.EditLabel(item)


    def OnLeftDClick(self, event):
        print "In OnLeftDClick"
        pt = event.GetPosition();
        item, flags = self.tree.HitTest(pt)
        if item:
            parent = self.GIVEProcTree.GetItemParent(item)
            if parent.IsOk():
                self.GIVEProcTree.SortChildren(parent)
        event.Skip()
