# $Id: 20120911$
# $Date: 2012-09-11 09:07:33$

# A righteous umask
if ($uid == 0) then
	umask 022
  if ( -d /home/case ) then
    cp -u /home/case/{.cshrc,.vimrc,.aliases,.tmux.conf,.screenrc} ~/
  endif
else
	umask 77
endif

set path = (/sbin /bin /usr/sbin /usr/bin /usr/games /usr/local/sbin /usr/local/bin /usr/X11R6/bin $HOME/bin )

#setenv LC_ALL		  "en_US.ISO8859-1"
setenv LC_CTYPE	  "pl_PL.ISO8859-2"
#setenv LC_CTYPE   "pl_PL.UTF-8"
#setenv	LC_MESSAGES	"en_US.ISO8859-1"
#setenv LC_TIME		  "en_US.ISO8859-1"

setenv EDITOR	vi
setenv BLOCKSIZE K
setenv PAGER more
where less > /dev/null && setenv PAGER less
where most > /dev/null && setenv PAGER most

setenv	SHOST `echo $HOST | awk -F'.' '{print $1}'`

if ($?prompt) then
  unset correct
  unset autocorrect
  unset autoexpand
  unset autologout
  set autorehash
  set addsuffix
  set autolist
  set color
  set colorcat
  set complete = "Enhance"
  set dunique
  set filec
  set histdup = 'erase'
  set history = 200
  set implicitcd
  set mail = (/var/mail/$USER)
  set matchebeep = 'never'
  set noclobber
  set noding
  set nokanji
  set notify
  set padhour
  set prompt = "[%n@%M %Y/%W/%D %P]\n%/ %# "
  set printexitvalue
  set rmstar
  set savehist = 0
  set symlinks = 'ignore'
  set time = 60
  set tperiod = 30
  set visiblebell
#	set watch  = (any any)
  set who    = "%n has %a %l from %M."
  if ( $?tcsh ) then
#		bindkey "^W" backward-delete-word
    bindkey -k up history-search-backward
    bindkey -k down history-search-forward
  endif

  # ssh-agent
  if ( -f ~/.ssh/ssh_agent ) then

    set TPID = `pgrep -nU $USER ssh-agent`

    if ($TPID == "") then
      ssh-agent -c | grep SSH >! ~/.ssh/ssh_agent
    else
      source ~/.ssh/ssh_agent
      if ($?SSH_AGENT_PID) then
        if ($SSH_AGENT_PID != $TPID) then
          ssh-agent -c | grep SSH >! ~/.ssh/ssh_agent
        endif
      else
        pkill -u $USER ssh-agent
        ssh-agent -c | grep SSH >! ~/.ssh/ssh_agent
      endif
    endif
    source ~/.ssh/ssh_agent
    unset TPID
  endif

  # gpg-agent
  if ( -f ~/.gpg-agent-info ) then
    setenv GPG_TTY `tty`
    set TPID = `pgrep -nU $USER gpg-agent`

    if ($TPID == "") then
      gpg-agent -q --daemon -c >! ~/.gpg-agent-info
      echo "setenv GPG_AGENT_PID `pgrep -U $USER gpg-agent`" >> ~/.gpg-agent-info
    else
      source ~/.gpg-agent-info
      if ($?GPG_AGENT_PID) then
        if ($GPG_AGENT_PID != $TPID) then
          gpg-agent -q --daemon -c >! ~/.gpg-agent-info
          echo "setenv GPG_AGENT_PID `pgrep -U $USER gpg-agent`" >> ~/.gpg-agent-info
        endif
      else
        gpg-agent -q --daemon -c >! ~/.gpg-agent-info
        echo "setenv GPG_AGENT_PID `pgrep -U $USER gpg-agent`" >> ~/.gpg-agent-info
      endif
    endif
    source ~/.gpg-agent-info
    unset TPID
  endif

  # alias file
  if ( -f ~/.aliases ) then
    source ~/.aliases
  endif

  if ($?TERM) then
    switch ($TERM)
      case "rxvt*":
      case "xterm*":
        alias postcmd 'printf "\033]0;$user@$SHOST \007"'
        #alias precmd  'printf "\033]0;${USER}@${SHOST} \007"'
        breaksw
      case "screen*":
        if ($?TMUX) then
          alias postcmd 'printf "\033]$user@$SHOST \007"'
          #alias precmd  'printf "\033]${USER}@${SHOST} \007"'
          #else
          #alias precmd  'printf "\033k\033\134"'
        endif
        breaksw
    endsw
  endif
  if ( -x /usr/games/fortune && -r ~/fortunes/mysli_zebrane ) then
    echo ""
    /usr/games/fortune ~/fortunes/mysli_zebrane
    echo ""
  endif

  ## sshhosts
  if ( -f ~/.ssh/config) then
    set sshhosts = (`awk '/^host /{gsub(/host /,"");gsub(/\S*\*\S*/,"");print}' $HOME/.ssh/config`)
    set sshhostsandusers = ($sshhosts `awk '/^\s*#/ {gsub(/.*/,"")}; /User /{gsub(/\s*$/,"@")};/User /{gsub(/\s*User /,"");print}' $HOME/.ssh/config | sort -u`)
  endif

  complete alias 'p/1/a/'
  complete bindkey 'p/*/b/'
  complete cd 'p/1/d/'
  complete chown 'c/*:/g/' 'p/1/u/:'
  complete dpkg 'p/1/(-I -l -L)/' 'n/-L/`dpkg -l | awk \{print\ \$2\}`/' 'n/-i/f:*.deb/'
  complete env 'c/*=/f/' 'p/1/e/=/' 'p/2/c/'
  complete find 'p/1/d/'
  complete last 'p/1/u/'
  complete ln 'c/-/(s)/'
  complete man 'p/*/c/'
  complete menv 'p/1/$sshhosts/'
  complete rmdir 'p/1/d/'
  complete setenv 'p/1/e/'
  complete set 'p/1/s/'
  complete unalias 'p/1/a/'
  complete uncomplete 'p/*/X/'
  complete unsetenv 'p/1/e/'
  complete unset 'p/1/s/'
  complete which 'p/1/c/'

  complete t 'p@1@`awk \$0\ \!\~\ \/^\\s\*#\/\ \{print\ \$2\} /etc/hosts`@'
  complete tc 'p@1@`awk \$0\ \!\~\ \/^\\s\*#\/\ \{print\ \$2\} /etc/hosts`@'
  complete sc 'p@1@`awk \$0\ \!\~\ \/^\\s\*#\/\ \{print\ \$2\} /etc/hosts`@'
  complete scp "c,*:/,F:/," "c,*:,F:$HOME," 'c/*@/$sshhosts/:/'
  complete s 'c/*@/$sshhosts/' 'p/*/$sshhostsandusers//'
  complete sfm 'p/1/(-L -R -D)/' 'p@*@`ls 1 ~/.ssh/sockets/ | sed "s/=//g;s/:.*//g"`@'
  complete sftp 'p/*/$sshhosts/'
  complete skm 'p@*@`ls -1 ~/.ssh/sockets/ | sed "s/=//g;s/:.*//g"`@'
  complete sk 'p/*/$sshhosts/'
  complete ssh 'c/*@/$sshhosts/' 'p/*/$sshhostsandusers//'
  complete telnet 'p@*@`awk \{print\ \$2\} /etc/hosts`@'

  ## some docs handling
  complete zathura 'p/1/f:*.{pdf,PDF}/'
  complete epdfview 'p/1/f:*.{pdf,PDF}/'
  complete xchm 'p/1/f:*.{chm,CHM}/'
  complete geeqie 'p/1/f:*.{jpg,JPG,png,PNG}/'
  complete unzip 'p/1/f:*.{zip,ZIP}/'
  complete FBReader 'p/1/f:*.{epub,EPUB}/'
  complete tar 'p/2/f:*.{tar,TAR,tar.gz,TAR.GZ,tgz,TGZ,tar.bz2,TAR.BZ2,tbz2,TBZ2}/'

  if ( -f ~/.lftp/bookmarks) then
    complete lftp 'p@1@`awk \{print\ \$1\} ~/.lftp/bookmarks`@'
  endif

  if ($uid == 0) then
    complete aptitude 'p/1/(show search versions update install upgrade dist-upgrade)/' 'p/2/`dpkg -l | awk \{print\ \$2\}`/'
    complete kill 'c/-/(s)/' 'n/-s/S/' 'p/*/`ps achx | awk \{print\ \$1\}`/'
    complete killall 'c/-/(s)/' 'n/-s/S/' 'p/*/`ps achx | awk \{print\ \$5\}`/'
  else
    complete aptitude 'p/1/(show search versions)/' 'p/2/`dpkg -l | awk \{print\ \$2\}`/'
    complete kill 'c/-/(s)/' 'n/-s/S/' 'p/*/`ps chx | awk \{print\ \$1\}`/'
    complete killall 'c/-/(s)/' 'n/-s/S/' 'p/*/`ps chx | awk \{print\ \$5\}`/'
  endif

  stty -ixon
endif
