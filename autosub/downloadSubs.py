# Autosub downloadSubs.py - https://github.com/Donny87/autosub-bootstrapbill
#
# The Autosub downloadSubs module
# Scrapers are used for websites:
# Podnapisi.net, Subscene.com, Undertexter.se, OpenSubtitles
# and addic7ed.com
#
import autosub
import logging

from bs4 import BeautifulSoup
from zipfile import ZipFile
from StringIO import StringIO
import re 
from urlparse import urljoin

import os
import time
import tempfile
import autosub

from autosub.Db import lastDown
import autosub.OpenSubtitles as OS
import autosub.notify as notify
import autosub.Helpers

import xml.etree.cElementTree as ET
import library.requests as requests

# Settings
log = logging.getLogger('thelogger')

def getSoup(url):
    try:
        api = autosub.Helpers.API(url)
        soup = BeautifulSoup(api.resp.read())
        api.close()
        return soup
    except:
        log.error("getSoup: The server returned an error for request %s" % url)
        return None   

def unzip(url):
    # returns a file-like StringIO object    
    try:
        api = autosub.Helpers.API(url)
        tmpfile = StringIO(api.resp.read())
    except:
        log.debug("unzip: Zip file at %s couldn't be retrieved" % url)
        return None     
    try: 
        zipfile = ZipFile(tmpfile)
    except:
        log.debug("unzip: Expected a zip file but got error for link %s" % url)
        log.debug("unzip: %s is likely a dead link, this is known for opensubtitles.org" % url)
        return None

    nameList = zipfile.namelist()
    for name in nameList:
        # sometimes .nfo files are in the zip container
        tmpname = name.lower()
        if tmpname.endswith('srt'):
            subtitleFile = StringIO(zipfile.open(name).read())
            log.debug("unzip: Retrieving zip file for %s was succesful" % url )
            return subtitleFile
        else: 
            log.debug("unzip: No subtitle files was found in the zip archive for %s" % url)
            log.debug("unzip: Subtitle with different extention than .srt?")
            return None  

def openSubtitles(DownloadPage):

    log.debug("OpenSubtitles: DownloadPage: %s" % DownloadPage)
    # To prevent Captcha's from opensubtitles after every 25e dowload we do this:
    # Logout from opensubtiles
    # break the connection
    # wait one minute
    # Login again in the website

    if autosub.OPENSUBTILESDLCNT > 25:
        Referer = autosub.OPENSUBTTITLESSESSION.headers['referer']
        OS.OpenSubtitlesLogout()
        OS.TimeOut(60)
        OS.OpenSubtitlesLogin()
        autosub.OPENSUBTILESDLCNT = 0
        autosub.OPENSUBTTITLESSESSION.headers.update({'referer': Referer})
    try:
        OS.TimeOut()
        RequestResult = autosub.OPENSUBTTITLESSESSION.get(DownloadPage, timeout=10)
        autosub.OPENSUBTTITLESSESSION.headers.update({'referer': DownloadPage})
    except:
        log.debug('openSubtitles: Could not connect to OpenSubtitles.')
        return None
    if 'text/xml' not in RequestResult.headers['Content-Type']:
        log.error('openSubtitles: OpenSubtitles responded with an error')
        return None
    try:
        root = ET.fromstring(RequestResult.content)
    except:
        log.debug('openSubtitles: Serie with IMDB ID %s could not be found on OpenSubtitles.' %ImdbId)
        return None
    try:
        DownloadId = root.find('.//SubBrowse/Subtitle/SubtitleFile/File').get('ID')
    except:
        log.debug('openSubtitles: Could not get the download link from OpenSubtitles')
        return None
    try:
        DownloadUrl = autosub.OPENSUBTITLESDL + DownloadId
        OS.TimeOut()
        RequestResult = autosub.OPENSUBTTITLESSESSION.get( DownloadUrl, timeout=10)
        autosub.OPENSUBTTITLESSESSION.headers.update({'referer': DownloadUrl})
    except:
        log.debug('openSubtitles: Could not connect to Opensubtitles.org.')
        return None
    if RequestResult.headers['Content-Type'] == 'text/html':
        log.error('openSubtitles: Expected srt file but got HTML; report this!')
        log.debug("openSubtitles: Response content: %s" % r.content)
        return None
    return StringIO(RequestResult.content)

def undertexter(subSeekerLink):
    engSub = 'http://www.engsub.net/getsub.php?id='    
    soup = getSoup(subSeekerLink)
    if soup:
        tag = soup.find('iframe', src=True)
        link = tag['src'].strip('/')     
    else:
        log.error("Undertexter: Failed to extract download link using SubtitleSeekers's link")        
        return None
    try:
        zipUrl = engSub + link.split('/')[3].encode('utf8')
    except:
        log.error("Undertexter: Something went wrong with parsing the downloadlink")        
        return None
    subtitleFile = unzip(zipUrl)
    return subtitleFile

def podnapisi(subSeekerLink):
    baseLink = 'http://www.podnapisi.net/'
    soup = getSoup(subSeekerLink)    
    if soup:
        linkToPodnapisi = soup.select('p > a[href]')[0]['href'].strip('/')
    else:
        log.error("Podnapisi: Failed to find the redirect link using SubtitleSeekers's link")        
        return None
    if baseLink in linkToPodnapisi:
        soup = getSoup(linkToPodnapisi)
    else:
        log.error("Podnapisi: Failed to find the Podnapisi page.")
        return None
    if soup:
        downloadLink = soup.find('form', class_='form-inline download-form').get('action')
    else:
        log.error("Podnapisi: Failed to find the download link on Podnapisi page")     
        return None
    zipUrl = urljoin(baseLink,downloadLink.encode('utf8'))
    subtitleFile = unzip(zipUrl)
    return subtitleFile

def subscene(subSeekerLink):
    baseLink = 'http://subscene.com/'
    soup = getSoup(subSeekerLink)
    if soup:
        linkToSubscene = soup.select('p > a[href]')[0]['href'].strip('/')
    else:
        log.error("Subscene: Failed to find the redirect link using SubtitleSeekers's link")        
        return None
    if baseLink in linkToSubscene :
        soup = getSoup(linkToSubscene)
    else:
        log.error("subscene: Failed to find the subscene page.")
        return None
    if soup:
        downloadLink = soup.select('div.download > a[href]')[0]['href'].strip('/')
    else:
        log.error("Subscene: Failed to find the download link on Subscene.com")        
        return None
    zipUrl = urljoin(baseLink,downloadLink.encode('utf8'))
    subtitleFile = unzip(zipUrl)
    return subtitleFile               

def addic7ed(url):
    subtitleFile = autosub.ADDIC7EDAPI.download(url)
    if subtitleFile:
        autosub.DOWNLOADS_A7 += 1
        log.debug("addic7ed: Your current Addic7ed download count is: %s" % autosub.DOWNLOADS_A7)
        return StringIO(subtitleFile)
    return None

def GetSubFile(StringSub,FileSub):
# this routine tries to download the sub and check if it is a correct sub
# this is done by reading the first lines (max 5) and check the line format
    SubOk = False
    for Count in range (1,5):
        Line = StringSub.readline()
        if Line[:1] == '1':
            Line = StringSub.readline()
            if re.match("\d{2}:\d{2}:\d{2},\d{3}\s*-->\s*\d{2}:\d{2}:\d{2},\d{3}",Line):          
                try:
                    log.debug("downloadSubs: Saving the subtitle file %s to the filesystem." % FileSub)
                    StringSub.seek(0)
                    fp = open(FileSub, 'wb')
                    fp.write(StringSub.getvalue())
                    fp.write('\n') 
                    fp.close()
                    SubOk = True
                    StringSub.close()
                    break
                except IOError as error :
                    log.error("downloadSubs: Could not write subtitle file. %s" % error.strerror)
    if not SubOk:
        StringSub.close()
        return False
    else:
        return True

def GetSubFile(StringSub,FileSub):
# this routine tries to download the sub and check if it is a correct sub
# this is done by reading the first lines (max 5) and check the line format
    SubOk = False
    for Count in range (1,5):
        Line = StringSub.readline()
        if Line[:1] == '1':
            Line = StringSub.readline()
            if re.match("\d{2}:\d{2}:\d{2},\d{3}\s*-->\s*\d{2}:\d{2}:\d{2},\d{3}",Line):          
                try:
                    log.debug("downloadSubs: Saving the subtitle file %s to the filesystem." % FileSub)
                    StringSub.seek(0)
                    fp = open(FileSub, 'wb')
                    fp.write(StringSub.getvalue())
                    fp.write('\n') 
                    fp.close()
                    SubOk = True
                    StringSub.close()
                    break
                except IOError as error :
                    log.error("downloadSubs: Could not write subtitle file. %s" % error.strerror)
    if not SubOk:
        StringSub.close()
        return False
    else:
        return True

def DownloadSub(allResults, a7Response, downloadItem):    
    
    log.debug("downloadSubs: Starting DownloadSub function")    
    
    if not 'destinationFileLocationOnDisk' in downloadItem.keys():
        log.error("downloadSub: No locationOnDisk found at downloadItem, skipping")
        return False
    
    log.debug("downloadSubs: Download dict seems OK. Dumping it for debug: %r" % downloadItem) 
    destsrt = downloadItem['destinationFileLocationOnDisk']
    destdir = os.path.split(destsrt)[0]
    if not os.path.exists(destdir):
        log.debug("checkSubs: no destination directory %s" %destdir)
        return False
    elif not os.path.lexists(destdir):
        log.debug("checkSubs: no destination directory %s" %destdir)
        return False        
    
    HIfallback = {}
    fileStringIO = None
    Downloaded = False 
    for result in allResults:   
        url = result['url']
        release = result['releasename']
        website = result['website']             
       
        log.debug("downloadSubs: Trying to download subtitle from %s using this link %s" % (website,url))      

        if website == 'undertexter.se':
            log.debug("downloadSubs: Scraper for Undertexter.se is chosen for subtitle %s" % destsrt)
            fileStringIO = undertexter(url) 
        elif website == 'subscene.com':    
            log.debug("downloadSubs: Scraper for Subscene.com is chosen for subtitle %s" % destsrt)
            fileStringIO = subscene(url)
        elif website == 'podnapisi.net':
            log.debug("downloadSubs: Scraper for Podnapisi.net is chosen for subtitle %s" % destsrt)
            fileStringIO = podnapisi(url)
        elif website == 'opensubtitles.org':
            log.debug("downloadSubs: Scraper for opensubtitles.org is chosen for subtitle %s" % destsrt)
            fileStringIO = openSubtitles(url)
        elif website == 'addic7ed.com' and a7Response:
            log.debug("downloadSubs: Scraper for Addic7ed.com is chosen for subtitle %s" % destsrt)
            if result['HI']:
                if not HIfallback:
                    log.debug("downloadSubs: Addic7ed HI version: store as fallback")
                    HIfallback = result            
                continue
            fileStringIO = addic7ed(url)   
        else:
            log.error("downloadSubs: %s is not recognized. Something went wrong!" % website)
        if fileStringIO:
            log.debug("downloadSubs: Subtitle is downloading from %s" % website)      
            if not GetSubFile(fileStringIO,destsrt):
                if website == 'opensubtitles.org':
                    log.error("downloadSubs: Downloaded file from opensubtitles is not a sub file, try to avoid Captcha")
                    Referer = autosub.OPENSUBTTITLESSESSION.headers['referer']
                    OS.OpenSubtitlesLogout()
                    OS.TimeOut(60)
                    OS.OpenSubtitlesLogin()
                    autosub.OPENSUBTTITLESSESSION.headers.update({'referer': Referer})
                    if not GetSubFile(fileStringIO,destsrt):
                        log.error("downloadSubs: Downloaded file is still not a correct .srt file. Skipping it!")
                else:
                    log.error("downloadSubs: Sub from %s not a correct .srt file. Skipping it." % website)
            else:
                Downloaded = True
                log.info("downloadSubs: Subtitle %s is downloaded from %s" % (destsrt,website))
                break
        else:
            if HIfallback:
                log.debug("downloadSubs: Downloading HI subtitle as fallback")
                fileStringIO = addic7ed(url)
                if not GetSubFile(fileStringIO,destsrt):
                    log.error("downloadSubs: Hearing impact sub from %s not a correct .srt file. Skipping it." % website)
                else:
                    Downloaded = True
                    release = HIfallback['releasename']
                    website = HIfallback['website']
                    break
    if not Downloaded:
        log.error("downloadSubs: Could not download a correct subtitle file for %s" % destsrt)
        return False

    downloadItem['subtitle'] = "%s downloaded from %s" % (release,website)
    downloadItem['timestamp'] = time.strftime('%Y-%m-%d %H:%M:%S')
    
    lastDown().setlastDown(dict = downloadItem)
    # Send notification        
    notify.notify(downloadItem['downlang'], destsrt, downloadItem["originalFileLocationOnDisk"], website)
    if autosub.POSTPROCESSCMD:
        postprocesscmdconstructed = autosub.POSTPROCESSCMD + ' "' + downloadItem["destinationFileLocationOnDisk"] + '" "' + downloadItem["originalFileLocationOnDisk"] + '" "' + downloadItem["downlang"] + '" "' + downloadItem["title"] + '" "' + downloadItem["season"] + '" "' + downloadItem["episode"] + '" '
        log.debug("downloadSubs: Postprocess: running %s" % postprocesscmdconstructed)
        log.info("downloadSubs: Running PostProcess")
        postprocessoutput, postprocesserr = autosub.Helpers.RunCmd(postprocesscmdconstructed)
        log.debug("downloadSubs: PostProcess Output:% s" % postprocessoutput)
        if postprocesserr:
            log.error("downloadSubs: PostProcess: %s" % postprocesserr)
            #log.debug("downloadSubs: PostProcess Output:% s" % postprocessoutput)
    
    log.debug('downloadSubs: Finished for %s' % downloadItem["originalFileLocationOnDisk"])
    return True