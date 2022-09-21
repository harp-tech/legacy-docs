# -*- coding: utf-8 -*-
"""
Created on Tue Jun  7 17:32:41 2022

Takes the information on a google sheet describing harp devices. For each device, makes;
- Device page with description, image, links to software etc
- Device 'Card' for overview page, which can be filtered by category

Both these are generated by inserting specific data from the google sheet into a page and a card template file. 
These are stored in the docs file under _static\python. 


Accessing google sheet via python instructions: https://towardsdatascience.com/turn-google-sheets-into-your-own-database-with-python-4aa0b4360ce7
To access the google sheet, the script needs access to a key json file, loaded in as 'creds'. This is kept locally,
not on the repo, as it contains access keys. 

@author: Alex
"""


#%% import 

from os.path import join 

import gspread
from oauth2client.service_account import ServiceAccountCredentials

#%% set file and folder locations 

pyDir = "C:\\Users\\Alex\\Documents\\Repos\\harp-docs\\source\\_static\python\\"

docDir = "C:\\Users\\Alex\\Documents\\Repos\\harp-docs\\source\\Devices\\"

scope = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/spreadsheets',"https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]

creds = ServiceAccountCredentials.from_json_keyfile_name("C:\\Users\\Alex\\Desktop\\harp-352616-f57e1230cd03.json",scope)

#%% collect device data from google sheet 

client = gspread.authorize(creds)

devicesheet = client.open("HARP Devices").sheet1  
devicedata = devicesheet.get_all_records() 

#%% locate template files 

pageTemplateFile = join(pyDir,"page_template.rst")
cardTemplateFile = join(pyDir,"card_template.rst")
repobuttonTemplate = join(pyDir,"repobutton_template.rst")
deviceListTemplateFile = join(pyDir,"device_list_template.rst")
filterTemplateFile = join(pyDir, "filter_template.rst")
softwareFile = join(pyDir, "software_section_template.rst")

#%% clear allcards.rst

allCardsFile = join(docDir,"allCards.rst")

finCardsAll = open(allCardsFile, "w")
finCardsAll.write("")
finCardsAll.close()


#%% replace device card template values with extracted device data from sheet 

allCategories = list()

for count, idevice in enumerate(devicedata):

    finCardTemplate = open(cardTemplateFile, "rt")
    finPageTemplate = open(pageTemplateFile, "rt")
    finRepobutton = open(repobuttonTemplate, "rt")
    finSoftware = open(softwareFile, "rt")

    deviceCard = finCardTemplate.read()
    devicePage = finPageTemplate.read()
    repoButton = finRepobutton.read()
    softwareSection = finSoftware.read()
    
    print(devicedata[count].get("deviceName"))
    
    devicePage = devicePage.replace('DEVICENAME', devicedata[count].get("deviceName"))

    devicePage = devicePage.replace('CONNECTIVITY', devicedata[count].get("connections"))

    deviceHandle = devicedata[count].get("deviceHandle")

    devicePage = devicePage.replace('DEVICEHANDLE', deviceHandle)
    
    devicePage = devicePage.replace('REFDEVICE',deviceHandle)
    
    devicePage = devicePage.replace('KEYFEATURES', devicedata[count].get("keyFeatures"))
    
    devicePage = devicePage.replace('USECASES', devicedata[count].get("useCases"))

    devicePage = devicePage.replace('SOFTWARECONFIG', devicedata[count].get("softwareConfig"))
    
    softwarelink= devicedata[count].get("softwareLink")
    
     
    if softwarelink == '':
        devicePage = devicePage.replace('SOFTWARESECTION', "")
    else: 
        softwareLine = softwareSection.replace("SOFTWARELINK",softwarelink)
        devicePage = devicePage.replace('SOFTWARESECTION', softwareLine)
    
    
    devicePage = devicePage.replace('DESCRIPTION', devicedata[count].get("description"))

    devicePage = devicePage.replace('GITHUBLINK', devicedata[count].get("github"))
        
    deviceCard = deviceCard.replace('CARDTEXT', devicedata[count].get("cardText"))
    
    deviceCard = deviceCard.replace('DEVICENAME', devicedata[count].get("deviceName"))
    
    catLine = devicedata[count].get("categories")
    categories = catLine.replace('\n', " ")    
    deviceCard = deviceCard.replace('CATEGORY', categories)
    
    # collect all existing categories to make filter 
    catSplit = catLine.split("\n")
    allCategories = allCategories + catSplit
    
    deviceCard = deviceCard.replace('DEVICEHANDLE', deviceHandle)
    
    
    # repos can be github and/ or bitbucket: create button for each repo present    
    githublink = devicedata[count].get("github")
    
    if githublink == '':
        repoButtonGH = githublink
    else:
        repoButtonGH = repoButton.replace('REPOLINK', githublink)
        repoButtonGH = repoButton.replace('WHICHREPO', "github")
        
    devicePage = devicePage.replace('REPOBUTTON1', repoButtonGH)
    
    
    bitbucketlink = devicedata[count].get("bitbucket")
    
    if bitbucketlink == '':
        repoButtonBB = bitbucketlink
    else:
        repoButtonBB = repoButton.replace('REPOLINK', bitbucketlink)
        repoButtonBB = repoButton.replace('WHICHREPO', "bitbucket")
    
    devicePage = devicePage.replace('REPOBUTTON2', repoButtonBB)
    
    filenameOut = "alldevices\\" + deviceHandle + ".rst"
    target = join(docDir,filenameOut)

    finPageOut = open(target, "wt", encoding="utf8")
    finPageOut.write(devicePage)
    finPageOut.close()
    
    finCardsAll = open(allCardsFile, "a", encoding="utf8")
    finCardsAll.write(deviceCard)
    finCardsAll.close()

#%% insert cards into deviceList page 

# open device list template file 
finDeviceListTemplate = open(deviceListTemplateFile, "rt")
deviceListTemplate = finDeviceListTemplate.read()

# read allCard file just saved 
finCardsAll = open(allCardsFile, "rt")
allCards = finCardsAll.read() 
finCardsAll.close()

# enter allCard info into the template 
deviceList = deviceListTemplate.replace('ALLCARDSHERE',allCards )

# save to deviceList in docs 
target = join(docDir, "device_list.rst")
finPageOut = open(target, "wt", encoding="utf8")
finPageOut.write(deviceList)
finPageOut.close()

#%% extract unique filter categories 

a = open(filterTemplateFile, "rt")
filtTemplate = a.read()
a.close()


filter_set = set(allCategories)

filterCode = str()
for id,val in enumerate(filter_set):
    
    filterMe = filtTemplate.replace("FILTERNAME", val)
    filterCode = filterCode + filterMe
    

deviceList = deviceList.replace('FILTERSHERE', filterCode)

finDevicePage = open(join(docDir,"device_list.rst"), "wt", encoding="utf8")
finDevicePage.write(deviceList)
finDevicePage.close()


