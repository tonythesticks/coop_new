#!/usr/bin/python

import urllib.request
#import urllib2
#import requests

urllib.request.urlopen('http://192.168.1.104:8080/json.htm?type=command&param=switchlight&idx=35&switchcmd=On')

#request = urllib.Request(url)
#response = urllib.urlopen(request)
