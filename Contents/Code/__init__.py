# -*- coding: utf-8 -*-
'''
Created on June 30, 2009
           0.7 + 0.8  + 0.9 on Nov 18,2010

@summary: A Plex Media Server plugin that integrates trailers of French web site Allocine.
@version: 0.9
@author: Oncleben31
         0.7 - 0.8 by Pierre - fixed non ascii characters display in the film descriptions - sped up thumbnail loading
         0.9 : removed previouslyused workaround for a bug that has been fixed - removed Log() functions
'''

# Plugin parameters
PLUGIN_TITLE						= "Allociné"					# The plugin Title
PLUGIN_PREFIX   					= "/video/Allocine"				# The plugin's contextual path within Plex
PLUGIN_HTTP_CACHE_INTERVAL			= 0

# Plugin Icons
PLUGIN_ICON_DEFAULT					= "icon-default.png"
PLUGIN_ICON_BA_ANEPASMANQUER		= "icon-default.png"
PLUGIN_ICON_BA_CETTESEMAINE			= "icon-default.png"
PLUGIN_ICON_BA_ALAFFICHE			= "icon-default.png"
PLUGIN_ICON_BA_PROCHAINEMENT		= "icon-default.png"
PLUGIN_ICON_PREFS					= "icon-default.png"

# Strings - Here since there is a bug with the JSON loading
ANEPASMANQUER_MENU_TITLE			= "À ne pas manquer".decode('utf-8')
ANEPASMANQUER_MENU_SUMMARY			= "Les Bandes-Annonces des films attendus".decode('utf-8')
CETTESEMAINE_MENU_TITLE			    = "Sorties de la semaine".decode('utf-8')
CETTESEMAINE_MENU_SUMMARY			= "Les Bandes-Annonces des films sortis mercredi dernier.".decode('utf-8')
PROCHAINEMENT_MENU_TITLE			= "Prochainement".decode('utf-8')
PROCHAINEMENT_MENU_SUMMARY			= "Les Bandes-Annonces des films devant sortirs dans les semaines à venir.".decode('utf-8')
ALAFFICHE_MENU_TITLE				= "À l'affiche".decode('utf-8')
ALAFFICHE_MENU_SUMMARY				= "Les Bandes-Annonces des films en salle actuellement.".decode('utf-8')

VIDEODETAILS = 'http://www.allocine.fr/modules/video/xml/AcVisiondata.ashx?media=%s&ref=191004&typeref=film'

# Plugin Artwork
PLUGIN_ARTWORK						= "art-default.jpg"

#Some URLs for the script
PLUGIN_URL_BA_ANEPASMANQUER			= "http://rss.allocine.fr/ac/bandesannonces/anepasmanquer"
PLUGIN_URL_BA_CETTESEMAINE			= "http://rss.allocine.fr/ac/bandesannonces/cettesemaine"
PLUGIN_URL_BA_ALAFFICHE				= "http://rss.allocine.fr/ac/bandesannonces/alaffiche"
PLUGIN_URL_BA_PROCHAINEMENT			= "http://rss.allocine.fr/ac/bandesannonces/prochainement"

####################################################################################################

def Start():
	# Register our plugins request handler
	Plugin.AddPrefixHandler(PLUGIN_PREFIX, MainMenu, PLUGIN_TITLE.decode('utf-8'), PLUGIN_ICON_DEFAULT, PLUGIN_ARTWORK)
	
	# Add in the views our plugin will support
	
	Plugin.AddViewGroup("Menu", viewMode="InfoList", mediaType="items")
	
	# Set up our plugin's container
	
	MediaContainer.title1 = PLUGIN_TITLE.decode('utf-8')
	MediaContainer.viewGroup = "Menu"
	MediaContainer.art = R(PLUGIN_ARTWORK)
	DirectoryItem.thumb = R(PLUGIN_ICON_DEFAULT)
	
	# Configure HTTP Cache lifetime
	
   	HTTP.CacheTime = 3600

####################################################################################################
# The plugin's main menu. 

def MainMenu():
	dir = MediaContainer(art = R(PLUGIN_ARTWORK), viewGroup = "Menu")
	dir.Append(Function(DirectoryItem(ListeANePasManquer, title=ANEPASMANQUER_MENU_TITLE, thumb=R(PLUGIN_ICON_BA_ANEPASMANQUER), summary=ANEPASMANQUER_MENU_SUMMARY)))
	dir.Append(Function(DirectoryItem(ListeCetteSemaine, title=CETTESEMAINE_MENU_TITLE, thumb=R(PLUGIN_ICON_BA_CETTESEMAINE), summary=CETTESEMAINE_MENU_SUMMARY)))
	dir.Append(Function(DirectoryItem(ListeALAffiche, title=ALAFFICHE_MENU_TITLE, thumb=R(PLUGIN_ICON_BA_ALAFFICHE), summary=ALAFFICHE_MENU_SUMMARY)))
	dir.Append(Function(DirectoryItem(ListeProchainement, title=PROCHAINEMENT_MENU_TITLE, thumb=R(PLUGIN_ICON_BA_PROCHAINEMENT), summary=PROCHAINEMENT_MENU_SUMMARY)))
		 
	return dir

####################################################################################################
# The A Ne pas Manquer menu

def GetThumb(path,thumb_type):
    image = HTTP.Request(path).content
    return DataObject(image,thumb_type) 	
	
def TraiteFluxRSS(urlFluxRSS, titreFluxRSS):
	dir = MediaContainer(art = R(PLUGIN_ARTWORK), viewGroup = "Menu", title2 = titreFluxRSS)

	fluxXML = XML.ElementFromURL(urlFluxRSS,encoding = "iso-8859-1")
	
	for c in fluxXML.xpath(".//item",encoding = "iso-8859-1"):
		titleEtSubtitle = c.xpath('.//title')[0].text.rsplit(' - ',1)
		title = titleEtSubtitle[0].encode("iso-8859-1")
		try:
		  subtitle = titleEtSubtitle[1].encode("iso-8859-1")
		except:
		  subtitle = None
		try:
		  thumb = c.find('enclosure').get('url')
		  thumb_type = c.find('enclosure').get('type')
		except:
		  thumb = c.find('thumbnail').get('url')
		  thumb_type = "image/jpeg"
		
		FilmPath  = thumb.rsplit("medias/nmedia/")[1].rsplit(".jpg")[0]
		FilmId = FilmPath.split('/')[-1].split('_')[0]
		
		urlFlv = XML.ElementFromURL(VIDEODETAILS%FilmId).xpath('//AcVisionVideo')[0].get('hd_path')

		try :
		  urlDescription = "http://www.allocine.fr/film/fichefilm_gen_cfilm=" + XML.StringFromElement(c.xpath("./link")[0]).rsplit("cfilm=")[1]
		
		  pageFilm = HTML.ElementFromURL(urlDescription,encoding = "iso-8859-1")
		  divDescription = pageFilm.xpath('//p[contains(., "Synopsis :")]')
		  description = divDescription[0].xpath("string()").rsplit("Synopsis :")[1].encode("iso-8859-1")
		except:
		  description = c.find('description').text_content().split('<')[0].encode("iso-8859-1")
		
		dir.Append(VideoItem(urlFlv, title=title, subtitle=subtitle, summary=description, thumb=Function(GetThumb,path=thumb,thumb_type=thumb_type))) 
	
	return dir     
	
####################################################################################################
# The A Ne pas Manquer menu
def ListeANePasManquer(sender):
	dir = TraiteFluxRSS(PLUGIN_URL_BA_ANEPASMANQUER, ANEPASMANQUER_MENU_TITLE)
	return dir

####################################################################################################
# The Cette Semaine menu
def ListeCetteSemaine(sender):
	dir = TraiteFluxRSS(PLUGIN_URL_BA_CETTESEMAINE, CETTESEMAINE_MENU_TITLE)
	return dir

####################################################################################################
# The A L'Affichie menu
def ListeALAffiche(sender):
	dir = TraiteFluxRSS(PLUGIN_URL_BA_ALAFFICHE, ALAFFICHE_MENU_TITLE)
	return dir

####################################################################################################
# The Prochainement menu
def ListeProchainement(sender):
	dir = TraiteFluxRSS(PLUGIN_URL_BA_PROCHAINEMENT, PROCHAINEMENT_MENU_TITLE)
	return dir

####################################################################################################
