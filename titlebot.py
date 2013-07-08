#!/usr/bin/env python2
# coding: utf-8

import os
import sys
import re

import socket
socket.setdefaulttimeout(10)

import time
import urllib2
from HTMLParser import HTMLParser as html_parser
import zlib

import libirc

HOST = "irc.freenode.net"
PORT = 6667
NICK = "titlebot2"
IDENT = "titlebot2"
REALNAME = "titlebot2"
CHANNELS = ["#kneecircle"]
ADMINS = ["biergaizi"]  # empty list means disable permission checking

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
    url = url.split(">", 1)[0].split('"', 1)[0]
    if re.match("https?:/*git.io(/|$)", url):
        # git.io is buggy
        return True
    return False


def restartProgram():
    time.sleep(10)
    sys.stderr.write("Restarting...\n")
    python = sys.executable
    os.execl(python, python, * sys.argv)


def getWebResourceInfo(h):
    webInfo = {
        "type": "",
        "title": "",
        "size": ""
    }

    def htmlDecode(encodedText):
        decodedText = ""
        for encoding in ("utf-8", "gbk", "gb18030", "iso-8859-1"):
            try:
                decodedText = encodedText.decode(encoding)
                break
            except UnicodeDecodeError:
                pass
        if not decodedText:
            decodedText = decodedText.decode("utf-8", "replace")

        decodedText = html_parser().unescape(decodedText).replace("\r", "").replace("\n", " ").strip()
        return decodedText

    def readContents(h):
        """Read a little part of the contents"""
        contents = ""
        counter = 1
        MAX = 5
        while len(contents) < 16384 and counter < MAX:
            following_contents = h.read(16384)
            if following_contents:
                contents += following_contents
            else:
                break
            counter += 1
        return contents

    def decompressContents(contents):
        """Decompress gzipped contents, ignore the error"""
        try:
            gunzip = zlib.decompressobj(16 + zlib.MAX_WBITS)
            contents = gunzip.decompress(contents)
        except:
            pass
        return contents

    if h.info()["Content-Type"].split(";")[0] == "text/html" or (not "Content-Type" in h.info()):
        webInfo["type"] = "text/html"
        contents = readContents(h)

        if h.info().get("Content-Encoding") == "gzip":  # Fix buggy www.bilibili.tv
            decompressContents(contents)

        if contents.find("<title>") != -1:
            encodedTitle = contents.split("<title>")[1].split("</title>")[0]
            webInfo['title'] = htmlDecode(encodedTitle)
        else:
            webInfo['title'] = ""
    else:
        webInfo["type"] = h.info()["Content-Type"]
        if "Content-Range" in h.info():
            webInfo["size"] = h.info()["Content-Range"].split("/")[1]
        elif "Content-Length" in h.info():
            webInfo["size"] = h.info()["Content-Length"]

    return webInfo


if __name__ == "__main__":
    try:
        irc = libirc.IRCConnection()
        irc.connect((HOST, PORT))
        irc.setnick(NICK)
        irc.setuser(IDENT, REALNAME)
        for channel in CHANNELS:
            irc.join(channel)
    except:
        restartProgram()

    channel = CHANNELS[0]

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
                if message["nick"] in ADMINS:
                    if message["msg"] == u"Get out of this channel!":  # A small hack
                        irc.quit(u"%s asked to leave." % message["nick"])
                        running = False
                        break
                    elif message["msg"] == u"Restart!":
                        irc.quit(u"%s asked to restart." % message["nick"])
                        running = False
                        restartProgram()
                    else:
                        irc.say(message["nick"], "Unknown Command, 233333...")
                else:
                    irc.say(message["nick"], "Permission Denied")

            channel = message["dest"]
            words = message["msg"].split()
            for word in words:
                word = pickupUrl(word)
                if not word or inBlacklist(word):
                    continue

                opener = urllib2.build_opener()
                opener.addheaders = HEADERS
                h = opener.open(word.encode("utf-8", "replace"))

                if h.code not in [200, 206]:
                    irc.say(channel, u"⇪HTTP %d 错误\r\n" % h.code)
                    continue

                contentsInfo = getWebResourceInfo(h)

                if contentsInfo["type"] == "text/html" and contentsInfo["title"]:
                    irc.say(channel, u"⇪标题: %s" % contentsInfo["title"])
                elif contentsInfo["type"] == "text/html" and not contentsInfo["title"]:
                        irc.say(channel, u"⇪无标题网页")
                elif contentsInfo["size"]:
                    assert contentsInfo["type"]
                    irc.say(channel, u"⇪文件类型: %s, 文件大小: %s 字节\r\n" % (contentsInfo["type"], contentsInfo["size"]))
                elif contentsInfo["type"]:
                    irc.say(channel, u"⇪文件类型: %s\r\n" % contentsInfo["type"])

        except socket.error as e:
            sys.stderr.write("Error: %s\n", e)
            irc.quit("Network error.")
        except Exception as e:
            try:
                irc.say(channel, u"哎呀，%s 好像出了点问题: %s" % (NICK, e))
            except:
                pass

# vim: et ft=python sts=4 sw=4 ts=4
