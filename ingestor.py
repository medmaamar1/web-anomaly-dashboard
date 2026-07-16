from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time 
from datetime import datetime,timedelta
import threading
LOG_FILE ='log.file'
class LogHandler(FileSystemEventHandler):
    def __init__(self):
        self.last_position=0
        self.lines=[]
    def on_modified(self,event):
        if event.src_path.endswith(LOG_FILE):
            with open(LOG_FILE,'r') as f:
                f.seek(self.last_position)
                lines=f.readlines()
                self.last_position=f.tell()
                for new_line in lines:
                    print(new_line.strip())
    def get_lines(self):
        new=self.lines
        self.lines=[]
        return new
    
def start_ingestor():
    event_handler=LogHandler()
    observer=Observer()
    observer.schedule(event_handler,path='.',recursive=False)
    observer.start()
    threading.Thread(target=lambda:observer.join(),daemon=True).start()
    return event_handler