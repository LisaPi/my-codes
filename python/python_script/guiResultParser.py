#! /usr/bin/python --

import sys
import os
import re

# gui result parser at Windows
def guiResultParserWin(sDir=None):

    fobj = open(r'%s\bws.html' % sDir, 'w')
    fobj.write("%s%s" % ('''<font face="Arial">''',os.linesep))
    fobj.write("%s%s" % ('''<html>''',os.linesep))
    fobj.write("%s%s" % ('''<head><title>  </title></head>''',os.linesep))
    fobj.write("%s%s" % ('''<body leftmargin="50">''',os.linesep))
    fobj.write("%s%s" % ('''<h1><font color="Black">  </font></h1>''',os.linesep))
    fobj.write("%s%s" % ('''<table width="1000" border="1" cellspacing="2" cellpadding="5">''',os.linesep))
    fobj.write("%s%s" % ('''<tr>''',os.linesep))
    fobj.write("%s%s" % ('''<th align="centre">TEST ID </th>''',os.linesep))
    fobj.write("%s%s" % ('''<th align="centre">TEST TITLE </th>''',os.linesep))
    fobj.write("%s%s" % ('''<th align="centre">STATUS </th>''',os.linesep))
    fobj.write("%s%s" % ('''<tr>''',os.linesep))
    
    f = open(r'%s\ovsGuiTest.html' % sDir, 'r')
    html = [line.strip() for line in f.readlines()]
    f.close()
    
    for match in re.finditer("<div class='testcase'>(.*?)</div>.*?<pre>(.*?)</pre>", str(html)):
        title = match.group(1)
        content = match.group(2)
        content = re.sub(",", "\r\n", content)
        f = open(r'%s\%s.txt' % (sDir,title), 'w')
        f.write("%s" % content)
        f.close()
    
        if re.search("%s test done" % title.split('_')[1], content):
            status = 'pass'
            color = '#00FF00'
        else:
            status = 'fail'
            color = '#FF0000'
    
        fobj.write("%s%s" % ('''<tr>''',os.linesep))
        fobj.write("%s%s" % ('''<td align="left"> <a href="%s.txt"> %s </a> </td>''' % (title, title),os.linesep))
        fobj.write("%s%s" % ('''<td align="left"> %s %s </td>''' % (title.split('_')[1], title.split('_')[0]), os.linesep))
        fobj.write("%s%s" % ('''<td align="left" bgcolor="%s"> %s </td>''' % (color, status),os.linesep))
        fobj.write("%s%s" % ('''&nbsp;''',os.linesep))
        fobj.write("%s%s" % ('''</tr>''',os.linesep))

# gui result parser at Linux
def guiResultParserLin(sDir=None):

    fobj = open(r'%s/bws.html' % sDir, 'w')
    fobj.write("%s%s" % ('''<font face="Arial">''',os.linesep))
    fobj.write("%s%s" % ('''<html>''',os.linesep))
    fobj.write("%s%s" % ('''<head><title>  </title></head>''',os.linesep))
    fobj.write("%s%s" % ('''<body leftmargin="50">''',os.linesep))
    fobj.write("%s%s" % ('''<h1><font color="Black">  </font></h1>''',os.linesep))
    fobj.write("%s%s" % ('''<table width="1000" border="1" cellspacing="2" cellpadding="5">''',os.linesep))
    fobj.write("%s%s" % ('''<tr>''',os.linesep))
    fobj.write("%s%s" % ('''<th align="centre">TEST ID </th>''',os.linesep))
    fobj.write("%s%s" % ('''<th align="centre">TEST TITLE </th>''',os.linesep))
    fobj.write("%s%s" % ('''<th align="centre">STATUS </th>''',os.linesep))
    fobj.write("%s%s" % ('''<tr>''',os.linesep))

    f = open(r'%s/ovsGuiTest.html' % sDir, 'r')
    html = [line.strip() for line in f.readlines()]
    f.close()

    for match in re.finditer("<div class='testcase'>(.*?)</div>.*?<pre>(.*?)</pre>", str(html)):
        title = match.group(1)
        content = match.group(2)
        content = re.sub(",", "\r\n", content)
        f = open(r'%s/%s.txt' % (sDir,title), 'w')
        f.write("%s" % content)
        f.close()

        if re.search("%s test done" % title.split('_')[1], content):
            status = 'pass'
            color = '#00FF00'
        else:
            status = 'fail'
            color = '#FF0000'

        fobj.write("%s%s" % ('''<tr>''',os.linesep))
        fobj.write("%s%s" % ('''<td align="left"> <a href="%s.txt"> %s </a> </td>''' % (title, title),os.linesep))
        fobj.write("%s%s" % ('''<td align="left"> %s %s </td>''' % (title.split('_')[1], title.split('_')[0]), os.linesep))
        fobj.write("%s%s" % ('''<td align="left" bgcolor="%s"> %s </td>''' % (color, status),os.linesep))
        fobj.write("%s%s" % ('''&nbsp;''',os.linesep))
        fobj.write("%s%s" % ('''</tr>''',os.linesep))

if __name__ == "__main__":

    if sys.platform == 'win32':
        guiResultParserWin(sDir="c:\gui")
    else:
        guiResultParserLin(sDir="/home/build/automation/tools")
