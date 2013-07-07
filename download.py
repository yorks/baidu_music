#!/usr/bin/env python2
#-*- code: utf-8 -*-

import urllib2
import urllib
import os
import sys
import re
import getopt
import copy
import time
import random
import cookie_db

verbose=False

def usage():
    print "%s: a script to download baidu mp3 ..."% sys.argv[0]
    print "Usage:"
    print "%s -a ablum -s song -d dir -h help "% sys.argv[0]
    print "\t\033[1;32m-a, --ablum\033[m: the ablum you want to download, you can input the ablum_id or ablum_url"
    print "\t\033[1;32m-s, --song\033[m: the song you want to download, you can input the song_id or song_url"
    print "\t\033[1;32m-d, --dir\033[m: the dir to save the downloaded mp3 files, default: ~/baidu_mp3_download/"
    print "\t\033[1;32m-r, --rate\033[m: the the song rate in kbps, default: auto(320->192->...)"
    print "\t\033[1;32m-h, --help\033[m: to see this."
    print "\t\033[1;32m    --all \033[m: download all the songs by the given ablum, used with -a option together"
    print "\t\033[1;32m-v, --verbose\033[m: display more information."
    print


def _parse_argv():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "a:s:r:d:h:v", ["ablum=", "song=", "rate=", "dir=", "all", "help", "verbose"])
    except getopt.GetoptError, err:
        print err
        usage()
        sys.exit(1)
    aid=""
    sid=""
    rate='auto'
    save_dir="~/baidu_mp3_download/"
    down_all=False

    for o, v in opts:
        if o in ("-a", "--ablum"):
            aid = v
        elif o in ("-s", "--song"):
            sid = v
        elif o in ("-d", "--dir"):
            save_dir = v
        elif o in ("-r", "--rate"):
            rate = v
            if rate not in ['auto', '320', '192', '128']:
                print "\033[1;31mError\033[m: Input the wrong value of rate. rate must is auto|320|192|128"
                sys.exit(1)
        elif o in ("--all"):
            down_all=True
        elif o in ("-v", "--verbose"):
            global verbose
            verbose = True
        elif o in ("-h", "--help"):
            usage()
            sys.exit(1)
        else:
            print "\033[1;31mError\033[m: Unkonw option!"
            usage()
            sys.exit(1)
    if not aid and not sid:
        print "\033[1;31mError\033[m: missing the option -a or -s"
        print "\tmust given the ablum(ablum_id/ablum_url) by the option[-a] or"
        print "\tthe song(song_di/song_url) by the option[-s]"
        sys.exit(1)
    elif aid and sid:
        print "\033[1;33mWarnning\033[m: given the -a and -s option both means only used -s option"
        if sid.endswith('/'):
            sid = sid[:-1]
        if sid.startswith('http://'):
            sid = sid.split('/')[-1:][0]
        if not sid.isdigit():
            print "\033[1;31mError\033[m: Input the wrong value of ablum. the song id must digits"
            sys.exit(1)
        aid=''
    elif aid:
        if aid.endswith('/'):
            aid = aid[:-1]
        if aid.startswith('http://'):
            aid = aid.split('/')[-1:][0]
        if not aid.isdigit():
            print "\033[1;31mError\033[m: Input the wrong value of ablum. the ablum id must digits"
            sys.exit(1)
    elif sid:
        if sid.endswith('/'):
            sid = sid[:-1]
        if sid.startswith('http://'):
            sid = sid.split('/')[-1:][0]
        if not sid.isdigit():
            print "\033[1;31mError\033[m: Input the wrong value of ablum. the song id must digits"
            sys.exit(1)
    if not save_dir:
        print "\033[1;31mError\033[m: Input the wrong save_dir by option -d"
        sys.exit(1)
    save_path = os.path.expanduser(save_dir)
    if not os.path.exists( save_path ):
        print "\033[1;33mWarnning\033[m: the save dir[%s] not exist, will be created autoly."% save_path
        #os.makedirs(save_path)

    args={'aid':aid, 'sid':sid, 'save_dir':save_path, 'down_all':down_all, 'rate':rate}
    #print args
    return args


def get_cookie():
    cookies=''
    ff_cookie_file_path = cookie_db.get_firefox_cookie_file()
    if not ff_cookie_file_path:
        ff_cookie_file_path = raw_input('cannot found firefox cookie file, pls input its abs path:')
        if os.path.isfile( ff_cookie_file_path ):
            print "Input error, you iput the file not exist or not a file!"
            sys.exit(1)
    baidu_cookies = cookie_db.get_cookie_from_db(ff_cookie_file_path, '.baidu.com')
    baidu_music_cookies = cookie_db.get_cookie_from_db(ff_cookie_file_path, 'music.baidu.com')
    cookies = baidu_cookies + baidu_music_cookies
    return cookies

def progress_bar(count, block_size, total_size, song_info):
    """
    @count: downloaded
    """
    rate = float(count * block_size) / float(total_size)
    rate_num = int(rate * 100)
    print '\rDownloading %s.mp3(%s kbps) ... %d%%'% ( song_info['title'], song_info['rate'], rate_num),

    #print "[%s ]%d%%\r" % (('%%-%ds' % 100) % (100 * rate_num / 100 * '='), rate_num),
    if rate_num >= 100:
        print "done"
    sys.stdout.flush()


class BAIDU_MUSIC(object):
    def __init__(self, cookies):
        self.cookies = cookies
        self.headers = {
            'User-Agent':'Mozilla/5.0 (X11; Linux i686; rv:18.0) Gecko/20100101 Firefox/18.0',
            'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Cookie':'%s'% self.cookies
            }

    def request_baidu(self, url):
        if verbose: print "request url[%s]"% url
        host = url.split('/')[2]
        req=urllib2.Request(url=url, headers=self.headers)
        conn = urllib2.urlopen(req)
        return conn

    def get_song_list(self, aid):
        song_list = []
        url = "http://music.baidu.com/album/%s"% aid
        conn = self.request_baidu(url)
        res = conn.read()
        if verbose: print "parse album page to findout the song_list"
        # <a href="/song/31458076" title="Catch My Breath [Ark Angel Remix]">
        regex = re.compile(r'<a href="/song/(\d+)" title="(.*)">')
        song_list = regex.findall(res)
        return song_list

    def get_song_info(self,sid):
        song_info={}
        url = "http://music.baidu.com/song/%s/download"% sid
        conn = self.request_baidu(url)
        res = conn.read()
        res = res.replace(r'&quot;',r'"')
        if verbose: print "parse song page to get song info, download links..."
        regex_rate = re.compile(r'{"rate":(\d+).*')
        rate_list = regex_rate.findall(res)
        regex = re.compile(r'{"rate":(\d+),"link":"(.*)"}')
        url_list = regex.findall(res)
        title = ''
        ablum = ''
        singer = ''
        tmp_collect = False
        try:
            title  = re.findall('song_title:\s*"(.*)",',res)[0]
            ablum  = re.findall('album_name:\s*"(.*)",',res)[0]
            singer = re.findall('singer_name:\s*"(.*)",',res)[0]
        except:
            print "[Warnning]Cannot get the song title,ablum,singer info!"
            pass
        song_info={'sid':sid, 'title':title, 'ablum':ablum, 'singer':singer, 'down_list':{}}
        for rate, link in url_list:
            link=link.replace(r'\/', '/')
            down_link = "http://music.baidu.com"+link
            song_info['down_list'][rate]= down_link
        for rate in rate_list:
            if rate == '1000':
                if verbose:print "skip flac rate 1000"
                continue
            if rate not in song_info['down_list'].keys():
                down_link = 'http://yinyueyun.baidu.com/data/cloud/downloadsongfile?songIds=%s&rate=%s'% (sid, rate)
                if not self._iscollect( sid ):
                    if verbose: print "tmp collect the song."
                    tmp_collect = True
                    self.collect( sid )
                real_url = self.get_real_link( down_link )
                if tmp_collect:
                    if verbose: print "un collect the song."
                    self.collect( sid, do=False )
                song_info['down_list'][rate]= real_url

        if verbose: print "song_info: %s"% song_info
        return song_info

    def get_real_link(self, yinyueyun_link):
        conn = self.request_baidu(yinyueyun_link)
        real_url = conn.url
        return real_url

    def _iscollect(self, ids, type_='song'):
        url = 'http://music.baidu.com/data/user/isCollect?type=%s&ids=%s'% (type_, ids)
        conn = self.request_baidu( url )
        try:
            ret = eval( conn.read() )
        except:
            return False
        if ret['errorCode'] == 22000 and ret['data']['isCollect'] == 1:
            return True
        else:
            return False


    def collect(self, ids, type_='song', do=True):
        data = {'ids':ids, 'type':type_}
        dtime = int(time.time())
        r=str( random.random() )
        r3=str( random.randint(111,999) )
        r=r+str(dtime)+r3
        url = 'http://music.baidu.com/data/user/collect?.r=%s'% r
        if not do:
            url = 'http://music.baidu.com/data/user/deleteCollection?.r=%s'% r
        if verbose: print url
        pst_data = urllib.urlencode( data )
        cl=len(pst_data)
        headers = copy.deepcopy(self.headers)
        headers['Content-Length']=cl
        headers['Content-Type']='application/x-www-form-urlencoded; charset=UTF-8'
        headers['Referer']='http://music.baidu.com/song/%s'% ids
        req = urllib2.Request(url=url, headers=headers, data=pst_data)
        conn = urllib2.urlopen(req)
        try:
            ret = eval( conn.read() )
        except:
            return False
        if ret['errorCode'] == 22000:
            return True
        else:
            return False

    def download(self, song_info, rate='auto'):
        for c in ['|', '&', '*', '/', '^', '%', '$', '#', '!', ' ']:
            song_info['title'] = song_info['title'].replace(c, '_')

        save_path = song_info['save_dir'] + song_info['title'] + '.mp3'
        down_link = ''
        rate_list = song_info['down_list'].keys()
        rate_list.sort(key=int, reverse=True)

        if rate == 'auto':
            for r in rate_list:
                song_info['rate'] = r
                down_link = song_info['down_list'][r]
                break

        elif rate in rate_list:
            down_link = song_info['down_list'][rate]
            song_info['rate'] = rate

        if not down_link:
            return 404
        if not os.path.exists( song_info['save_dir'] ):
            os.makedirs( song_info['save_dir'] )
        if verbose: print "get song url[%s]"% down_link
        if verbose: print "save to:[%s]"% save_path
        try:
            urllib.urlretrieve(down_link, save_path,
                lambda block_num, block_size, total_size, song_info=song_info:progress_bar(block_num, block_size, total_size, song_info))
        except:
            print down_link
            return 500
        #conn = self.request_baidu(down_link)
        #res = conn.read()
        #fobj=open(save_path, 'wb')
        #fobj.write(res)
        #fobj.close()
        return 200


if __name__ == "__main__":
    args=_parse_argv()
    cookies = get_cookie()
    bd_music = BAIDU_MUSIC(cookies)
    if args['sid']:
        song_info = bd_music.get_song_info( args['sid'] )
        song_info['save_dir'] = args['save_dir']
        rcode = bd_music.download(song_info, args['rate'])
        if rcode == 200 :
            pass
            #print "done"
        elif rcode == 404 :
            print "Cannot found download link."
        elif rcode == 500:
            print "exception while downloading"

    elif args['aid']:
        song_list = bd_music.get_song_list( args['aid'] )
        for sid, title in song_list:
            args['sid'] = sid
            song_info = bd_music.get_song_info( args['sid'] )
            song_info['save_dir'] = args['save_dir']
            rcode = bd_music.download(song_info, args['rate'])
            if rcode == 200 :
                pass
                #print "done"
            elif rcode == 404 :
                print "Cannot found download link."
            elif rcode == 500:
                print "exception while downloading"
