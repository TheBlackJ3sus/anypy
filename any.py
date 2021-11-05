import time
from pywinauto.application import Application
from pywinauto.findwindows import ElementNotFoundError
from pywinauto.findbestmatch import MatchError
from pywinauto.timings import TimeoutError
from pywinauto import timings

def FutureSpecs():
    DLConfig = main.child_window(title="Download configuration", control_type="Window", found_index=0)
    Pbar = main.child_window(class_name="QProgressBar")
    return DLConfig, Pbar

def Connect():
    print('Connecting to AnyStream...')
    try:
        app = Application(backend="uia").connect(title_re="AnyStream*", auto_id='MainWindow', visible_only = False)
        main = app.AnyStream
        main.wait('ready')
    except ElementNotFoundError:
        print('AnyStream is not open. Opening...')
        app = Application(backend="uia").start('C:/Program Files/RedFox/AnyStream/AnyStream.exe')
        main = app.AnyStream
        main.wait('ready')
    print('Connected to AnyStream')
    return app, main
def GetProvider(main):
    Tabs = main.child_window(class_name="QTabBar", control_type="Tab").descendants()
    for provider in Tabs:
        if provider.has_keyboard_focus():
            foundprovider = provider.texts()[0]
            print(f'Detected {foundprovider}')
            return foundprovider
def GottaBlast(sname,sList,Smax,app,dw,DLConfig,Pbar,provider):
    for dlseason in sList:
        if sList.index(dlseason)+1 > Smax:
            return print('Season limit reached')
        if sList != ['Amazon']:
            SelectSeason(dw,sList,sList.index(dlseason)+1)
            EpisodeList = EpisodeButtons(dw,sname,sList.index(dlseason)+1)
        else:
            EpisodeList = EpisodeButtons(dw,sname,sList[0])
        StartDownload(app,dw,DLConfig,Pbar,EpisodeList,provider)
def WaitForShow(main):
    print('Waiting for user to find a show...')
    dw = main.child_window(title='Downloadable item(s)', class_name='DownloadableViewDialog', control_type="Window", visible_only = False)
    dw.wait('enabled', timeout=1000)
    sname = dw.Static1.texts()[0]
    return dw, sname
def GetSeasons(dw,provider):
    if 'Amazon' in provider:
        sList = ['Amazon']
        return sList
    sList = dw.ListBox.texts()
    return sList
def SeasonLimiter(sList):
    validnumber = False
    maxseasons = len(sList)
    while validnumber is False:
        Smax = input(f'Limit number of seasons to download: 1-{maxseasons} (Press Enter for default ALL): ')
        try:
            Smax = int(Smax)
            if Smax > maxseasons or Smax == 0:
                print(f'Please enter a number between 1-{maxseasons}')
                continue
            validnumber = True
        except ValueError:
            if Smax == '':
                Smax = maxseasons
                validnumber = True
                continue
            print(f'{Smax} is not a number')
    return Smax
def SelectSeason(dw,sList,snumber):
    dw.ComboBox.select(sList[snumber-1][0])    
def EpisodeButtons(dw,sname,snumber):
    try:
        snumber = int(snumber)
        print(f'{sname}, Season {snumber} Episodes')
    except:
        print(f'{sname}, Episode List')
    Episodes = dw.descendants(class_name='DownloadableDetails')
    EpisodeList = {"Title":[],"Button":[]}
    for episode in Episodes:
        print(episode.children_texts()[1])
        EpisodeList["Title"].append(episode.children_texts()[1])
        EpisodeList["Button"].append(f'dw.DownloadButton{Episodes.index(episode)+1}')   
    return EpisodeList
def StartDownload(app,dw,DLConfig,Pbar,EpisodeList,provider):
    for EpisodeTitle, DownloadButton in zip(EpisodeList["Title"], EpisodeList["Button"]):
        DownloadDone = False
        eval(DownloadButton).click()
        DLConfig.wait('visible', timeout=100)
        DLConfig.DownloadButton.click()
        if app.FileExists.exists():
            app.FileExists.NoButton.click()
            print(f' Skipping.. {EpisodeTitle} (Already Downloaded)')
            if 'Hulu' in provider:
                main.child_window(class_name="QMessageBox").OKButton.click()
            if 'Disney' in provider:
                main.child_window(class_name="QMessageBox").OKButton.click()    
            if 'Amazon' in provider:
                main.child_window(class_name='VendorAmazon', control_type='Group').DownloadableVideosButton.click()
            dw.wait('visible', timeout=100)
            continue
        Pbar.wait('active',timeout=100)
        before = int(Pbar.legacy_properties()['Value'])
        print(f' Downloading...{EpisodeTitle} {before / 100}%', end="")
        while DownloadDone is False:
            after = int(Pbar.legacy_properties()['Value'])
            if after == 10000:
                print(f'\r Downloading...{EpisodeTitle} (Download Complete)')
                DownloadDone = True
            else:
                if after != before:
                    print(f'\r Downloading...{EpisodeTitle} {after / 100}%', end="")
                    before = after
        if 'Amazon' in provider:
            time.sleep(5) # because amazon doesnt return to the download window after downloading the post-processing message stops me from clicking back to the download menu. Gotta use a sleep until I can find a better workaround or become quick enough to inspect the post-processing msg. 
            main.child_window(class_name='VendorAmazon', control_type='Group').DownloadableVideosButton.click()
        dw.wait('visible', timeout=100)

    

app, main = Connect()
provider = GetProvider(main)
DLConfig, Pbar = FutureSpecs()
dw, sname = WaitForShow(main)
sList = GetSeasons(dw,provider)
if len(sList) == 1:
   Smax = 1
else:    
   Smax = SeasonLimiter(sList)
GottaBlast(sname,sList,Smax,app,dw,DLConfig,Pbar,provider)
print(f'Downloaded {Smax} seasons of {sname}. Now let me rest..')
KillMe = input('Press Enter to exit..')