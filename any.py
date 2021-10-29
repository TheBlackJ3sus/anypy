import time
from pywinauto.application import Application
from pywinauto.findwindows import ElementNotFoundError
from pywinauto.findbestmatch import MatchError

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


print('Waiting for user to find a show...')
DownloadWindow = mainwindow.child_window(title='Downloadable item(s)', class_name='DownloadableViewDialog', visible_only = False)
DownloadWindow.wait('enabled', timeout=1000)
ShowName = ''.join(DownloadWindow.Static1.texts())


print('Found a selection')
print(f'Grabbing episodes from {ShowName}...')
Episodes = DownloadWindow.descendants(class_name='DownloadableDetails')
DownloadBts = DownloadWindow.descendants(class_name='QPushButton')
EpisodeList = {"Title":[],"Button":[]}
count = 0
for episode,downloadbt in zip(Episodes, DownloadBts):
    count +=1
    print(episode.children_texts()[1])
    EpisodeList["Title"].append(episode.children_texts()[1])
    EpisodeList["Button"].append(f'DownloadWindow.DownloadButton{count}')


###Future Specs
DownloadConfig = mainwindow.child_window(title="Download configuration", class_name="DownloadConfigurationNetflix", visible_only = False, found_index=0)
Progressbar = mainwindow.child_window(class_name="MultiBar", visible_only = False)


print('Starting Downloads...')
for EpisodeTitle, EpisodeDownload in zip(EpisodeList["Title"], EpisodeList["Button"]):
    DownloadDone = False
    print(f'Downloading.. {EpisodeTitle}')
    eval(EpisodeDownload).click()
    DownloadConfig.DownloadButton.click()
    time.sleep(1)
    if app.FileExists.exists():
        app.FileExists.NoButton.click()
        DownloadWindow.wait('visible', timeout=1000)
        continue
    Progressbar.NetflixProgress.wait('visible')
    mainwindow.minimize()
    before = int(Progressbar.NetflixProgress.legacy_properties()['Value'])
    print(f'\r Progress... {before / 100}%', end="")
    while DownloadDone is False:
        after = int(Progressbar.NetflixProgress.legacy_properties()['Value'])
        if after == 10000:
            print('\r Progress... (Download Complete)')
            DownloadDone = True
        if after != before:
            print(f'\r Progress... {after / 100}%', end="")
            before = after
    print(f'{EpisodeTitle} downloaded.')
    mainwindow.restore().set_focus()
    DownloadWindow.wait('visible', timeout=1000)