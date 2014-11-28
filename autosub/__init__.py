import Config
import logging.handlers
import time
from autosub.version import autosubversion

ROOTPATH=None
FALLBACKTOENG=None
DOWNLOADENG=None
DOWNLOADDUTCH=None
SUBENG=None
LOGFILE=None
SUBNL=None
SKIPHIDDENDIRS=None
NOTIFYNL=None
NOTIFYEN=None
LOGLEVEL=None
LOGLEVELCONSOLE=None
LOGSIZE=None
LOGNUM=None
SKIPSHOW=None
SKIPSHOWUPPER=None
USERNAMEMAPPING=None
USERNAMEMAPPINGUPPER=None
USERADDIC7EDMAPPING=None
USERADDIC7EDMAPPINGUPPER=None
NAMEMAPPING=None
NAMEMAPPINGUPPER=None
SHOWID_CACHE=None
POSTPROCESSCMD=None
CONFIGFILE=None
PATH=None
MINMATCHSCORE=None
CONFIGVERSION=None
CONFIGUPGRADED=None
HOMELAYOUTFIRST=None
ENGLISHSUBDELETE=None
PODNAPISILANG=None
SUBSCENELANG=None
BIERDOPJEMIRRORLANG=None
OPENSUBTITLESLANG=None
UNDERTEXTERLANG=None
ADDIC7EDLANG=None
ADDIC7EDUSER=None
ADDIC7EDPASSWD=None
SKIPWEBDL=None

ADDIC7EDAPI = None
WANTEDQUEUE=None
WANTEDQUEUELOCK=False
LASTESTDOWNLOAD=None

APIKEY=None
API=None
IMDBAPI=None

APICALLSLASTRESET_TVDB=None
APICALLSLASTRESET_SUBSEEKER=None
APICALLSRESETINT_TVDB=None
APICALLSRESETINT_SUBSEEKER=None
APICALLSMAX_TVDB=None
APICALLSMAX_SUBSEEKER=None
APICALLS_TVDB=None
APICALLS_SUBSEEKER=None

TIMEOUT=None
DOWNLOADS_A7=None
DOWNLOADS_A7MAX=None

SCHEDULERSCANDISK=None
SCHEDULERCHECKSUB=None

SCANDISK=None
CHECKSUB=None
DOWNLOADSUBS=None

WEBSERVERIP=None
WEBSERVERPORT=None
LAUNCHBROWSER=True
USERNAME=None
PASSWORD=None
WEBROOT=None

NOTIFYMAIL=None
MAILSRV=None
MAILFROMADDR=None
MAILTOADDR=None
MAILUSERNAME=None
MAILPASSWORD=None
MAILSUBJECT=None
MAILAUTH=None
MAILENCRYPTION=None
NOTIFYGROWL=None
GROWLHOST=None
GROWLPORT=None
GROWLPASS=None
NOTIFYTWITTER=None
TWITTERKEY=None
TWITTERSECRET=None
NOTIFYNMA=None
NMAAPI=None
NOTIFYPROWL=None
PROWLAPI=None
PROWLPRIORITY=None
PUSHALOTAPI=None
NOTIFYPUSHALOT=None
NOTIFYPUSHOVER=None
PUSHOVERAPI=None
NMAPRIORITY=None
NOTIFYBOXCAR2=None
BOXCAR2TOKEN=None
NOTIFYPLEX=None
PLEXSERVERHOST=None
PLEXSERVERPORT=None

DAEMON=None

DBFILE=None
DBVERSION=None

VERSIONURL=None
USERAGENT=None

SYSENCODING=None
MOBILEUSERAGENTS=None
MOBILEAUTOSUB=None

ENGLISH=None
DUTCH=None

def Initialize():
    global ROOTPATH, FALLBACKTOENG, DOWNLOADENG, DOWNLOADDUTCH, SUBENG, LOGFILE, SUBNL, LOGLEVEL, SKIPHIDDENDIRS, \
    LOGLEVELCONSOLE, LOGSIZE, LOGNUM, SKIPSHOW, SKIPSHOWUPPER, SKIPWEBDL, \
    USERNAMEMAPPING, USERNAMEMAPPINGUPPER, NAMEMAPPING, NAMEMAPPINGUPPER, USERADDIC7EDMAPPING, USERADDIC7EDMAPPINGUPPER, \
    SHOWID_CACHE, POSTPROCESSCMD, CONFIGFILE, WORKDIR, NOTIFYEN, NOTIFYNL, ENGLISHSUBDELETE, \
    MAILSRV, MAILFROMADDR, MAILTOADDR, MAILUSERNAME, CONFIGVERSION, CONFIGUPGRADED, HOMELAYOUTFIRST, \
    MAILPASSWORD, MAILSUBJECT, MAILENCRYPTION, \
    GROWLHOST, GROWLPORT, GROWLPASS, \
    TWITTERKEY, TWITTERSECRET, NMAAPI, NOTIFYMAIL, NOTIFYGROWL, NOTIFYTWITTER, NOTIFYNMA, \
    WANTEDQUEUE, ADDIC7EDAPI, \
    APIKEY, API, IMDBAPI, TIMEOUT, \
    APICALLSLASTRESET_TVDB, APICALLSLASTRESET_SUBSEEKER, APICALLSRESETINT_TVDB, APICALLSRESETINT_SUBSEEKER, \
    APICALLSMAX_TVDB, APICALLSMAX_SUBSEEKER, APICALLS_TVDB, APICALLS_SUBSEEKER, \
    SCHEDULERSCANDISK, SCHEDULERCHECKSUB, SCHEDULERDOWNLOADSUBS, DOWNLOADS_A7, DOWNLOADS_A7MAX, \
    DAEMON, NOTIFYPROWL, PROWLAPI, PROWLPRIORITY, PUSHALOTAPI, NOTIFYPUSHALOT, NOTIFYPUSHOVER, PUSHOVERAPI, \
    DBFILE, MOBILEUSERAGENTS, MOBILEAUTOSUB, NMAPRIORITY, \
    USERAGENT, VERSIONURL, \
    ENGLISH, DUTCH, PODNAPISILANG, SUBSCENELANG, BIERDOPJEMIRRORLANG, OPENSUBTITLESLANG, UNDERTEXTERLANG, \
    ADDIC7EDLANG, ADDIC7EDUSER, ADDIC7EDPASSWD, NOTIFYBOXCAR2, BOXCAR2TOKEN, \
    NOTIFYPLEX, PLEXSERVERHOST, PLEXSERVERPORT

    
    DBFILE = 'database.db'
    
    release = autosubversion.split(' ')[0]
    versionnumber = autosubversion.split(' ')[1]
    
    VERSIONURL = 'http://autosub-bootstrapbill.googlecode.com/hg/autosub/version.py'
    USERAGENT = 'AutoSub/' + versionnumber + release.lower()[0]

    WANTEDQUEUE = []

    APIKEY = "24430affe80bea1edf0e8413c3abf372a64afff2"
    TIMEOUT = 300 #default http timeout
    
    if CONFIGFILE==None:
        CONFIGFILE = "config.properties"
    
    Config.ReadConfig(CONFIGFILE)
    
    if CONFIGUPGRADED:
        print "AutoSub: Config seems to be upgraded. Writing config"
        Config.WriteConfig()
        print "AutoSub: Writing config done"
    
    API = "http://api.subtitleseeker.com/get/title_subtitles/?api_key=%s" %APIKEY
    IMDBAPI = "http://thetvdb.com/api/"

    MOBILEUSERAGENTS = ["midp", "240x320", "blackberry", "netfront", "nokia", "panasonic", 
                        "portalmmm", "sharp", "sie-", "sonyericsson", "symbian", "windows ce", 
                        "benq", "mda", "mot-", "opera mini", "philips", "pocket pc", "sagem",
                        "samsung", "sda", "sgh-", "vodafone", "xda", "palm", "iphone", "ipod", 
                        "ipad", "android", "windows phone"]
    MOBILEAUTOSUB = True
    
    APICALLSLASTRESET_TVDB = time.time()
    APICALLSLASTRESET_SUBSEEKER = time.time()
    
    APICALLSRESETINT_TVDB = 86400
    APICALLSRESETINT_SUBSEEKER = 86400
    
    APICALLSMAX_TVDB = 2500
    APICALLSMAX_SUBSEEKER = 1000
    
    APICALLS_TVDB = APICALLSMAX_TVDB
    APICALLS_SUBSEEKER = APICALLSMAX_SUBSEEKER      

    #Set the language paramater for the API query
    ENGLISH = 'English'
    DUTCH = 'Dutch'
    
    # Default value
    DOWNLOADS_A7MAX = 40
     
    
def initLogging(logfile):
    global LOGLEVEL, LOGSIZE, LOGNUM, LOGLEVELCONSOLE, \
    DAEMON
    
    # initialize logging
    # A log directory has to be created below the start directory
    log = logging.getLogger("thelogger")
    log.setLevel(LOGLEVEL)

    log_script = logging.handlers.RotatingFileHandler(logfile, 'a', LOGSIZE, LOGNUM)
    log_script_formatter=logging.Formatter('%(asctime)s %(levelname)s  %(message)s')
    log_script.setFormatter(log_script_formatter)
    log_script.setLevel(LOGLEVEL)
    log.addHandler(log_script)
    
    #CONSOLE log handler
    if DAEMON!=True:
        console = logging.StreamHandler()
        console.setLevel(LOGLEVELCONSOLE)
        # set a format which is simpler for console use
        formatter = logging.Formatter('%(asctime)s %(levelname)s  %(message)s')
        console.setFormatter(formatter)
        log.addHandler(console)
        
    return log