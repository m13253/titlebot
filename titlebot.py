#!/usr/bin/env python2
# coding: utf-8

import os
import sys
import re

import socket
socket.setdefaulttimeout(10)

import time
import urllib2
import HTMLParser
import zlib

import libirc

HOST="irc.freenode.net"
PORT=6667
NICK="titlebot2"
IDENT="titlebot2"
REALNAME="titlebot2"
CHANNELS=["#kneecircle"]

HEADERS = [("Accept-Charset", "utf-8, iso-8859-1"),
           ("Accept-Language", "zh-cn, zh-hans, zh-tw, zh-hant, zh, en-us, en-gb, en"),
           ("Range", "bytes=0-16383"),
           ("User-Agent", "Mozilla/5.0 (compatible; Titlebot; like IRCbot; +https://github.com/m13253/titlebot)"),
           ("X-Forwarded-For", "10.2.0.101"),
           ("X-moz", "prefetch"),
           ("X-Prefetch", "yes"),
           ("X-Requested-With", "Titlebot")]

def pickupUrl(text):
    """Return a vaild URL from a string"""

    PROTOCOLS = ["http:", "https:"]
    for protocol in PROTOCOLS:
        index = text.find(protocol)
        if index != -1:
            return text[index:]
    return None

def inBlacklist(url):
    if re.match("https?:/*git.io(/|$)", url):
        # git.io is buggy
        return True
    return False

def restartProgram():
    time.sleep(10)
    sys.stderr.write("Restarting...\n")
    os.execlp("python2", "python2", __file__)
    raise Exception
    sys.exit(1)


try:
    irc=libirc.IRCConnection()
    irc.connect((HOST, PORT))
    irc.setnick(NICK)
    irc.setuser(IDENT, REALNAME)
    for channel in CHANNELS:
        irc.join(channel)
except:
    restartProgram()

channel=CHANNELS[0]

html_parser=HTMLParser.HTMLParser()

running = True
while running:
    if not irc.sock:
        running = False
        restartProgram()
    try:
        text = irc.recvline(block=True)
        if not text:
            continue

        sys.stderr.write("%s\n" % text.encode('utf-8', 'replace'))
        message = irc.parse(line=text)
        if not message or message["cmd"] != "PRIVMSG":
            continue

        if message["dest"] == NICK:
            if message["msg"] == u"Get out of this channel!":  # A small hack
                irc.quit(u"%s asked to leave." % message["nick"])
                running = False
        else:
            channel = message["dest"]
            words = message["msg"].split()
            for word in words:
                word = pickupUrl(word)
                if not word:
                    continue

                word = word.split(">", 1)[0].split('"', 1)[0]
                if inBlacklist(word):
                    continue

                opener=urllib2.build_opener()
                opener.addheaders = HEADERS
                h=opener.open(word.encode("utf-8", "replace"))

                if h.code == 200 or h.code == 206:
                    if not "Content-Type" in h.info() or h.info()["Content-Type"].split(";")[0]=="text/html":
                        wbuf=h.read(16384)
                        read_times=1
                        while len(wbuf)<16384 and read_times<4:
                            read_times+=1
                            wbuf_=h.read(16384)
                            if wbuf_:
                                wbuf+=wbuf_
                            else:
                                break
                        if "Content-Encoding" in h.info() and h.info()["Content-Encoding"]=="gzip": # Fix buggy www.bilibili.tv
                            try:
                                gunzip_obj=zlib.decompressobj(16+zlib.MAX_WBITS)
                                wbuf=gunzip_obj.decompress(wbuf)
                            except:
                                pass
                        if wbuf.find("<title>")!=-1:
                            titleenc=wbuf.split("<title>")[1].split("</title>")[0]
                            title=None
                            for enc in ("utf-8", "gbk", "gb18030", "iso-8859-1"):
                                try:
                                    title=titleenc.decode(enc)
                                    break
                                except UnicodeDecodeError:
                                    pass
                            if title==None:
                                title=title.decode("utf-8", "replace")
                            title=html_parser.unescape(title).replace("\r", "").replace("\n", " ").strip()
                            irc.say(channel, u"⇪标题: %s" % title)
                        else:
                            irc.say(channel, u"⇪无标题网页")
                    else:
                        if "Content-Range" in h.info():
                            irc.say(channel, u"⇪文件类型: %s, 文件大小: %s 字节\r\n" % (h.info()["Content-Type"], h.info()["Content-Range"].split("/")[1]))
                        elif "Content-Length" in h.info():
                            irc.say(channel, u"⇪文件类型: %s, 文件大小: %s 字节\r\n" % (h.info()["Content-Type"], h.info()["Content-Length"]))
                        else:
                            irc.say(channel, u"⇪文件类型: %s\r\n" % h.info()["Content-Type"])
                else:
                    irc.say(channel, u"⇪HTTP %d 错误\r\n" % h.code)
    except Exception as e:
        try:
            irc.say(channel, u"哎呀，%s 好像出了点问题: %s" % (NICK, e))
        except:
            pass
    except socket.error as e:
        sys.stderr.write("Error: %s\n", e)
        irc.quit("Network error.")

# vim: et ft=python sts=4 sw=4 ts=4
