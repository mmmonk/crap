#!/bin/tcsh

# $Id: 20120722$
# $Date: 2012-07-22 16:32:15$
# $Author: Marek Lukaszuk$

set servers = (x tp r s c dkl pkl laaf)
foreach srv ($servers)
  echo "[+] server: ${srv}"
  cd ~;tar -cf - .cshrc .vimrc .aliases .screenrc .tmux.conf | ssh $srv 'tar -xvf -';
end
