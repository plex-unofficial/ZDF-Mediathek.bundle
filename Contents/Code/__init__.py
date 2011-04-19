# +++++ ZDF Mediathek Plugin for Plex +++++
#
# Version 1.0
#
# (c) 2010 by Marcel Dischinger (http://www.digital-tea.net)
# Initial version based on code by Sebastian Majstorovic
# 
# Licensed under the GPL, Version 3.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#  
#    http://www.gnu.org/licenses/gpl-3.0-standalone.html
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Artwork (folder 'Resources'): (c) ZDF

# TODO
# - Support Bilderserien

from PMS import *
from PMS.Objects import *
from PMS.Shortcuts import *

####################################################################################################

# Number of videos displayed per show
MAX_ENTRIES = 50 
# Do not display trailers
FILTER_TRAILERS = True

# These shows act as shortcuts / favorites
# You can add your favorite show using the links at
#    http://www.zdf.de/ZDFmediathek/hauptnavigation/sendung-a-bis-z?flash=off
# Format: ['title', 'URL', 'ShowIcon', 'ShowArtwork']
SHOWS = [
# Examples: (note: artwork is not included!)
#  ['Heute Show', "http://www.zdf.de/ZDFmediathek/kanaluebersicht/aktuellste/760014?bc=saz;saz2&flash=off", 'heuteshow.png'],
#  ['History', "http://www.zdf.de/ZDFmediathek/kanaluebersicht/aktuellste/496?bc=saz;saz2&flash=off", 'history.png'],
#  ['Leschs Kosmos', "http://www.zdf.de/ZDFmediathek/kanaluebersicht/aktuellste/925180?bc=saz;saz3&flash=off", 'leschskosmos.png'],
#  ['Neues aus der Anstalt', "http://www.zdf.de/ZDFmediathek/kanaluebersicht/aktuellste/508?bc=saz;saz0&flash=off", 'neuesausderanstalt.png'],
#  ['Terra X', "http://www.zdf.de/ZDFmediathek/kanaluebersicht/aktuellste/330?bc=saz;saz6&flash=off", 'terrax.png']
]

CATEGORY = [
  ['Sendungen A-Z', "http://www.zdf.de/ZDFmediathek/hauptnavigation/sendung-a-bis-z?flash=off"],
  ['Sendungen der letzten 7 Tage', "http://www.zdf.de/ZDFmediathek/hauptnavigation/sendung-verpasst?flash=off"],
  ['Live', "http://www.zdf.de/ZDFmediathek/hauptnavigation/live?flash=off"]
]

VIDEO_PREFIX = "/video/zdfmediathek"

NAME = L('Title')

ART = 'art-default.jpg'
ICON = 'icon-default.png'

BASE_URL = "http://www.zdf.de"


####################################################################################################

def Start():

    Plugin.AddPrefixHandler(VIDEO_PREFIX, VideoMainMenu, L('VideoTitle'), ICON, ART)

    Plugin.AddViewGroup("InfoList", viewMode="InfoList", mediaType="items")
    Plugin.AddViewGroup("List", viewMode="List", mediaType="items")

    MediaContainer.art = R(ART)
    MediaContainer.title1 = NAME
    DirectoryItem.thumb = R(ICON)

def VideoMainMenu():
    dir = MediaContainer(viewGroup="List")

    for page in CATEGORY :
      dir.Append(Function(DirectoryItem(VideoSubMenu, title = page[0]), listUrl = page[1]))
    for show in SHOWS :
      show[1] = show[1] + "&teaserListIndex="+str(MAX_ENTRIES*2)
      if(len(show) > 2 and show[2] != '') :
	if((len(show) > 3) and (show[3] != '')) :
	  dir.Append(Function(DirectoryItem(DateMenu, title = show[0], thumb = R(show[2]), art = R(show[3])), arg = show[1]))
	else :
	  dir.Append(Function(DirectoryItem(DateMenu, title = show[0], thumb = R(show[2])), arg = show[1]))
      else :
	dir.Append(Function(DirectoryItem(DateMenu, title = show[0]), arg = show[1]))

    return dir


def VideoSubMenu(sender, listUrl):
  dir = MediaContainer(viewGroup="List")
  site = XML.ElementFromURL(listUrl, True)
  
  dateElements = site.xpath("//ul[@class='subNavi']/li/a")
  elementsCount = len(dateElements)
  for i in range(0, elementsCount):
    dateElement = dateElements[i]
    url = str(dateElement.xpath('@href')[0])
    date = dateElement.text
    description = date[2:]
    
    # Remove podcasts directory
    if('Podcasts' in description) :
      continue
    
    if('sendung-a-bis-z' in listUrl) :
      dir.Append(Function(DirectoryItem(ShowsMenu, title = description), arg = url))
    else :
      dir.Append(Function(DirectoryItem(DateMenu, title = description), arg = url))
    
  return dir


def ShowsMenu(sender, arg):
  dir = MediaContainer(viewGroup="InfoList")
  
  if(arg.startswith('http://')) :
    site = XML.ElementFromURL(arg, True)
    #Log("DateMenu for " +arg)
  else :
    site = XML.ElementFromURL(BASE_URL + arg, True)
    #Log("DateMenu for " +BASE_URL + arg)
  
  showElements = site.xpath("//div[@class='beitragListe']//li")
  elementsCount = len(showElements)
  for i in range(0, elementsCount):

    showElement = showElements[i]
    try:
      link_element = showElement.xpath(".//b/a")[0]
    except IndexError :
      continue
    show_url = str(link_element.xpath('@href')[0]) + "&teaserListIndex="+str(MAX_ENTRIES*2)
    show_title = str(link_element.text)
    subtitleElements = showElement.xpath(".//p[@class='grey']/a")
    showSubtitle = subtitleElements[len(subtitleElements)-1].text
    
    img_url = str(showElement.xpath(".//img")[0].xpath("@src")[0])
    img_url_parts = img_url.split("/")
    img_url_parts.pop()
    large_img_url = "/".join(img_url_parts)
    large_img_url = BASE_URL + large_img_url.replace("94x65", "485x273")
    
    dir.Append(Function(DirectoryItem(DateMenu, title = show_title, subtitle = showSubtitle, thumb = large_img_url), arg = show_url)) 
  
  return dir


def DateMenu(sender, arg):
  dir = MediaContainer(viewGroup="InfoList")

  maxEntries = MAX_ENTRIES

  if(arg.startswith('http://')) :
    site = XML.ElementFromURL(arg, True)
    #Log("DateMenu for " +arg)
  else :
    site = XML.ElementFromURL(BASE_URL + arg, True)
    #Log("DateMenu for " +BASE_URL + arg)
  
  showElements = site.xpath("//div[@class='beitragListe']//li")
  elementsCount = len(showElements)
  for i in range(0, elementsCount):

    if((maxEntries > 0) and (i >= maxEntries)) :
      break

    showElement = showElements[i]
    try:
      link_element = showElement.xpath(".//b/a")[0]
    except IndexError :
      continue
    show_url = str(link_element.xpath('@href')[0])

    # We do not support Bilderserien or interaktiveInhalte 
    # (we could support Bilderserien in the future)
    if(('bilderserie' in show_url) or ('interaktiv' in show_url)) :
      if(maxEntries > 0) :
	maxEntries += 1; # Compensate for entries not displayed
      continue

    show_title = str(link_element.text)
    
    # Filter out "Vorschau"/"Trailer" videos 
    if(FILTER_TRAILERS and (('Vorschau' in show_title) or ('Trailer' in show_title))) :
      continue
    
    subtitleElements = showElement.xpath(".//p[@class='grey']/a")
    showSubtitle = subtitleElements[len(subtitleElements)-1].text
    
    img_url = str(showElement.xpath(".//img")[0].xpath("@src")[0])
    img_url_parts = img_url.split("/")
    img_url_parts.pop()
    large_img_url = "/".join(img_url_parts)
    large_img_url = BASE_URL + large_img_url.replace("94x65", "485x273")
    
    showDetails = LoadShowDetails(show_url)
    if (len(showDetails) > 0):
      dir.Append(VideoItem(showDetails[0], title = show_title, subtitle = showSubtitle, summary = showDetails[1], thumb = large_img_url))
      #dir.Append(WindowsMediaVideoItem(showDetails[0], title = show_title, subtitle = showSubtitle, summary = showDetails[1], thumb = large_img_url))
      #link = 'http://www.plexapp.com/player/silverlight.php?stream=' + String.Quote(showDetails[0], usePlus=False)
      #dir.Append(WebVideoItem(link, title = show_title, subtitle = showSubtitle, summary = showDetails[1], thumb = large_img_url))
    
  return dir


def LoadShowDetails(url):
  site = XML.ElementFromURL(BASE_URL + url, True, errors='ignore')
  summaryElements = site.xpath("//p[@class='kurztext']")
  if (len(summaryElements) > 0):
    summaryElement = summaryElements[0]
    summaryText = summaryElement.text
    
    streamURLElements = site.xpath("//ul[@class='dslChoice']/li/a")
    
    for elem in streamURLElements :
      url = str(elem.xpath('@href'))

      if('asx' in url) :
	streamURL = url;
	if('veryhigh' in url): # Prefer high-quality version
	  break
	        
    streamURL = streamURL.replace('[','').replace(']','').replace('\'','')
    return [streamURL, summaryText]
    
  return []
