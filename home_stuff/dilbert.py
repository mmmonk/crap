#!/usr/local/bin/python

# $Id$





import smtplib
from email.MIMEImage import MIMEImage
from email.MIMEMultipart import MIMEMultipart

import datetime
import imghdr
import os
import re
import time
import urllib

url = "http://www.dilbert.com"
me = "your@email.com"
dimg = "/dir/where/to/store/data/"
logfile = "dilbert.log"
ok = 0 

try:
	oldfile = file(dimg+logfile).read()
except:
	oldfile = ""

while ok == 0:
	sock = urllib.urlopen(url)
	html = sock.read()
	sock.close()
	webimg = url+re.search('(\/comics\/dilbert\/archive\/images\/dilbert\d+\.\w+)',html).group(1)
	file = re.search('\/(dilbert\d+\.\w+)',webimg).group(1)

	if oldfile == file:
		time.sleep(1800)
	else:
		ok = 1 

		image = dimg+file
		urllib.urlcleanup()
		urllib.urlretrieve(webimg,image);

		try:
			imgtype = imghdr.what(image)
			if imgtype == 'gif' or imgtype == 'jpeg':
				pass
			else:
				ok = 0
				time.sleep(30)
		except:
			ok = 0
			time.sleep(30)
		

log = open(dimg+logfile,"w")
log.write(file)
log.close()

now = datetime.datetime.now()

msg = MIMEMultipart()
msg['Subject'] = 'dilbert daily mail - ' + now.ctime()
msg['From'] = me 
msg['To'] = me 
msg.preamble = '' 
msg.epilogue = ''
fd = open(image,'rb')
img = MIMEImage(fd.read())
fd.close()
msg.attach(img)

s = smtplib.SMTP()
ok = 0
while ok == 0:
	try:
		s.connect()
		s.sendmail(me, [me], msg.as_string())
		s.close()
		ok = 1
	except:
		time.sleep(60)

os.remove(image)
