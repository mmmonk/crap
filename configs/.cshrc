# A righteous umask
if ($uid == 0) then
	umask 022
else
	umask 77 
endif

set path = (/sbin /bin /usr/sbin /usr/bin /usr/games /usr/local/sbin /usr/local/bin /usr/X11R6/bin $HOME/bin )

#setenv  LC_ALL		  "en_US.ISO8859-1"
setenv  LC_CTYPE	  "pl_PL.ISO8859-2"
setenv	LC_MESSAGES	"en_US.ISO8859-1"
setenv  LC_TIME		  "en_US.ISO8859-1"

setenv	EDITOR	vi
setenv  BLOCKSIZE K
where more > /dev/null && setenv PAGER more
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
#	set implicitcd
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

  # alias file
  if ( -f ~/.aliases ) then
          source ~/.aliases
  endif

  if ($?TERM) then
    switch ($TERM)
      case "rxvt*":
      case "xterm*":
        alias postcmd 'printf "\033]0;$user@$SHOST \!#:0 \007"'
        alias precmd  'printf "\033]0;$USER@$SHOST \007"'
        breaksw
      case "screen*":
        alias precmd  'printf "\033k\033\134"'
        breaksw
    endsw
  endif

endif
