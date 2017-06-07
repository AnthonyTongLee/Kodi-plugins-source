# -*- coding: utf-8 -*-
# Food Network Kodi Video Addon
#
from t1mlib import t1mAddon
import json
import re
import os
import datetime
import urllib
import urllib2
import xbmc
import xbmcplugin
import xbmcgui
import sys

qp  = urllib.quote_plus
uqp = urllib.unquote_plus
UTF8     = 'utf-8'

STUDIO = 'Food Network'


class myAddon(t1mAddon):


  def getAddonMenu(self,url,ilist):
    html = self.getRequest('http://www.foodnetwork.com/videos/full-episodes/')
    mediaBlocks = re.compile('<h4 class="m-MediaBlock__a-Headline">(.+?)</h4', re.DOTALL).findall(html)
    linkRx = re.compile('<a href="(.+?)"')
    textRx = re.compile('<span class="m-MediaBlock__a-HeadlineText".*?>(.+?)</span')

    infoList={}
    for mediablock in mediaBlocks:
      #self.log("parse:"+str(mediablock))
      if mediablock is None:
        continue

      linkMatch = linkRx.search(mediablock)
      textMatch = textRx.search(mediablock)
      if linkMatch is None or textMatch is None:
        continue
      name = textMatch.group(1)
      url = linkMatch.group(1)
      if "full-episodes" not in url:
        continue
      #self.log("getAddonMenu  name:"+str(name)+"  url:"+str(url))
      thumb = self.addonIcon
      fanart = None
      ilist = self.addMenuItem(name,'GE', ilist, url, thumb, fanart, infoList, isFolder=True)
    return(ilist)


  def getAddonEpisodes(self,url,ilist):
    html = self.getRequest(url)
    videoJsonMatch = re.compile('"videos": \[(.+?)\]', re.DOTALL).search(html)
    if videoJsonMatch is None:
      self.log("No episode json blob")
      return(ilist)

    jsonStr = "{\"videos\":["+videoJsonMatch.group(1)+"]}"
    self.log(jsonStr)
    jobj = json.loads(jsonStr)
    for b in jobj['videos']:
       url     = b['releaseUrl']
       name    = b['title']
       thumb   = b['thumbnailUrl']
       fanart  = thumb
       infoList = {}
       infoList['Duration']    = b['length']
       infoList['Title']       = b['title']
       infoList['Studio']      = STUDIO
       infoList['Plot']        = b["description"]
       infoList['TVShowTitle'] = b["showTitle"]
       infoList['MPAA']        = 'TV-PG'
       infoList['mediatype']   = 'episode'
       ilist = self.addMenuItem(name,'GV', ilist, url, thumb, fanart, infoList, isFolder=False)
    return(ilist)


  def getAddonVideo(self,url):
   html   = self.getRequest(uqp(url))
   m    = re.compile('<video src="(.+?)"',re.DOTALL).search(html)
   url = m.group(1)
   suburl = None
   subs   = re.compile('<textstream src="(.+?)"',re.DOTALL).findall(html[m.start(1):])
   for st in subs:
      if '.srt' in st:
         suburl = st
         break

   liz = xbmcgui.ListItem(path = url)
   if suburl: liz.setSubtitles([suburl])
   xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, liz)

