'''
Generates a Freemind compatible file & outline text file
from Saylor GitHub repo

Known limitation: does not handle long titles wrapping onto a
second line--reads only first line

Saves files in the same directory as the program

2016 Paul Morris
paulmorris@inbox.com
'''

import urllib
import os

# Gets path for text file (same as script)
path = os.path.dirname(__file__) + "/"

def outline(line, level):
    ''' Add line to outlineText string indented by 2 spaces for each level'''
    global outlineText
    for i in range(level):
        outlineText = outlineText + "  "
    outlineText = outlineText + line + '\n'

def countUnits():
    ''' Count the number of unit pages'''
    count = 0
    while True:
        if count+1<10:
            url = urlStart+course+urlEnd+'Unit0'+str(count+1)+'.md'
        else:
            url = urlStart+course+urlEnd+'Unit'+str(count+1)+'.md'
        uh = urllib.urlopen(url)
        check = uh.readline()
        if check == "Not Found": #github raw return for a non-existent page
            break
        else: 
            count +=1
    return count

outlineText = ""
tree = []

urlStart = 'https://raw.githubusercontent.com/saylordotorg/course_'
urlEnd = '/master/'
course = raw_input("Enter course:")
course = course.lower()

url = urlStart+course+urlEnd+'Intro.md'

uh = urllib.urlopen(url)
if uh.getcode()!=200:
    print "Course not found"
    quit()

#Extract Course Title
courseTitle = uh.readline()
courseTitle = courseTitle[courseTitle.find('"'):]
courseTitle = courseTitle[1:-2]
print courseTitle

tree.append(('<node TEXT="' + courseTitle + '">')) # Root of map
branch = 1
outline(courseTitle, 0)

unitCount = countUnits()

if unitCount == 0:
    print "No units found"
    quit()
        
print 'Processing Unit: ';

for unit in range(1,unitCount+1):
    print str(unit)
    if unit<10:
        url = urlStart+course+urlEnd+'Unit0'+str(unit)+'.md'
    else:
        url = urlStart+course+urlEnd+'Unit'+str(unit)+'.md'
    uh = urllib.urlopen(url)
    units = []
    unitTitle = uh.readline()
    unitTitle = unitTitle.lstrip('*')
    unitTitle = unitTitle[:unitTitle.find('*')]
    units.append(unitTitle)
    branch = branch + 1
    outline(unitTitle, 1)

    for line in uh:
        entry = ""
        if line.startswith('**'): # Unit titles are always bold
            words = line.split()       
            firstword = words[0]
            if firstword[2]>"0" and firstword[2]<="9": #Units/subunits start with numbers           
                for part in words:
                    if part.endswith('**'):
                        entry = entry + " " + part.rstrip('*')
                        break
                    if part.startswith('**'):
                        entry = part[2:]
                    else:   
                        entry = entry + " " + part  # Rebuild string
                outline(entry, firstword.count('.')+1)
                entry=entry.replace('&', '&amp;') # escape ampersands for xml
                units.append(entry)
                

    level = 0
    parent = -1
    oldLevel = 0
    
    if unit <= unitCount/2: #Position branches left or right
        unitPosition = 'left'
    else:
        unitPosition = 'right'
    
 
    for i in range (len(units)):

        oldLevel = level
        unitNo = units[i].split()
        level = unitNo[0].count('.')
        
        
        if oldLevel > level: #gone up

            while oldLevel>level:
                tree.append('</node>')
                branch = branch +1
                oldLevel -= 1
            
        if parent <= level-2: #gone down

            tree[len(tree)-1] = tree[len(tree)-1][:-2]+'>' #amend previous line
        if i == 0:
            tree.append('<node POSITION="' + unitPosition + '" TEXT="' + units[i] + '"/>')
        else:
            tree.append('<node TEXT="' + units[i] + '"/>')
        branch = branch+1
        parent = level-1

        
     
    while level>0:
        tree.append('</node>')
        branch += 1
        level -= 1


tree.append('</node>')


 
target = open(path + course + '.mm', 'w')
target.write('<map version="1.0.1">')  # Add required framing
target.write("\n")
for line in tree:
    target.write(line)
    target.write("\n")
target.write('</map>')
target.write("\n")
target.close()


f = open(path + course + "_outline.txt", "w") # Write outline to a text file
f.write(outlineText)
f.close()
   
