import cherrypy
import logging

log = logging.getLogger('thelogger')

try:
    from Cheetah.Template import Template
except:
    print "ERROR!!! Cheetah is not installed yet. Download it from: http://pypi.python.org/pypi/Cheetah/2.4.4"

import threading
import time
import autosub.Config
from autosub.Db import idCache, lastDown

import autosub.notify as notify

import autosub.Helpers

def redirect(abspath, *args, **KWs):
    assert abspath[0] == '/'
    raise cherrypy.HTTPRedirect(autosub.WEBROOT + abspath, *args, **KWs)

# TODO: Create webdesign
class PageTemplate (Template):
    #Placeholder for future, this object can be used to add stuff to the template
    pass

class Config:
    @cherrypy.expose
    def index(self):
        redirect("/config/settings")

    @cherrypy.expose
    def info(self):
        tmpl = PageTemplate(file="interface/templates/config-info.tmpl")
        return str(tmpl)  

    @cherrypy.expose
    def liveinfo(self):
        tmpl = PageTemplate(file="interface/templates/config-liveinfo.tmpl")
        return str(tmpl)  

    @cherrypy.expose
    def settings(self):
        tmpl = PageTemplate(file="interface/templates/config-settings.tmpl")
        return str(tmpl)  

    @cherrypy.expose
    def notifications(self):
        tmpl = PageTemplate(file="interface/templates/config-notification.tmpl")
        return str(tmpl)  

    @cherrypy.expose
    def skipShow(self, title, season=None):
        if not season:
            tmpl = PageTemplate(file="interface/templates/config-skipshow.tmpl")
            tmpl.title = title
            return str(tmpl)
        else:
            tmpl = PageTemplate(file="interface/templates/home.tmpl")
            if not title:
                raise cherrypy.HTTPError(400, "No show supplied")
            if title.upper() in autosub.SKIPSHOWUPPER:
                for x in autosub.SKIPSHOWUPPER[title.upper()]:
                    if x == season or x == '0':
                        tmpl.message = "This show is already being skipped"
                        return str(tmpl)
                if season == '00':
                    season = season + ',' + ','.join(autosub.SKIPSHOWUPPER[title.upper()])
                else:
                    season = str(int(season)) + ',' + ','.join(autosub.SKIPSHOWUPPER[title.upper()])
            else:
                if not season == '00':
                    season = str(int(season))
            autosub.Config.SaveToConfig('skipshow',title,season)
            autosub.Config.applyskipShow()
            
            tmpl.message = "<strong>%s</strong> season <strong>%s</strong> will be skipped.<br> This will happen the next time that Auto-Sub checks for subtitles" % (title.title(), season)
            tmpl.displaymessage = "Yes"
            tmpl.modalheader = "Information"
            return str(tmpl)
    
    @cherrypy.expose
    def applyConfig(self):
        autosub.Config.applyAllSettings()
        tmpl = PageTemplate(file="interface/templates/home.tmpl")
        tmpl.message = "Settings read & applied"
        tmpl.displaymessage = "Yes"
        tmpl.modalheader = "Information"
        return str(tmpl)

    @cherrypy.expose  
    def saveConfig(self, subeng, checksub, scandisk, skiphiddendirs, subnl, postprocesscmd, 
                   path, logfile, rootpath, launchbrowser, fallbacktoeng, downloadeng, englishsubdelete, username, 
                   password, webroot, skipshow, lognum, loglevelconsole, logsize, loglevel, 
                   webserverip, webserverport, usernamemapping, notifyen, notifynl, homelayoutfirst,
                   podnapisilang, subscenelang, bierdopjemirrorlang, opensubtitleslang, undertexterlang,
                   mmssource = None, mmsquality = None, mmscodec = None, mmsrelease = None):
        # Set all internal variables
        autosub.PATH = path
        autosub.ROOTPATH = rootpath
        autosub.LOGFILE = logfile
        autosub.FALLBACKTOENG = fallbacktoeng
        autosub.DOWNLOADENG = downloadeng
        autosub.SUBENG = subeng
        autosub.SUBNL = subnl
        autosub.NOTIFYEN = notifyen
        autosub.NOTIFYNL = notifynl
        autosub.POSTPROCESSCMD = postprocesscmd
        autosub.LAUNCHBROWSER = launchbrowser
        autosub.SKIPHIDDENDIRS = skiphiddendirs
        autosub.HOMELAYOUTFIRST = homelayoutfirst
        autosub.ENGLISHSUBDELETE = englishsubdelete
        autosub.PODNAPISILANG = podnapisilang
        autosub.SUBSCENELANG = subscenelang
        autosub.BIERDOPJEMIRRORLANG = bierdopjemirrorlang
        autosub.OPENSUBTITLESLANG = opensubtitleslang
        autosub.UNDERTEXTERLANG = undertexterlang
        
        autosub.MINMATCHSCORE = 0
        if mmssource:
            autosub.MINMATCHSCORE += 8
        if mmsquality:
            autosub.MINMATCHSCORE += 4
        if mmscodec:
            autosub.MINMATCHSCORE += 2
        if mmsrelease:
            autosub.MINMATCHSCORE += 1 
               
        autosub.SCHEDULERSCANDISK = int(scandisk)
        autosub.SCHEDULERCHECKSUB = int(checksub)
        autosub.LOGLEVEL = int(loglevel)
        autosub.LOGNUM = int(lognum)
        autosub.LOGSIZE = int(logsize)
        autosub.LOGLEVELCONSOLE = int(loglevelconsole)
        autosub.WEBSERVERIP = webserverip
        autosub.WEBSERVERPORT = int(webserverport)
        autosub.USERNAME = username
        autosub.PASSWORD = password
        autosub.WEBROOT = webroot
        autosub.SKIPSHOW = autosub.Config.stringToDict(skipshow)
        autosub.USERNAMEMAPPING = autosub.Config.stringToDict(usernamemapping)

        # Now save to the configfile
        message = autosub.Config.WriteConfig(configsection="")

        tmpl = PageTemplate(file="interface/templates/config-settings.tmpl")
        tmpl.message = message
        tmpl.displaymessage = "Yes"
        tmpl.modalheader = "Information"
        return str(tmpl)

    @cherrypy.expose
    def saveNotification(self, notifymail, notifygrowl, notifynma, notifytwitter, mailsrv, mailfromaddr, 
                         mailtoaddr, mailusername, mailpassword, mailsubject, mailencryption, mailauth, 
                         growlhost, growlport, growlpass, nmaapi, twitterkey, twittersecret, notifyprowl, 
                         prowlapi, prowlpriority, notifypushalot, pushalotapi, notifypushover, pushoverapi, 
                         nmapriority):

        # Set all internal notify variables
        autosub.NOTIFYMAIL = notifymail
        autosub.MAILSRV = mailsrv
        autosub.MAILFROMADDR = mailfromaddr
        autosub.MAILTOADDR = mailtoaddr
        autosub.MAILUSERNAME = mailusername
        autosub.MAILPASSWORD = mailpassword
        autosub.MAILSUBJECT = mailsubject
        autosub.MAILENCRYPTION = mailencryption
        autosub.MAILAUTH = mailauth
        autosub.NOTIFYGROWL = notifygrowl
        autosub.GROWLHOST = growlhost
        autosub.GROWLPORT = growlport
        autosub.GROWLPASS = growlpass
        autosub.NOTIFYNMA = notifynma
        autosub.NMAAPI = nmaapi
        autosub.NMAPRIORITY = int(nmapriority)
        autosub.NOTIFYTWITTER = notifytwitter
        autosub.TWITTERKEY = twitterkey
        autosub.TWITTERSECRET = twittersecret
        autosub.NOTIFYPROWL = notifyprowl
        autosub.PROWLAPI = prowlapi
        autosub.PROWLPRIORITY = int(prowlpriority)
        autosub.NOTIFYPUSHALOT = notifypushalot
        autosub.PUSHALOTAPI = pushalotapi
        autosub.NOTIFYPUSHOVER = notifypushover
        autosub.PUSHOVERAPI = pushoverapi

        # Now save to the configfile
        message = autosub.Config.WriteConfig(configsection="notifications")

        tmpl = PageTemplate(file="interface/templates/config-notification.tmpl")
        tmpl.message = message
        tmpl.displaymessage = "Yes"
        tmpl.modalheader = "Information"
        return str(tmpl)

    @cherrypy.expose
    def flushCache(self):
        idCache().flushCache()
        message = 'ID Cache flushed'
        tmpl = PageTemplate(file="interface/templates/home.tmpl")
        tmpl.message = message
        tmpl.displaymessage = "Yes"
        tmpl.modalheader = "Information"
        return str(tmpl)
    
    @cherrypy.expose
    def flushLastdown(self):
        lastDown().flushLastdown()
        message = 'Downloaded subtitles database flushed'
        tmpl = PageTemplate(file="interface/templates/home.tmpl")
        tmpl.message = message
        tmpl.displaymessage = "Yes"
        tmpl.modalheader = "Information"
        return str(tmpl)
    
    @cherrypy.expose
    def checkVersion(self):
        checkversion = autosub.Helpers.CheckVersion()
        
        if checkversion == 0:
            message = 'You are running the latest version!'
        elif checkversion == 1:
            message = 'There is a new version available!'
        elif checkversion == 2:
            message = 'There is a new major release available for your version.<br> For example, you are running an Alpha version and there is a Beta version available.'
        elif checkversion == 3:
            message = 'There is a newer testing version available. Only the risk-takers should upgrade!'
        elif checkversion == 4:
            message = 'What are you doing here??? It is time to upgrade!'
        else:
            message = 'Something went wrong there, is Google-Project reachable?<br> Or are you running a really old release?'

        tmpl = PageTemplate(file="interface/templates/home.tmpl")
        tmpl.message = message
        tmpl.displaymessage = "Yes"
        tmpl.modalheader = "Information"
        
        return str(tmpl)   
    
    @cherrypy.expose
    def testPushalot(self, pushalotapi):
        
        log.info("Notification: Testing Pushalot")
        result = notify.pushalot.test_notify(pushalotapi)
        if result:
            return "Auto-Sub successfully sent a test message with <strong>Pushalot</strong>."
        else:
            return "Failed to send a test message with <strong>Pushalot</strong>."
    
    @cherrypy.expose
    def testMail(self, mailsrv, mailfromaddr, mailtoaddr, mailusername, mailpassword, mailsubject, mailencryption, mailauth):  
        
        log.info("Notification: Testing Mail")
        result = notify.mail.test_notify(mailsrv, mailfromaddr, mailtoaddr, mailusername, mailpassword, mailsubject, mailencryption, mailauth)
        if result:
            return "Auto-Sub successfully sent a test message with <strong>Mail</strong>."
        else:
            return "Failed to send a test message with <strong>Mail</strong>."
    
    @cherrypy.expose
    def testTwitter(self, twitterkey, twittersecret):
        
        log.info("Notification: Testing Twitter")  
        result = notify.twitter.test_notify(twitterkey, twittersecret)
        if result:
            return "Auto-Sub successfully sent a test message with <strong>Twitter</strong>."
        else:
            return "Failed to send a test message with <strong>Twitter</strong>."
    
    @cherrypy.expose
    def testNotifyMyAndroid(self, nmaapi, nmapriority):
        
        log.info("Notification: Testing Notify My Android")     
        result = notify.nma.test_notify(nmaapi, nmapriority)
        if result:
            return "Auto-Sub successfully sent a test message with <strong>Notify My Android</strong>."
        else:
            return "Failed to send a test message with <strong>Notify My Android</strong>."
    
    @cherrypy.expose
    def testPushover(self, pushoverapi):
        
        log.info("Notification: Testing Pushover")
        result = notify.pushover.test_notify(pushoverapi)
        if result:
            return "Auto-Sub successfully sent a test message with <strong>Pushover</strong>."
        else:
            return "Failed to send a test message with <strong>Pushover</strong>."
    
    @cherrypy.expose
    def testGrowl(self, growlhost, growlport, growlpass):
        
        log.info("Notification: Testing Growl")
        result = notify.growl.test_notify(growlhost, growlport, growlpass)
        if result:
            return "Auto-Sub successfully sent a test message with <strong>Growl</strong>."
        else:
            return "Failed to send a test message with <strong>Growl</strong>."
    
    @cherrypy.expose
    def testProwl(self, prowlapi, prowlpriority):
        
        log.info("Notification: Testing Prowl")
        result = notify.prowl.test_notify(prowlapi, prowlpriority)
        if result:
            return "Auto-Sub successfully sent a test message with <strong>Prowl</strong>."
        else:
            return "Failed to send a test message with <strong>Prowl</strong>."
    
    @cherrypy.expose
    def regTwitter(self, token_key=None, token_secret=None, token_pin=None):
        import library.oauth2 as oauth
        import autosub.notify.twitter as notifytwitter 
        try:
            from urlparse import parse_qsl
        except:
            from cgi import parse_qsl
        
        if not token_key and not token_secret:
            consumer = oauth.Consumer(key=notifytwitter.CONSUMER_KEY, secret=notifytwitter.CONSUMER_SECRET)
            oauth_client = oauth.Client(consumer)
            response, content = oauth_client.request(notifytwitter.REQUEST_TOKEN_URL, 'GET')
            if response['status'] != '200':
                message = "Something went wrong when trying to register Twitter"
                tmpl = PageTemplate(file="interface/templates/config-settings.tmpl")
                tmpl.message = message
                tmpl.displaymessage = "Yes"
                tmpl.modalheader = "Error"
                return str(tmpl)
            else:
                request_token = dict(parse_qsl(content))
                tmpl = PageTemplate(file="interface/templates/config-twitter.tmpl")
                tmpl.url = notifytwitter.AUTHORIZATION_URL + "?oauth_token=" + request_token['oauth_token']
                token_key = request_token['oauth_token']
                token_secret = request_token['oauth_token_secret']
                tmpl.token_key = token_key
                tmpl.token_secret = token_secret
                return str(tmpl)
        
        if token_key and token_secret and token_pin:
            
            token = oauth.Token(token_key, token_secret)
            token.set_verifier(token_pin)
            consumer = oauth.Consumer(key=notifytwitter.CONSUMER_KEY, secret=notifytwitter.CONSUMER_SECRET)
            oauth_client2 = oauth.Client(consumer, token)
            response, content = oauth_client2.request(notifytwitter.ACCESS_TOKEN_URL, method='POST', body='oauth_verifier=%s' % token_pin)
            access_token = dict(parse_qsl(content))

            if response['status'] != '200':
                message = "Something went wrong when trying to register Twitter"
                tmpl = PageTemplate(file="interface/templates/config-settings.tmpl")
                tmpl.message = message
                tmpl.displaymessage = "Yes"
                tmpl.modalheader = "Error"
                return str(tmpl)
            else:
                autosub.TWITTERKEY = access_token['oauth_token']
                autosub.TWITTERSECRET = access_token['oauth_token_secret']
                
                message = "Twitter registration complete.<br> Remember to save your configuration and test Twitter!"
                tmpl = PageTemplate(file="interface/templates/config-settings.tmpl")
                tmpl.message = message
                tmpl.displaymessage = "Yes"
                tmpl.modalheader = "Information"
                return str(tmpl)
                

class Home:
    @cherrypy.expose
    def index(self):
        useragent = cherrypy.request.headers.get("User-Agent", '')
        tmpl = PageTemplate(file="interface/templates/home.tmpl")
        if autosub.Helpers.CheckMobileDevice(useragent) and autosub.MOBILEAUTOSUB:
            tmpl = PageTemplate(file="interface/templates/mobile/home.tmpl")
        return str(tmpl)
    
    @cherrypy.expose
    def runNow(self):
        #time.sleep is here to prevent a timing issue, where checksub is runned before scandisk
        useragent = cherrypy.request.headers.get("User-Agent", '')
        tmpl = PageTemplate(file="interface/templates/home.tmpl")
        if autosub.Helpers.CheckMobileDevice(useragent) and autosub.MOBILEAUTOSUB:
            tmpl = PageTemplate(file="interface/templates/mobile/message.tmpl")

        if not hasattr(autosub.CHECKSUB, 'runnow'):
            tmpl.message = "Auto-Sub is already running, no need to rerun"
            tmpl.displaymessage = "Yes"
            tmpl.modalheader = "Information"
            return str(tmpl)

        autosub.SCANDISK.runnow = True
        time.sleep(5)
        autosub.CHECKSUB.runnow = True

        tmpl.message = "Auto-Sub is now checking for subtitles!"
        tmpl.displaymessage = "Yes"
        tmpl.modalheader = "Information"

        return str(tmpl)

    @cherrypy.expose
    def exitMini(self):
        if autosub.MOBILEAUTOSUB:
            autosub.MOBILEAUTOSUB = False
            redirect("/home")
        else:
            autosub.MOBILEAUTOSUB = True
            redirect("/home")
    
    @cherrypy.expose
    def shutdown(self):
        tmpl = PageTemplate(file="interface/templates/stopped.tmpl")
        threading.Timer(2, autosub.AutoSub.stop).start()
        return str(tmpl)

class Log:
    @cherrypy.expose
    def index(self, loglevel = ''):
        redirect("/log/viewLog")
    
    @cherrypy.expose
    def viewLog(self, loglevel = ''):
        tmpl = PageTemplate(file="interface/templates/viewlog.tmpl")
        if loglevel == '':
            tmpl.loglevel = 'All'
        else:
            tmpl.loglevel = loglevel
        result = autosub.Helpers.DisplayLogFile(loglevel)
        tmpl.logentries = result
        
        return str(tmpl)   
    
    @cherrypy.expose
    def clearLog(self):
        autosub.Helpers.ClearLogFile()
        tmpl = PageTemplate(file="interface/templates/home.tmpl")
        tmpl.message = "Logfile has been cleared!"
        tmpl.displaymessage = "Yes"
        tmpl.modalheader = "Information"
        return str(tmpl)

class Mobile:
    @cherrypy.expose
    def index(self):
        tmpl = PageTemplate(file="interface/templates/mobile/home.tmpl")
        return str(tmpl)

class WebServerInit():
    @cherrypy.expose
    def index(self):
        redirect("/home")
    
    home = Home()
    config = Config()
    log = Log()
    mobile = Mobile()

    def error_page_401(status, message, traceback, version):
        tmpl = PageTemplate(file="interface/templates/home.tmpl")
        message = "You don't have access to this resource.<br><br><center><textarea rows='15' wrap='off' class='spancustom'>%s</textarea></center>" %traceback
        tmpl.message = message
        tmpl.displaymessage = "Yes"
        tmpl.modalheader = "Error %s" %status
        return str(tmpl)
    
    def error_page_404(status, message, traceback, version):
        tmpl = PageTemplate(file="interface/templates/home.tmpl")
        message = "Page could not be found.<br><br><center><textarea rows='15' wrap='off' class='spancustom'>%s</textarea></center>" %traceback
        tmpl.message = message
        tmpl.displaymessage = "Yes"
        tmpl.modalheader = "Error %s" %status
        return str(tmpl)
    
    def error_page_500(status, message, traceback, version):
        tmpl = PageTemplate(file="interface/templates/home.tmpl")
        message = "Try again. If this error doesn't go away, please report the issue.<br><br><center><textarea rows='15' wrap='off' class='spancustom'>%s</textarea></center>" %traceback
        tmpl.message = message
        tmpl.displaymessage = "Yes"
        tmpl.modalheader = "Error %s" %status
        return str(tmpl)

    _cp_config = {'error_page.401':error_page_401,
                  'error_page.404':error_page_404,
                  'error_page.500':error_page_500}
