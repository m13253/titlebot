#!/usr/bin/env python2
# coding: utf-8

import sys
import socket
import string
import urllib2
import HTMLParser

HOST="irc.freenode.net"
PORT=6667
NICK="titlebot"
IDENT="titlebot"
REALNAME="titlebot"
CHANS=["#Orz"]

readbuffer=""
s=socket.socket()
s.connect((HOST, PORT))
s.send("NICK %s\r\n" % NICK)
s.send("USER %s %s bla :%s\r\n" % (IDENT, HOST, REALNAME))
for CHAN in CHANS:
    s.send("JOIN :%s\r\n" % CHAN)
CHAN=CHANS[0]
socket.setdefaulttimeout(10)

html_parser=HTMLParser.HTMLParser()

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
                CHAN=sline[2]
                if line.find(" PRIVMSG %s :" % NICK)!=-1:
                    if line.split(" PRIVMSG %s :" % NICK)[1]=="Get out of this channel!": # A small hack
                        s.send("QUIT :Client Quit\r\n")
                        quiting=True
                    else:
                        s.send("PRIVMSG %s :%s: 我不接受私信哦。\r\n" % (rnick, rnick))
                else:
                    content=line.split(" PRIVMSG %s :" % CHAN)[1]
                    for w in content.split():
                        if w.startswith("http:") or w.startswith("https:"):
                            opener=urllib2.build_opener()
                            opener.addheaders = [("Accept-Charset", "utf-8, iso-8859-1"), ("Accept-Language", "zh-cn, zh-hans, zh-tw, zh-hant, zh, en-us, en-gb, en"), ("Range", "bytes=0-16383"), ("User-Agent", "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.1 (KHTML, like Gecko) Safari/537.1"), ("X-Forwarded-For", "10.2.0.101"), ("X-moz", "prefetch"), ("X-Prefetch", "yes")]
                            h=opener.open(w)
                            if h.code==200 or h.code==206:
                                if not "Content-Type" in h.info() or h.info()["Content-Type"].split(";")[0]=="text/html":
                                    wbuf=h.read(16384)
                                    if wbuf.find("<title>")!=-1:
                                        title=wbuf.split("<title>")[1].split("</title>")[0]
                                        title=html_parser.unescape(title.decode("utf-8", "replace")).encode("utf-8", "replace").replace("\r", "").replace("\n", " ").strip()
                                        s.send("PRIVMSG %s :⇪标题: %s\r\n" % (CHAN, title))
                                    else:
                                        s.send("PRIVMSG %s :⇪无标题网页\r\n" % CHAN)
                                else:
                                    if "Content-Range" in h.info():
                                        s.send("PRIVMSG %s :⇪文件类型: %s, 文件大小: %s 字节\r\n" % (CHAN, h.info()["Content-Type"], h.info()["Content-Range"].split("/")[1]))
                                    elif "Content-Length" in h.info():
                                        s.send("PRIVMSG %s :⇪文件类型: %s, 文件大小: %s 字节\r\n" % (CHAN, h.info()["Content-Type"], h.info()["Content-Length"]))
                                    else:
                                        s.send("PRIVMSG %s :⇪文件类型: %s\r\n" % (CHAN, h.info()["Content-Type"]))
                            else:
                                s.send("PRIVMSG %s :⇪HTTP %d 错误\r\n" % (CHAN, h.code))
        except Exception as e:
            s.send("PRIVMSG %s :哎呀，%s 好像出了点问题: %s\r\n" % (CHAN, NICK, e))

# vim: et ft=python sts=4 sw=4 ts=4
