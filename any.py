import time
from pywinauto.application import Application
from pywinauto.findwindows import ElementNotFoundError
from pywinauto.findbestmatch import MatchError

print('Connecting to AnyStream...')
try:
    app = Application(backend="uia").connect(title_re="AnyStream*")
    mainwindow = app.AnyStream
    mainwindow.wait('visible')
except ElementNotFoundError:
    print('AnyStream is not open. Opening...')
    app = Application(backend="uia").start('C:/Program Files/RedFox/AnyStream/AnyStream.exe')
    mainwindow = app.AnyStream
    mainwindow.wait('visible')
print('Connected to AnyStream')


print('Waiting for user to find a show...')
DownloadWindow = mainwindow.child_window(title='Downloadable item(s)', class_name='DownloadableViewDialog')
DownloadWindow.wait('visible', timeout=1000)
ShowName = ''.join(DownloadWindow.Static1.texts())


print('Found a selection')
print(f'Loading episodes for {ShowName}...')
Episodes = DownloadWindow.descendants(class_name='DownloadableDetails')
EpisodeList = {"Title":[],"Button":[]}
count = -1
for episode in Episodes:
    count +=1
    title = episode.children_texts()[1]
    print(title)
    EpisodeList["Title"].append(title)
    EpisodeList["Button"].append(f'DownloadWindow.DownloadButton{count}')


DownloadConfig = mainwindow.child_window(title="Download configuration", class_name="DownloadConfigurationNetflix")
Progressbar = mainwindow.child_window(class_name="MultiBar")

for EpisodeTitle, EpisodeDownload in zip(EpisodeList["Title"], EpisodeList["Button"]):
    DownloadDone = False
    print(f'Downloading {EpisodeTitle}..')
    DownloadWindow.wait('visible')
    eval(EpisodeDownload).click()
    DownloadConfig.wait('visible')
    DownloadConfig.DownloadButton.click()
    if app.FileExists.exists():
        app.FileExists.NoButton.click()
        DownloadWindow.wait('visible')
        print(f'{EpisodeTitle} already downloaded (skipping)..')
        continue
    
    Progressbar.NetflixProgress
    Progressbar.NetflixProgress.wait('visible')
    before = int(Progressbar.NetflixProgress.legacy_properties()['Value'])
    print(f'\r Progress... {before / 100}%', end="")
    while DownloadDone is False:
        after = int(Progressbar.NetflixProgress.legacy_properties()['Value'])
        if after == 10000:
            print('\r Progress... 100%')
            DownloadDone = True
        if after != before:
            print(f'\r Progress... {after / 100}%', end="")
            before = after
    print(f'{EpisodeTitle} downloaded.')        