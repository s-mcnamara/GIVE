#
# Create a Process Tree Class.  This class is used to visualize the process hierarchy
#
class PTree:

    def __init__(self,PID):
        self.PID = PID
        self.image = ""
        self.numchildren = 0
        self.children = []

    def AddChild(self,PID,PPID):
        if self.PID == PPID:
            self.children.append(PTree(PID))
            self.numchildren += 1
        else:
            for idx in range(self.numchildren):
               self.children[idx].AddChild(PID,PPID)

    def SearchTree(self,PID):
        if self.PID == PID:
            return True
        else:
            for idx in range(self.numchildren):
                PIDFound = self.children[idx].SearchTree(PID)
                if PIDFound: return True

    def ListTree(self):
        for idx in range(self.numchildren): 
            print "------",self.children[idx].PID
        for idx in range(self.numchildren):
            self.children[idx].ListTree()
#
#   CalcXCoords returns the x coordinates for each of the children in a list
#
    def CalcXCoords(self,X):
        XL = []
        if self.numchildren%2 == 0:  # even # of children
            for idx in range(self.numchildren/2):
                pos1 = -3*(idx+1)
                pos2 = 3*(idx+1)
                XL.append(X+pos1)
                XL.append(X+pos2)

        else:  # ODD
            XL.append(X-3)  # place  first child to the left of its parent
            for idx in range((self.numchildren-1)/2):
                pos1 = -3*(idx+1)
                pos2 = 3*(idx+1)
                XL.append(X+pos1)
                XL.append(X+pos2)

        return XL


    def DrawTree(self,Graph,Positions):
        coords = Positions[self.PID]  # get the tuple with my coordinates to calc my children's
        Ycoord = int(coords[1]) - 1
        Xcoord = int(coords[0])
        XList = self.CalcXCoords(Xcoord)
#
#       Add edges and x/y coordinates for each child in the directed graph
#
        for idx in range(len(XList)):
            Graph.add_edge(self.PID,self.children[idx].PID)
            Positions[self.children[idx].PID] = (XList[idx],Ycoord)
        for idx in range(self.numchildren):
            self.children[idx].DrawTree(Graph,Positions)
