# Parameters
# -p	Pagespeed
# -w	W3C
# -s	SEO Structure
# -m	MPIs
# -u	Unique Links
# -f	Menus
# -a	All

from requests_html import HTMLSession
from tqdm import tqdm
import time
import os
import errno
from socket import error as socket_error
import json
from colorama import Fore, Style
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import random
from itertools import groupby

url = ''

while ' -' not in url:
    print('\033c')
    print(Fore.YELLOW)
    print('┌────────────────────────────────┐')
    print('│          INSTRUCTIONS          │')
    print('└────────────────────────────────┘')
    print('\nPaste the site URL followed by desired parameters\n')
    print('-p ─────── Pagespeed (BETA)')
    print('-w ─────── W3C')
    print('-s ─────── SEO structure (Alt and Title)')
    print('-m ─────── MPI validation')
    print('-u ─────── Search for links that aren\'t in the menu')
    print('-c ─────── Compare menus')
    print('-l ─────── Check lateral scroll on mobile')
    print('-a ─────── Check all errors')
    print('\nExample: [url] [parameter] [...]', Style.RESET_ALL)
    url = input(str('\nPaste the url here: '))

def main_url(url):
    url = url.split('//')
    url = url[1].split('/')
    return url[0]

root = main_url(url)

vPagespeed = True if ' -p' in url else False
vW3C = True if ' -w' in url else False
vSEO = True if ' -s' in url else False
vMPI = True if ' -m' in url else False
vUniqueLinks = True if ' -u' in url else False
vMenus = True if ' -c' in url else False
vMobile = True if ' -l' in url else False
vAll = True if ' -a' in url else False

if vAll:
    vPagespeed = True
    vW3C = True
    vSEO = True
    vMPI = True
    vUniqueLinks = True
    vMenus = True
    vMobile = True

url = url.split(' ')[0]

def valid_url(url):
    if '?' not in url and '#' not in url and '.jpg' not in url and '.jpeg' not in url and '.png' not in url and '.png' not in url and '.pdf' not in url and 'tel:' not in url and 'mailto:' not in url:
        return True
    else:
        return False


session = HTMLSession()
r = session.get(url)
insideLinks = r.html.absolute_links
menuTop = r.html.absolute_links

if vMobile:
    cap = DesiredCapabilities().FIREFOX
    cap["marionette"] = False
    driver = webdriver.Firefox(capabilities=cap, executable_path="%USERPROFILE%\\AppData\\Local\\Geckodriver\\geckodriver.exe")
    driver.set_window_position(0, 0)
    driver.set_window_size(350, 568)

def GetWidth(pageUrl):    
    driver.get(pageUrl)
    windowWidth = driver.execute_script('return document.body.clientWidth')
    documentWidth = driver.execute_script('return document.body.scrollWidth')
    if windowWidth < documentWidth:
        print('\n------------- LATERAL SCROLL -------------\n')
        print(pageUrl)
        print('Page content larger than window')
        print('\n----------- END LATERAL SCROLL -----------\n')


mpiBaseLink = (url + 'mapa-site') if url[-1:] == '/' else (url + '/mapa-site')
r = session.get(mpiBaseLink)
subMenuInfo = r.html.find('.sitemap ul.sub-menu-info li a')
mpiLinks = []
for content in subMenuInfo:
    mpiLinks.append(str(content.links)[2:-2])

if vMPI:
    print('-------------- MPI Validation --------------')
    
    for key, item in groupby(mpiLinks):
        frequency = list(item)
        if(len(frequency) > 1):
            print(f'Duplicated MPI: {frequency[0]} - {len(frequency)}') 

    def CheckIssues(mpiLinks):
        issueUrls = []
        for link in tqdm(mpiLinks):
            print('\n')
            w3cLink = f"{link}"
            try:
                r = session.get(w3cLink)
            except socket_error as serr:
                if serr.errno == errno.ECONNREFUSED:
                    print('Link inválido:', link, serr)
                    continue
            description = len(r.html.find('head meta[name="description"]', first=True).attrs['content'])
            images = len(r.html.find('article ul.gallery img'))
            h2 = len(r.html.find('article h2'))
            articleElements = r.html.find('article h2, article p')

            emptyElements = []
            for emptyElement in articleElements:
                if len(emptyElement.text) < 6:
                    emptyElements.append(emptyElement)

            fakeTitles = r.html.find('article p')
            pUpper = []
            for fakeTitle in fakeTitles:
                if fakeTitle.text.isupper():
                    pUpper.append(fakeTitle)
            
            fakeParagraphs = r.html.find('article h2:not(:last)')
            h2Lower = []
            for fakePragraph in fakeParagraphs:
                if fakePragraph.text.islower():
                    pUpper.append(fakePragraph)
                            
            pList = r.html.find('article p', containing=';')
            hasIssues = False

            sequentialList = r.html.find('article ul + ul')

            if len(pUpper) > 0:
                print(f'There are {len(pUpper)} uppercase p')
                hasIssues = True
            if len(h2Lower) > 0:
                print(f'There are {len(fakeTitles)} uppercase p')
                hasIssues = True
            if len(emptyElements) > 0:
                print(f'There are {len(emptyElements)} empty elements')
                hasIssues = True
            if description < 140 or description > 160 : 
                print('Description char count:', description)
                hasIssues = True
            if images < 3 :
                print('Image count:', images)
                hasIssues = True
            if h2 < 3 :
                print('H2 count:', h2)
                hasIssues = True
            if len(pList) > 0 :
                print('p tag as list:', len(pList))
                # print('p tag as list:')
                # for p in pList:
                # 	print('[...]', p.text[-30:])
                hasIssues = True
            if len(sequentialList) > 0 :
                print('There are', len(sequentialList),'list(s) in sequence')
                hasIssues = True
            if hasIssues :
                print(link, '\n')
            time.sleep(1)
        print('-------------- MPI Validation Finished --------------')
            
    CheckIssues(mpiLinks)

links = []
visitedLinks = [url]
count = 0
loader = ['/', '–', '\\', '|']

strangeLinks = []

if vPagespeed:

    pageSpeedLinks = [url]

    while len(pageSpeedLinks) != 5:
        uniqueMpi = random.choice(mpiLinks)
        if uniqueMpi not in pageSpeedLinks:
            pageSpeedLinks.append(uniqueMpi)
	
    print('-------------- PageSpeed Insights --------------')
    print('Checking PageSpeed Score...')

    apiKey = 'AIzaSyDFsGExCkww5IFLzG1aAnfSovxSN-IeHE0'

    def PageSpeed(pagespeedUrl, apiKey):

        print(f'{pagespeedUrl}')
        
        pagespeedUrl = pagespeedUrl.replace(':', '%3A')
        pagespeedUrl = pagespeedUrl.replace('/', '%2F')
        mobileUrl = f'https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url={pagespeedUrl}&category=performance&locale=pt_BR&strategy=mobile&key={apiKey}'
        desktopUrl = f'https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url={pagespeedUrl}&category=performance&locale=pt_BR&strategy=desktop&key={apiKey}'

        mobileRequest = session.get(mobileUrl)
        jsonData = json.loads(mobileRequest.text)
        mobileScore = int(float(jsonData['lighthouseResult']['categories']['performance']['score']) * 100)
        print(f'Mobile score - {mobileScore}')

        desktopRequest = session.get(desktopUrl)
        jsonData = json.loads(desktopRequest.text)
        desktopScore = int(float(jsonData['lighthouseResult']['categories']['performance']['score']) * 100)
        print(f'Desktop score - {desktopScore}')
        print('-' * 40)

    for pageSpeedLink in pageSpeedLinks:
        PageSpeed(pageSpeedLink, apiKey)
        
    #pagespeedUrl = url
    #filterThirdPartyResouces = True
    #locale = 'pt_BR'
    #screenshot = False
    #category = 'performance'

    #filterThirdPartyResouces = str(filterThirdPartyResouces).lower()
    #screenshot = str(screenshot).lower()

    # v2
    # url = f'https://www.googleapis.com/pagespeedonline/v2/runPagespeed?url={url}/&filter_third_party_resources={filterThirdPartyResouces}&screenshot={screenshot}&strategy={strategy}&key={apiKey}'

    # v5
    #desktopUrl = f'https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url={url}&category={category}&locale={locale}&strategy=desktop&key={apiKey}'
    #mobileUrl = f'https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url={url}&category={category}&locale={locale}&strategy=mobile&key={apiKey}'

print('Getting links...')

def site_urls(insideLinks, counter):
    for link in insideLinks:
        if 'http' in link and root in link:
            if valid_url(link):
                links.append(link)
    for link in links:
        if link not in visitedLinks:
            if counter < len(loader) - 1:
                counter += 1
            else:
                counter = 0
            # print('\033c')
            # print('Getting links ', loader[counter])
            if 'orcamento' in link: continue
            visitedLinks.append(link)
            r = session.get(link)
            pageLinks = r.html.absolute_links
            site_urls(pageLinks, counter)

def CheckForUniqueLinks(uniqueLinks):
    r = session.get(url + '/mapa-site')
    sitemapElements = r.html.find('.sitemap li a')
    sitemapLinks = []
    unlistedLinks = []
    for sitemapElement in sitemapElements:
        sitemapLinks.append(sitemapElement.attrs['href'])
    for uniqueLink in uniqueLinks:
        # if uniqueLink not in sitemapLinks and uniqueLink not in (url + 'carrinho') and uniqueLink not in (url + 'mapa-sitea'):
        if uniqueLink not in sitemapLinks and '/mapa-site' not in uniqueLink and '/carrinho' not in uniqueLink:
            unlistedLinks.append(uniqueLink)
    if(len(unlistedLinks) > 0):
        print(f'This links are not listed in sitemap page')
        for unlistedLink in unlistedLinks:
            print(unlistedLink)
        print('------------------------')

if vW3C or vSEO or vMPI or vMobile:
    site_urls(insideLinks, count)

def CompareMenus():
    r = session.get(url)
    menuTop = r.html.find('header nav[id*="menu"] > ul > li > a')
    menuFooter = r.html.find('footer .menu-footer nav > ul > li > a')
    
    menuTopLinks = []
    menuFooterLinks = []
    for menuTopLink in menuTop:
        menuTopLinks.append(menuTopLink.attrs['href'])
    for menuFooterLink in menuFooter:
        menuFooterLinks.append(menuFooterLink.attrs['href'])
    menuTopLinks.append(url + 'mapa-site')

    # print(menuTopLinks)
    # print(menuFooterLinks)

    print('-' * 10 + ' COMPARING MENUS ' + '-' * 10)

    print('Comparsion links of header\'s menu and footer\'s menu')

    if False in [True if i == j else False for i,j in zip(menuTopLinks, menuFooterLinks)]:
        print('There are wrong links or order')
    else:
        print('The links are the same')
    print('-' * 40)
    
    menuTopTexts = []
    menuFooterTexts = []
    for menuTopText in menuTop:
        menuTopTexts.append(menuTopText.text.lower())
    for menuFooterText in menuFooter:
        menuFooterTexts.append(menuFooterText.text.lower())
    menuTopTexts.append('Mapa do site'.lower())
    
    # print(menuTopTexts)
    # print(menuFooterTexts)

    print('Comparsion texts of header\'s menu and footer\'s menu')

    if False in [True if i == j else False for i,j in zip(menuTopTexts, menuFooterTexts)]:
        print('There are wrong texts or order')
    else:
        print('The texts are the same')
    print('-' * 40)

if vMenus:
    CompareMenus()

if vUniqueLinks:
    CheckForUniqueLinks(visitedLinks)

if os.path.exists('errors.txt'):
    os.remove('errors.txt')
f = open('errors.txt', 'w+')

if vW3C or vSEO or vMPI or vMobile:

    visitedLinks.append(url + '404')

    for link in tqdm(visitedLinks):
        print('\n')
        r = session.get(link)
        if vMobile:
            GetWidth(link)
        if vSEO:
            allImages = r.html.find('body img')
            allLinks = r.html.find('body a[href*="http"]')
            hasNoAttrInImage = False
            hasNoAttrInLink = False
            for checkImage in allImages:
                try:
                    if 'escrev' in checkImage.attrs['title'].lower():
                        if not hasNoAttrInImage:
                            hasNoAttrInImage = True
                            print('\n---------------- IMAGES ------------------')
                        print('WRONG TITLE IN\n' + link + '\n[' + checkImage.attrs['src'] + ']\n')
                except KeyError as err:
                    if not hasNoAttrInImage:
                        hasNoAttrInImage = True
                        print('\n---------------- IMAGES ------------------')
                    print('IMAGE WITHOUT TITLE IN\n' + link + '\n[' + checkImage.attrs['src'] + ']\n')
                try:
                    if 'escrev' in checkImage.attrs['alt'].lower():
                        if not hasNoAttrInImage:
                            hasNoAttrInImage = True
                            print('\n---------------- IMAGES ------------------')
                        print('WRONG ALT IN\n' + link + '\n[' + checkImage.attrs['src'] + ']\n')
                except KeyError as err:
                    if not hasNoAttrInImage:
                        hasNoAttrInImage = True
                        print('\n---------------- IMAGES ------------------')
                    print('IMAGE WITHOUT ALT IN\n' + link + '\n[' + checkImage.attrs['src'] + ']\n')
            for checkLink in allLinks:
                    try:
                        if 'facebook' in checkLink.attrs['title'].lower():
                            continue
                        if 'escrev' in checkLink.attrs['title'].lower():
                            if not hasNoAttrInLink:
                                hasNoAttrInLink = True
                                print('\n---------------- LINKS ------------------')
                            print(f'WRONG TITLE IN {link} --- [' + checkLink.attrs['href'] + ']'+'\n')
                    except KeyError as err:
                        if not hasNoAttrInLink:
                            hasNoAttrInLink = True
                            print('\n---------------- LINKS ------------------')
                        print(f'LINK WITHOUT TITLE IN {link} --- [' + checkLink.attrs['href'] + ']'+'\n')
        if vW3C:
            hasW3CError = False
            w3cLink = f"https://validator.w3.org/nu/?doc={link}"
            try:
                r = session.get(w3cLink)
            except socket_error as serr:
                if serr.errno == errno.ECONNREFUSED:
                    print('Invalid or broken link:', link, serr)
                    continue
            erros = r.html.find('#results strong')
            if erros:
                if not hasW3CError:
                    hasW3CError = True
                    print('\n---------------- W3C ------------------')
                print(link)
                f.write(f'{link}\n')
            for erro in erros:
                print(erro.text)
            time.sleep(1)

    f.close()
if vMobile:
    driver.close()
    driver.quit()
print('Finished')
