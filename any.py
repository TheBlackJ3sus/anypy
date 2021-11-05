from pywinauto.application import Application
from pywinauto.findwindows import ElementNotFoundError

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
            return
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
        Smax = 1
        return sList,Smax
    sList = dw.ListBox.texts()
    if len(sList) == 1:
        Smax = 1
    else:    
        Smax = SeasonLimiter(sList)
    return sList, Smax
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
        DLConfig.DownloadButton.click()
        if app.FileExists.exists():
            print(f' Skipping.. {EpisodeTitle} (Already Downloaded)')
            app.FileExists.NoButton.click()
            if 'Amazon' in provider:
                main.child_window(class_name='VendorAmazon', control_type='Group').DownloadableVideosButton.click()
                continue
            if 'Netflix' in provider:
                continue
            main.child_window(class_name="QMessageBox").OKButton.click()
            continue
        before = int(Pbar.legacy_properties()['Value'])
        print(f' Downloading...{EpisodeTitle} {before / 100}%', end="")
        while DownloadDone is False:
            after = int(Pbar.legacy_properties()['Value'])
            if after == 10000:
                print(f'\r Downloading.. {EpisodeTitle} (Download Complete)')
                DownloadDone = True
            else:
                if after != before:
                    print(f'\r Downloading.. {EpisodeTitle} {after / 100}%', end="")
                    before = after
        if 'Amazon' in provider:
            Pbar.wait_not('active',timeout=100)
            main.child_window(class_name='VendorAmazon', control_type='Group').DownloadableVideosButton.click()

    

app, main = Connect()
provider = GetProvider(main)
DLConfig, Pbar = FutureSpecs()
dw, sname = WaitForShow(main)
sList, Smax = GetSeasons(dw,provider)
GottaBlast(sname,sList,Smax,app,dw,DLConfig,Pbar,provider)
print(f'All {sname} downloads are complete. Now let me rest..')
KillMe = input('Press Enter to exit..')