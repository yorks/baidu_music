##是什么?
一个用来下载百度音乐MP3(320k...)的工具


##有哪些特征？

* 支持下载整个专辑
* 支持下载指定歌曲
* 支持指定码率, 默认320k

## 用法


````
python2 download.py -h
download.py: a script to download baidu mp3 ...
Usage:
download.py -a ablum -s song -d dir -h help 
    -a, --ablum: the ablum you want to download, you can input the ablum_id or ablum_url
    -s, --song: the song you want to download, you can input the song_id or song_url
    -d, --dir: the dir to save the downloaded mp3 files, default: ~/baidu_mp3_download/
    -r, --rate: the the song rate in kbps, default: auto(320->192->...)
    -h, --help: to see this.
        --all : download all the songs by the given ablum, used with -a option together

e.g:

1. download an ablum:
$ python2 download.py -a http://music.baidu.com/album/31496572 -d ./31496572/
Warnning: the save dir[./31496572/] not exist, will be created autoly.
Downloading 四季列车.mp3(320 kbps) ... 100% done
Downloading 手语.mp3(320 kbps) ... 100% done
Downloading 公公偏头痛.mp3(320 kbps) ... 100% done
Downloading 明明就.mp3(320 kbps) ... 100% done
Downloading 傻笑.mp3(320 kbps) ... 100% done
Downloading 比较大的大提琴.mp3(320 kbps) ... 100% done
Downloading 爱你没差.mp3(320 kbps) ... 100% done
Downloading 红尘客栈.mp3(320 kbps) ... 100% done
Downloading 梦想启动.mp3(320 kbps) ... 100% done
Downloading 大笨钟.mp3(320 kbps) ... 100% done
Downloading 哪里都是你.mp3(320 kbps) ... 100% done
Downloading 乌克丽丽.mp3(320 kbps) ... 100% done

2. download a song:
$ python2 download.py -s http://music.baidu.com/song/31496563 -d ./
Downloading 红尘客栈.mp3(320 kbps) ... 100% done

```


##有问题反馈
在使用中有任何问题，欢迎反馈给我, 联系方式:

* 邮件(yorks.yang#163.com)
* weibo: [@空白-yy](http://weibo.com/iyangyou)

