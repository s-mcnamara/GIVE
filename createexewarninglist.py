#!/usr/bin/python

#
# This file takes well-known Windows program names that are often imitated by malware
# with subtle differences and writes them to a file in the $GIVEDB folder.  The file
# is read by GIVE and used to identify suspect processes
#
import os

alphabet = 'abcdefghijklmnopqrstuvwxyz'

def mangle(exe):
   splits     = [(exe[:i], exe[i:]) for i in range(len(exe) + 1)]
   deletes    = [a + b[1:] for a, b in splits if b]
   transposes = [a + b[1] + b[0] + b[2:] for a, b in splits if len(b)>1]
   replaces   = [a + c + b[1:] for a, b in splits for c in alphabet if b]
   num4letts = []
   num4letts.append(exe.replace('o','0'))
   num4letts.append(exe.replace('i','1'))
   num4letts.append(exe.replace('l','1'))
   num4letts.append(exe.replace('q','9'))
   return set(deletes+transposes+replaces+num4letts)

#
# Main routine
#
WindowsExes=['lsass','csrss','svchost','smss','explorer']
GiveDir = os.getenv('GIVEDB')
WarningFileName = os.path.join(GiveDir,'exewarning.txt')
WarningFile = open(WarningFileName,'w')
for idx in range(len(WindowsExes)):
    WarningStrings = mangle(WindowsExes[idx])
    try:
        WarningStrings.remove(WindowsExes[idx])  # remove the word itself if its there
    except:
	pass
    else:
        for string in WarningStrings:
            WarningFile.write(string + '\n')
    
WarningFile.close()

print "Done! File created: ",WarningFileName
