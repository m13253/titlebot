#!/usr/bin/env python2
# coding: utf-8

import sys
import socket
import string
import urllib
import json

HOST="irc.freenode.net"
PORT=6667
NICK="titlebot"
IDENT="titlebot"
REALNAME="titlebot"
CHAN="#Orz"

readbuffer=""
s=socket.socket()
s.connect((HOST, PORT))
s.send("NICK %s\r\n" % NICK)
s.send("USER %s %s bla :%s\r\n" % (IDENT, HOST, REALNAME))
s.send("JOIN :%s\r\n" % CHAN)
socket.setdefaulttimeout(10)

quiting=False
while not quiting:
    readbuffer=readbuffer+s.recv(1024)
    temp=string.split(readbuffer, "\n")
    readbuffer=temp.pop()
    for line in temp:
        try:
            print line
            line=string.rstrip(line)
            sline=string.split(line)
            if sline[0]=="PING":
                s.send("PONG %s\r\n" % sline[1])
            elif sline[1]=="PRIVMSG":
                rnick=sline[0][1:].split("!")[0]
                if line.find(" PRIVMSG %s :" % NICK)!=-1:
                    if line.split(" PRIVMSG %s :" % NICK)[1]=="Get out of this channel!": # A small hack
                        s.send("QUIT :Client Quit\r\n")
                        quiting=True
                    else:
                        s.send("PRIVMSG %s :%s: 我不接受私信哦\r\n" % (rnick, rnick))
                else:
                    content=line.split(" PRIVMSG %s :" % CHAN)[1]
                    for w in content.split():
                        if w.startswith("http:") or w.startswith("https:"):
                            h=urllib.urlopen(w)
                            if h.code==200:
                                if not "Content-Type" in h.info() or h.info()["Content-Type"].split(";")[0]=="text/html":
                                    wbuf=h.read(4096)
                                    if wbuf.find("<title>")!=-1:
                                        title=wbuf.split("<title>")[1].split("</title>")[0]
                                        s.send("PRIVMSG %s :⇪标题: %s\r\n" % (CHAN, title))
                                else:
                                    if "Content-Length" in h.info():
                                        s.send("PRIVMSG %s :⇪文件类型: %s, 文件大小: %s 字节\r\n" % (CHAN, h.info()["Content-Type"], h.info()["Content-Length"]))
                                    else:
                                        s.send("PRIVMSG %s :⇪文件类型: %s\r\n" % (CHAN, h.info()["Content-Type"]))
                            else:
                                s.send("PRIVMSG %s :⇪HTTP %d 错误\r\n" % (CHAN, h.code))
        except:
            s.send("PRIVMSG %s :哎呀，%s 好像出了点问题。\r\n" % (CHAN, NICK))

# vim: et ft=python sts=4 sw=4 ts=4
