from pywinauto.application import Application
from pywinauto.findwindows import ElementNotFoundError
from pywinauto.findbestmatch import MatchError
import time

def SelectSeason(DownloadWindow,SeasonList,sn):
    DownloadWindow.ComboBox.select(SeasonList[sn-1][0])

def GetSeasons(DownloadWindow):
    SeasonList = DownloadWindow.ListBox.texts()
    return SeasonList
    
def EpiBts(DownloadWindow,ShowName,sn):
    print(f'Grabbing episodes from {ShowName} Season {sn}...')
    Episodes = DownloadWindow.descendants(class_name='DownloadableDetails')
    DownloadBts = DownloadWindow.descendants(class_name='QPushButton')
    EpisodeList = {"Title":[],"Button":[]}
    count = 0
    for episode,downloadbt in zip(Episodes, DownloadBts):
        count +=1
        print(episode.children_texts()[1])
        EpisodeList["Title"].append(episode.children_texts()[1])
        EpisodeList["Button"].append(f'DownloadWindow.DownloadButton{count}')
    return EpisodeList  

def DownloadEpis(EpisodeList):
    for EpisodeTitle, EpisodeDownload in zip(EpisodeList["Title"], EpisodeList["Button"]):
        DownloadDone = False
        print(f'Downloading.. {EpisodeTitle}')
        eval(EpisodeDownload).click()
        DownloadConfig.DownloadButton.click()
        if app.FileExists.exists(timeout=10):
            app.FileExists.NoButton.click()
            print(f'Skipping.. {EpisodeTitle} (Already Downloaded)')
            DownloadWindow.wait('visible', timeout=1000)
            continue
        Progressbar.NetflixProgress.wait('visible')
        before = int(Progressbar.NetflixProgress.legacy_properties()['Value'])
        print(f'Progress... {before / 100}%', end="")
        while DownloadDone is False:
            after = int(Progressbar.NetflixProgress.legacy_properties()['Value'])
            if after == 10000:
                print('\r Progress... (Download Complete)')
                DownloadDone = True
            else:
                if after != before:
                    print(f'\r Progress... {after / 100}%', end="")
                    before = after
        DownloadWindow.wait('visible', timeout=1000)
    

print('Connecting to AnyStream...')
try:
    app = Application(backend="uia").connect(title_re="AnyStream*", auto_id='MainWindow', visible_only = False)
    mainwindow = app.AnyStream
    mainwindow.wait('ready')
except ElementNotFoundError:
    print('AnyStream is not open. Opening...')
    app = Application(backend="uia").start('C:/Program Files/RedFox/AnyStream/AnyStream.exe')
    mainwindow = app.AnyStream
    mainwindow.wait('ready')
print('Connected to AnyStream')

###Future Specs
DownloadConfig = mainwindow.child_window(title="Download configuration", class_name="DownloadConfigurationNetflix", visible_only = False, found_index=0)
Progressbar = mainwindow.child_window(class_name="MultiBar", visible_only = False)

print('Waiting for user to find a show...')
DownloadWindow = mainwindow.child_window(title='Downloadable item(s)', class_name='DownloadableViewDialog', visible_only = False)
DownloadWindow.wait('enabled', timeout=1000)
ShowName = ''.join(DownloadWindow.Static1.texts())

Seasons = GetSeasons(DownloadWindow)
count = 0
for dlseason in Seasons:
    count +=1
    SelectSeason(DownloadWindow,Seasons,count)
    time.sleep(1)
    EpiandBtList = EpiBts(DownloadWindow,ShowName,count)
    DownloadEpis(EpiandBtList)