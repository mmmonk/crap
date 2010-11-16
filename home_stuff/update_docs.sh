#!/bin/sh

cpwd=`pwd`
cd /home/case/store/docs

(/usr/bin/wget -4 -r -N -q -m ftp://ftp.cisco.com/pub/mibs/oid/oid.tar.gz && ( cd ftp.cisco.com/pub/mibs/oid/ && tar -zxf oid.tar.gz ) &
/usr/bin/wget -4 -r -N -q -m ftp://ftp.cisco.com/pub/mibs/schema/schema.tar.gz && ( cd ftp.cisco.com/pub/mibs/schema/ && tar -zxf schema.tar.gz ) &
/usr/bin/wget -4 -r -N -q -m ftp://ftp.cisco.com/pub/mibs/traps/traps.tar.gz && ( cd ftp.cisco.com/pub/mibs/traps && tar -zxf traps.tar.gz ) &
/usr/bin/wget -4 -r -N -q -m ftp://ftp.cisco.com/pub/mibs/v1/v1.tar.gz && ( cd ftp.cisco.com/pub/mibs/v1 && tar -zxf v1.tar.gz ) &
/usr/bin/wget -4 -r -N -q -m ftp://ftp.cisco.com/pub/mibs/v2/v2.tar.gz && ( cd ftp.cisco.com/pub/mibs/v2 && tar -zxf v2.tar.gz ) &
/usr/bin/wget -4 -r -N -q -m http://www.exploit-db.com/archive.tar.bz2 && ( cd www.exploit-db.com && tar -jxf archive.tar.bz2 )
echo "[+] ftp.cisco.com - done" ) &

(/usr/bin/lftp -c "open ftp://ftp.ietf.org ; mirror -e -c -p rfc/ /home/case/store/docs/ftp.ietf.org/rfc" > /dev/null
/usr/bin/lftp -c "open ftp://ftp.ietf.org ; mirror -e -c -p internet-drafts/ /home/case/store/docs/ftp.ietf.org/internet-drafts" > /dev/null
echo "[+] ftp.ietf.com - done" ) &

(/usr/bin/wget -4 -r -N -q -m --accept '*exploits.tgz' http://packetstormsecurity.nl 
/usr/bin/wget -4 -r -N -q -m --no-parent http://packetstormsecurity.nl/assess/
/usr/bin/wget -4 -r -N -q -m --no-parent http://packetstormsecurity.nl/papers/
echo "[+] packetstormsecurity.nl - done" ) &

#/usr/bin/wget -4 -r -N -q -m --no-parent --accept='*.pdf' http://www.juniper.net/techpubs/software/screenos/ &
(/usr/bin/puf -ns -P /home/case/store/docs -A pdf -r -u -xd http://www.juniper.net/techpubs/ 
echo "[+] www.juniper.net - done" ) &

#/usr/bin/puf -ns -P /home/case/store/oreilly -F -r -pr -c -xd http://hell.org.ua/Docs/oreilly/ &

(/usr/bin/wget -4 -D "blackhat.com" -H -r -N -q -m --no-check-certificate --accept '*zip,*gz,*bz2,*txt,*pdf,*ppt,*rtf,*doc' http://www.blackhat.com/html/bh-media-archives/bh-multi-media-archives.html
echo "[+] www.blackhat.com - done" ) &
(/usr/bin/wget -4 -r -N -q -m --no-check-certificate --reject '*.html,*.htm,*.jpg,*.gif' http://cansecwest.com/pastevents.html
echo "[+] cansecwest.com - done") &

/usr/bin/wget -4 -r -N -q -m --no-parent http://www.ngssoftware.com/research/papers/
/usr/bin/wget -4 -r -N -q -m --no-parent http://libnet.sourceforge.net/libnet.html
/usr/bin/wget -4 -r -N -q -m http://www.phenoelit-us.org/dpl/dpl.html
/usr/bin/wget -4 -r -N -q -m http://www.neohapsis.com/neolabs/neo-ports/neo-ports.svcs
/usr/bin/wget -4 -r -N -q -m http://www.neohapsis.com/neolabs/neo-ports/neo-ports.csv
/usr/bin/wget -4 -r -N -q -m http://www.iana.org/assignments/port-numbers
/usr/bin/wget -4 -r -N -q -m http://www.iana.org/assignments/ethernet-numbers
/usr/bin/wget -4 -r -N -q -m http://www.iana.org/assignments/multicast-addresses
/usr/bin/wget -4 -r -N -q -m http://standards.ieee.org/regauth/oui/oui.txt 
/usr/bin/wget -4 -r -N -q -m --no-parent http://www.internic.net/zones/
/usr/bin/wget -4 -r -N -q -m --accept '*.tar.gz' http://phrack.org 

wait

echo "[+] Cleaning empty directories and files "

/usr/bin/cleanlinks 

echo "[+] All done"


cd $cpwd
