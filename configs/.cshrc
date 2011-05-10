# A righteous umask
if ($uid == 0) then
	umask 022
else
	umask 77 
endif

set path = (/sbin /bin /usr/sbin /usr/bin /usr/games /usr/local/sbin /usr/local/bin /usr/X11R6/bin $HOME/bin )

#setenv LC_ALL		  "en_US.ISO8859-1"
setenv LC_CTYPE	  "pl_PL.ISO8859-2"
#setenv	LC_MESSAGES	"en_US.ISO8859-1"
#setenv LC_TIME		  "en_US.ISO8859-1"

setenv EDITOR	vi
setenv BLOCKSIZE K
setenv PAGER more
where less > /dev/null && setenv PAGER less
where most > /dev/null && setenv PAGER most

#setenv	GPG_TTY `tty`
setenv	SHOST `echo $HOST | awk -F'.' '{print $1}'`

if ($?prompt) then
  unset correct
  unset autocorrect
  unset autoexpand
  unset autologout
  set addsuffix
  set autolist
  set color
  set colorcat
  set dunique
  set filec
  set histdup = 'erase'
  set history = 200
  set mail = (/var/mail/$USER)
  set matchebeep = 'never'
  set noclobber
  set noding
  set nokanji
  set notify
  set prompt = "[%n@%M %Y/%W/%D %P]\n%/ %# "
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
    source ~/.ssh/ssh_agent

    if ($?SSH_AGENT_PID) then
      if ( { kill -s 0 $SSH_AGENT_PID > /dev/null } == 0 ) then
        ssh-agent -c | grep SSH >! ~/.ssh/ssh_agent
      endif
    else
      ssh-agent -c | grep SSH >! ~/.ssh/ssh_agent
    endif
    source ~/.ssh/ssh_agent
  endif

  # gpg-agent
  if ( -f ~/.gpg-agent-info ) then
    setenv GPG_TTY `tty`
    source ~/.gpg-agent-info
    if ($?GPG_AGENT_PID) then
      if ( { kill -s 0 $GPG_AGENT_PID > /dev/null } == 0 ) then
        gpg-agent -q --daemon -c >! ~/.gpg-agent-info
        echo "setenv GPG_AGENT_PID `pgrep -u $USER gpg-agent`" >> ~/.gpg-agent-info
      endif
    else
      gpg-agent -q --daemon -c >! ~/.gpg-agent-info
      echo "setenv GPG_AGENT_PID `pgrep -u $USER gpg-agent`" >> ~/.gpg-agent-info
    endif
    source ~/.gpg-agent-info
  endif

  # alias file
  if ( -f ~/.aliases ) then
    source ~/.aliases
  endif

  if ($?TERM) then
    switch ($TERM)
      case "rxvt*":
      case "xterm*":
        alias postcmd 'printf "\033]0;$user@$SHOST \!#:0 \007"'
        alias precmd  'printf "\033]0;${USER}@${SHOST} \007"'
        breaksw
      case "screen*":
        if ($?TMUX) then
          alias postcmd 'printf "\033]$user@$SHOST \!#:0 \007"'
          alias precmd  'printf "\033]${USER}@${SHOST} \007"'
        else
          alias precmd  'printf "\033k\033\134"'
        endif
        breaksw
    endsw
  endif
  if ( -x /usr/games/fortune && -r ~/fortunes/mysli_zebrane ) then
    echo ""
    /usr/games/fortune ~/fortunes/mysli_zebrane
    echo ""
  endif

  complete ssh 'p/*/$sshhosts/'
  complete s 'p/*/$sshhosts/'
  complete sftp 'p/*/$sshhosts/'
  complete scp 'p/*/$sshhosts/'
  complete sk 'p/*/$sshhosts/'
endif
