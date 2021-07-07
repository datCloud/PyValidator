# http://mpitemporario.com.br/projetos/atar.com.br/
# Parameters
# -p	Pagespeed
# -w	W3C
# -s	SEO Structure
# -m	MPIs
# -u	Unique Links
# -f	Menus
# -a	All

from requests_html import HTMLSession
import urllib
from tqdm import tqdm
import time
import os
import inspect
import errno
from socket import error as socket_error
import json
from colorama import Fore, Style
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import random
from itertools import groupby
from selenium.webdriver.firefox.options import Options
import sys
# from PIL import ImageFile

url = ''

while ' -' not in url:
    print('\033c')
    print(Fore.YELLOW)
    print('┌────────────────────────────────┐')
    print('│          INSTRUCTIONS          │')
    print('└────────────────────────────────┘')
    print('\nPaste the site URL followed by desired parameters\n')
    print('GENERAL')
    # print('-p ─────── Pagespeed (BETA)')
    print('-i ─────── ICM Mode (New)')
    print('-w ─────── W3C')
    print('-s ─────── SEO structure (Alt and Title)')
    print('-m ─────── MPI validation')
    print('-x ─────── Use sitemap.xml to get site links (crawls faster)')
    print('-u ─────── Search for links that aren\'t in the menu')
    print('-c ─────── Compare menus')
    print('-l ─────── Check lateral scroll on mobile')
    print('-a ─────── Check all errors')
    # print('MISC')
    # print('-u ─────── Check User Analytics')
    print('\nExample: [url] [parameter] [...]', Style.RESET_ALL)
    url = input(str('\nPaste the url here: '))

def main_url(cleanUrl):
    cleanUrl = cleanUrl.split('//')
    cleanUrl = cleanUrl[1].split('/')
    return cleanUrl[0]

root = main_url(url)

# currentDirectory = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
# keywordsFile = open(os.path.join(currentDirectory, 'keywords.txt'), 'r')

vPagespeed = True if ' -p' in url else False
vW3C = True if ' -w' in url else False
vSEO = True if ' -s' in url else False
vMPI = True if ' -m' in url else False
vUniqueLinks = True if ' -u' in url else False
vMenus = True if ' -c' in url else False
vMobile = True if ' -l' in url else False
vAll = True if ' -a' in url else False
vSitemap = True if ' -x' in url else False
vMisc = True if ' -u' in url else False
vICM = True if ' -i' in url else False
vMisc = False

if vAll:
    vPagespeed = True
    vW3C = True
    vSEO = True
    vMPI = True
    vUniqueLinks = True
    vMenus = True
    vMobile = True
    # vMisc = False

vImageData = False

url = url.split(' ')[0]
if url[-1:] != '/' : url = url + '/'
fullUrl = url

def valid_url(url):
    url = url.lower()
    if '?' not in url and '#' not in url and '.jpg' not in url and '.jpeg' not in url and '.png' not in url and '.png' not in url and '.pdf' not in url and 'tel:' not in url and 'mailto:' not in url and '.mp4' not in url and '.zip' not in url and '.rar' not in url:
        return True
    else:
        return False


session = HTMLSession()
r = session.get(url)
insideLinks = r.html.xpath('//a[not(@rel="nofollow")]/@href')
menuTop = r.html.absolute_links

hasSitemap = False

imageList = []

# Check robots.txt
r = session.get(url + 'robots.txt')
robots = r.text
if url in robots:
    print('Robots -> Ok')
else:
    print('Robots -> Wrong')

if vMobile or vMisc:

    # binary = r'C:\Program Files\Mozilla Firefox\firefox.exe'
    options = Options()
    options.add_argument('--headless')
    # options.binary = binary
    # cap = DesiredCapabilities().FIREFOX
    # cap["marionette"] = False
    # driver = webdriver.Firefox(options=options, capabilities=cap, executable_path="%USERPROFILE%\\AppData\\Local\\Geckodriver\\geckodriver.exe")
    driver = webdriver.Firefox(options=options)
    driver.set_window_position(0, 0)
    driver.set_window_size(350, 568)

if vMisc:
    driver.get(url)
    analyticsId = driver.execute_script('return Object.keys(window.gaData)[0]')
    print('Analytics ID -> ' + analyticsId)

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
            w3cLink = f"{link}"
            issueMessages = []
            try:
                r = session.get(w3cLink)
            except socket_error as serr:
                if serr.errno == errno.ECONNREFUSED:
                    print('Link inválido:', link, serr)
                    continue
            # description = len(r.html.find('head meta[name="description"]', first=True).attrs['content'])
            description = r.html.find('head meta[name="description"]', first=True).attrs['content']
            images = len(r.html.find('ul.gallery img'))
            h2 = r.html.find('article.full h2') if vICM else r.html.find('article h2')
            articleElements = r.html.find('article h2, article p')
            articleElements = r.html.find('article.full h2, article.full p, article.full li') if vICM else r.html.find('article h2, article p, article p')
            strongsInArticle = r.html.find('article.full p strong') if vICM else r.html.find('article p strong')
            titleWithStrong = r.html.find('article.full h2 strong') if vICM else r.html.find('article h2 strong')
            allParagraphs = r.html.find('article.full p, article.full li') if vICM else r.html.find('article p, article p')

            hasIssues = False

            try:
                h1 = r.html.find('h1')
                if(len(h1) > 1):
                    issueMessages.append('There is more than 1 H1')
                    hasIssues = True
                h1 = h1[0].text
            except AttributeError as aerr:
                h1 = 'Not found'
                issueMessages.append('There is no H1')
                hasIssues = True
                continue

            h2HasH1 = False
            for uniqueH2 in h2:
                if h1.lower() in uniqueH2.text.lower():
                    h2HasH1 = True
                    break

            h2List = []
            h1EqualsH2 = False
            for title in h2:
                h2List.append(title.text)
                if title.text.lower() == h1.lower() and not h1EqualsH2:
                    issueMessages.append('There are H2 equals to H1')
                    hasIssues = True
                    h1EqualsH2 = True

            if len(h2List) != len(set(h2List)):
                issueMessages.append('There are duplicated H2')
                hasIssues = True

            pAllList = []
            descriptionInArticle = False
            for paragraph in allParagraphs:
                pAllList.append(paragraph.text)
                if len(description) > 30:
                    if description[:-20].lower().strip() in paragraph.text.lower() and not descriptionInArticle:
                        descriptionInArticle = True

            if not descriptionInArticle:
                issueMessages.append('Description not in article')
                hasIssues = True

            if len(pAllList) != len(set(pAllList)):
                issueMessages.append('There are duplicated paragraphs')
                hasIssues = True

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

            pList = []

            for paragraph in pAllList:
                if paragraph[-5:] == ';':
                    pList.append(paragraph)
                            
            pList = r.html.find('article p', containing=';')

            sequentialList = r.html.find('article ul + ul')
            sequentialTitle = r.html.find('article h2 + h2')

            if h1.lower() not in description.lower() : 
                issueMessages.append('Description doesn\'t have mention to H1')
                hasIssues = True
            if len(strongsInArticle) < 3:
                issueMessages.append(f'There are only {len(strongsInArticle)} strongs in this article')
                hasIssues = True
            if len(titleWithStrong) > 0:
                issueMessages.append(f'There are {len(titleWithStrong)} titles with strong in this article')
                hasIssues = True
            if len(pUpper) > 0:
                issueMessages.append(f'There are {len(pUpper)} uppercase p')
                hasIssues = True
            if len(h2Lower) > 0:
                issueMessages.append(f'There are {len(fakeTitles)} uppercase p')
                hasIssues = True
            if len(emptyElements) > 0:
                issueMessages.append(f'There are {len(emptyElements)} empty elements')
                hasIssues = True
            if len(description) < 140 or len(description) > 160 : 
                issueMessages.append(f'Description char count: {len(description)}')
                hasIssues = True
            if images < 1 :
                issueMessages.append(f'Image count: {images}')
                hasIssues = True
            if len(h2) < 2 :
                issueMessages.append(f'H2 count: {len(h2)}')
                hasIssues = True
            if not h2HasH1:
                issueMessages.append(f'H2 text doesn\'t have mention to H1 in')
                hasIssues = True
            if len(pList) > 0 :
                issueMessages.append(f'p tag as list: {len(pList)}')
                # print('p tag as list:')
                # for p in pList:
                # 	print('[...]', p.text[-30:])
                hasIssues = True
            if len(sequentialList) > 0 :
                issueMessages.append(f'There are {len(sequentialList)} list(s) in sequence')
                hasIssues = True
            if len(sequentialTitle) > 0 :
                issueMessages.append(f'There are {len(sequentialTitle)} title(s) in sequence')
                hasIssues = True
            if hasIssues :
                print('\n')
                for issue in issueMessages:
                    print(issue)

                print('in', link)
            #time.sleep(1)
        print('-------------- MPI Validation Finished --------------')
        if not vW3C or  not vSEO or not vMobile:
            sys.exit('Finished')

            
    CheckIssues(mpiLinks)

links = []
visitedLinks = [url]
count = 0
loader = ['/', '–', '\\', '|']

strangeLinks = []

if vPagespeed:

    pageSpeedLinks = [url]

    while len(pageSpeedLinks) != 1:
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
        # f'https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url={pagespeedUrl}&fields=lighthouseResult/categories/*/score&prettyPrint=false&locale=pt_BR&strategy=mobile&&category=performance&key={apiKey}'
        desktopUrl = f'https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url={pagespeedUrl}&category=performance&locale=pt_BR&strategy=desktop&key={apiKey}'
        # test = f'https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url={pagespeedUrl}&fields=lighthouseResult/categories/*/score&prettyPrint=false&strategy=desktop&category=performance&key={apiKey}'
        # test = f'https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url={pagespeedUrl}&fields=lighthouseResult/categories/*/score&prettyPrint=false&strategy=desktop&category=performance&category=pwa&category=best-practices&category=accessibility&category=seo&key=AIzaSyDFsGExCkww5IFLzG1aAnfSovxSN-IeHE0'

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

def site_urls(insideLinks, counter, hasSitemap):
    if vSitemap:
        sitemapUrl = url + 'sitemap.xml'
        sitemapResquest = session.get(sitemapUrl)
        sitemapLinks = sitemapResquest.html.find('loc')
        if len(sitemapLinks) > 0:
            for sitemapItem in sitemapLinks:
                visitedLinks.append(sitemapItem.text)
            sitemapLinks = visitedLinks
            if url + '404' in visitedLinks:
                print('Found 404 link in sitemap.xml')
            return 0
        elif not hasSitemap:
            print('The site doesn\'t have a sitemap.xml file')
            print('Getting links...')
            hasSitemap = True
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
            if link[-1:] == '/' and link != fullUrl : continue
            if 'orcamento' in link: continue
            visitedLinks.append(link)
            r = session.get(link)
            pageLinks = r.html.xpath('//a[not(@rel="nofollow")]/@href')
            site_urls(pageLinks, counter, hasSitemap)

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
    site_urls(insideLinks, count, hasSitemap)

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

#if os.path.exists('errors.txt'):
    #os.remove('errors.txt')
#f = open('errors.txt', 'w+')

def GetImageData(imageUrl):
    if imageUrl not in imageList:
        imageList.append(imageUrl)
        try:
            if imageUrl.startswith('inc/'):
                imageUrl = fullUrl + imageUrl
            file = urllib.request.urlopen(imageUrl)
            size = file.headers.get("content-length")
            if size: size = int(size)
            p = ImageFile.Parser()
            while 1:
                data = file.read(1024)
                if not data:
                    break
                p.feed(data)
                if p.image:
                    if size != None:
                        # return size, p.image.size
                        return size / 1000
                    else:
                        return None;
                    break
            file.close()
            return size, None
        except socket_error as serr:
            return 'Broken image [' + imageUrl + ']'
    else:
        return 'pass'

if vW3C or vSEO or vMPI or vMobile:

    visitedLinks.append(url + '404')


    for link in tqdm(visitedLinks):
        # print(link)
        r = session.get(link)
        if vMobile:
            GetWidth(link)
        if vSEO:
            allImages = r.html.find('body img')
            allLinks = r.html.find('body a[href*="http"]')

            try:
                h1 = r.html.find('h1', first=True).text
            except AttributeError as aerr:
                h1 = 'Not found'
                print(f'\nH1 not found in {link}\n')
                continue

            description = r.html.find('head meta[name="description"]', first=True).attrs['content']
            if h1.lower() not in description.lower() and link != fullUrl: 
                print(f'\nDescription doesn\'t have mention to H1 in {link}')
            if len(description) < 140 or len(description) > 160 : 
                print(f'\nDescription char count: {len(description)} \n in {link}')
            hasNoAttrInImage = False
            hasNoAttrInLink = False
            for checkImage in allImages:
                # if vImageData:
                #     imageSize = GetImageData(checkImage.attrs['src'])
                #     if(imageSize != 'pass'):
                #         if(isinstance(imageSize, int)):
                #             if(imageSize > 200):
                #                 print('\nImage file size > 200KB [' + GetImageData(checkImage.attrs['src']) + 'KB] in ' + link + '\n')
                #         elif(isinstance(imageSize, str)):
                #             print('\n' + imageSize + '\n')
                try:
                    if 'escrev' in checkImage.attrs['title'].lower() or checkImage.attrs['title'] == '':
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
                    if 'escrev' in checkImage.attrs['alt'].lower() or checkImage.attrs['alt'] == '':
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
                        if 'facebook' in checkLink.attrs['href'].lower():
                            continue
                        if 'escrev' in checkLink.attrs['title'].lower() or checkLink.attrs['title'] == '':
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
                #f.write(f'{link}\n')
            for erro in erros:
                print(erro.text)
            #time.sleep(1)

    #f.close()
if vMobile:
    driver.close()
    driver.quit()
print('Finished')
