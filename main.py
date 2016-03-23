"""
    filename: scrppingaweb.py
    author: JGarcia
    Description: We scrapp a webpage ot get the download links for audios.
    Advantage of this software: This use threads for parallel downloads.
"""
import sys
import urllib2
from __builtin__ import dict
import threading
import Queue
from genericpath import isfile

downloads_q = Queue.Queue()


class WorkerThread(threading.Thread):
    def __init__(self):
        super(WorkerThread, self).__init__()
        self.thr_flg = threading.Event()

    def run(self):

        while not self.thr_flg.isSet():
            global downloads_q
            print "Donwloading in: ", threading.currentThread()
            curr_task = downloads_q.get()

            if not self.is_file_downloaded(curr_task['dst_file']):
                try:
                    self.download_file(curr_task['remote_file_url'], curr_task['dst_file'])
                except:
                    print "REENQUEUING: ", str(curr_task)
                    # Reenqueue the task
                    downloads_q.put(curr_task)
                else:
                    self.create_metada(curr_task['text_file'], curr_task['metadata'] )


    def download_file(self, url_target, dst_file):
        import urllib
        import requests

        #head = requests.head(url_target)
        #requests.get(url_target, )
        # info = urllib.urlopen(url_target)
        # a = info.read()
        # print info

        try:
            urllib.urlretrieve(url_target, dst_file)
        except:
            # Erase the uncomplete file if it exists in path
            if isfile(dst_file):
                from subprocess import Popen
                Popen(["rm",dst_file])
            # Raise an exception
            raise RuntimeError

    def create_metada(self, text_file, metadata):
        with open(text_file,'w') as meta:
            meta.write(metadata)

    def is_file_downloaded(self, path):
        if isfile(path):
            return True
        else:
            return False

    def join(self, timeout=None):
        self.thr_flg.set()
        super(WorkerThread,self).join(timeout=timeout)

class TPFilesOnWeb():
    """
        Download files stored in web page, you specify
        de html tag element and a class to search and a
        path where to store files
    """
    def __init__(self, url_target, path_name):
        self.data =""
        self.url_target_list = []
        self.metada_file_list = []
        self.infodata = []
        self.url_target = url_target
        self.path_name = path_name
        #self.get_info(url_target, path_name)
        # self.download_file(path_name)
    def get_info(self):
        url_target = self.url_target
        pname = self.path_name
        import string
        letters = list(string.ascii_lowercase)
        for letter in letters:
            try:
                src = urllib2.urlopen(url_target.replace('%var',letter))
            except:
                pass
            else:
                data = src.read()
                from BeautifulSoup import BeautifulSoup
                tree = BeautifulSoup(data)
                #Get all a with class modal
                alla = tree.findAll('a',{'class':'modal'})
                for a in alla:
                    a_dict = eval(str(a['rel'].encode('utf-8')))
                    remote_file_name = self.get_file_name(a_dict['url'])
                    dst_file =pname+'/'+ remote_file_name
                    text_file = pname+'/'+remote_file_name.replace('.mp3','.txt')
                    remote_file_url = a_dict['url']
                    task = {'remote_file_url':remote_file_url,\
                                          'dst_file':dst_file,\
                                          'text_file':text_file,\
                                          'metadata':'filename: '+remote_file_name +'\r\n Description: ' + a_dict['desc'] }
                    #Enqueue the tasks to be processed in
                    #pool of threads
                    downloads_q.put(task)
                    self.infodata.append(task)
        return self.infodata
    def get_file_name(self, url_target):
        import re
        res_re = re.findall(r'^.*\/(.*\.mp3)$',url_target, re.IGNORECASE)
        if res_re:
            # print 'filename:',res_re[0]
            return res_re[0]
        else:
            return ''


def main(argv):
    # argv0=url
    # argv1=path
    #%var a-z, in lowercase
    argv0 = "http://latremendacorte.info/episodios-radio/radio-%var.php"
    argv1 = "../../Desktop/all_tp1"
    #Make sure path already exists, if not create it
    from subprocess import  Popen
    import os
    if not os.path.exists(argv1):
        Popen(['mkdir',argv1])
    Popen(['open',argv1])
    #Start file downloading
    nfile = TPFilesOnWeb(argv0,argv1)
    res_info = nfile.get_info()
    for item in res_info:
        print item
    N_THREADS =1
    wk_thr = [WorkerThread() for i in range(N_THREADS)]
    for thr in wk_thr:
        thr.start()

if __name__ == '__main__':
    main(sys.argv[1:])