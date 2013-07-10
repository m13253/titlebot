HOST = "irc.freenode.net"
PORT = 6667
NICK = "titlebot002"
IDENT = "titlebot002"
REALNAME = "titlebot002"
CHANNELS = ["#kde-cn", "##Orz", "#botwar"]
ADMINS = ["biergaizi", "StarBrilliant"]  # empty list means disable permission checking

HEADERS = [("Accept-Charset", "utf-8, iso-8859-1"),
           ("Accept-Language", "zh-cn, zh-hans, zh-tw, zh-hant, zh, en-us, en-gb, en"),
           ("Range", "bytes=0-16383"),
           ("User-Agent", "Mozilla/5.0 (compatible; Titlebot; like IRCbot; +https://github.com/biergaizi/titlebot)"),
           ("X-Forwarded-For", "10.2.0.101"),
           ("X-moz", "prefetch"),
           ("X-Prefetch", "yes"),
           ("X-Requested-With", "Titlebot")]
