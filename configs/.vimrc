" ~/.vimrc file
" $Id: 20120722$
" $Date: 2012-07-22 22:10:55$
" $Author: Marek Lukaszuk$
"
" ideas http://amix.dk/vim/vimrc.html
" vim --servername GVIM --remote-tab-silent

if $HOSTNAME=~"solix"
  let weAreOnSolix=1
endif

set autoindent    " autoindent
set autoread      " automatically read a file when it was modified outside of Vim
set background=dark
set backspace=indent,eol,start " powerful backspaces
set display=uhex  " include "uhex" to show unprintable characters as a hex number
set enc=iso-8859-2
set esckeys       " recognize keys that start with <Esc> in Insert mode
set expandtab     " spaces instead of tabs
set ffs=unix,dos  " list of file formats to look for when editing a file
set ff=unix       " force unix fileformat
set hidden        " allows hidden buffers to stay unsaved
"set hls
set ignorecase    " ignore case when using a search pattern
set incsearch     " Incremental search.
set laststatus=2  " when to use a status line for the last window
set linebreak     " wrap long lines at a character in 'breakat'
set modeline
set modelines=1
set mouse=a
set nobackup      " no backups
set nowritebackup
set nocompatible
set noerrorbells
set nosplitbelow
"set paste
set ruler
set scs
set shiftwidth=2
set showcmd       " Show current vim command in status bar
set showmatch     " Show matching parentheses/brackets
set showmode      " Show current vim mode
set smartcase     " override 'ignorecase' when pattern has upper case characters
set tabstop=2
set textwidth=0   " don't wrap words
set ttymouse=xterm
set visualbell    " use a visual bell instead of beeping
set wrap          " Wrap too long lines
"set verbose=5

" Tell vim to remember certain things when we exit
"  '10  :  marks will be remembered for up to 10 previously edited files
"  "100 :  will save up to 100 lines for each register
"  :20  :  up to 20 lines of command-line history will be remembered
"  %    :  saves and restores the buffer list
"  n... :  where to save the viminfo files
set viminfo='20,\"200,:50,%,n~/.viminfo
fixdel

filetype plugin on
filetype indent on

" set statusline=[%02n]\ %f\ %(\[%M%R%H]%)%=\ %4l,%02c%2V\ %P%*
set statusline=%f[%{strlen(&fenc)?&fenc:'none'},%{&ff}]%h%m%r%y%=%c,%l/%L\ %P
"set tabline=%T%X

let maplocalleader=','        " all my macros start with ,

if has("syntax")
  syntax on
endif

if has('diff')
  set diffopt=filler        " insert filler to make lines match up
  set diffopt+=iwhite       " ignore all whitespace
endif

if !exists('weAreOnSolix')
  set showtabline=2
  set diffopt+=vertical     " make :diffsplit default to vertical

  function! SwitchColorScheme(c1,c2)
    if g:colors_name == a:c1
      exe ":colorscheme ".a:c2
    else
      exe ":colorscheme ".a:c1
    endif
    set background=dark
  endfunction

  function! SetColorSchemaBaseOnTime(c1,c2)
    let hour = system("date +%H")
    if hour > 19 " between 19 and 8 use the c1
      exe ":colorscheme ".a:c1
    elseif hour < 8
      exe ":colorscheme ".a:c1
    else " during the day use c2
      exe ":colorscheme ".a:c2
    endif
    set background=dark
  endfunction

  set ttyfast       " better terminal
  set completeopt=longest,menu,preview " completion options

  "call SetColorSchemaBaseOnTime("desert","ron")
  colorscheme ron
  map <F3> :call SwitchColorScheme("desert","ron")<CR>

  if has('gui_running')
    " set the gui options to:
    "   g: grey inactive menu items
    "   m: display menu bar
    "   r: display scrollbar on right side of window
    "   b: display scrollbar at bottom of window
    "   t: enable tearoff menus on Win32
    "   T: enable toolbar on Win32
    set guioptions=r
    " set guioptions-=T         " no toolbar
    set number                " line numbers
    set guifont=Monospace\ 10 " gui font
    set nomh                  " no mouse hide
    "call SetColorSchemaBaseOnTime("desert","pablo")
    colorscheme pablo
    map <F3> :call SwitchColorScheme("desert","pablo")<CR>
  endif
else
  set lazyredraw            " do not redraw while running macros (much faster) (LazyRedraw)
endif

if has('spell')
  " <F12> highlight spelling mistakes
  nmap <F12> :set spell!<CR>
  " <sp> set dictionary to Polish
  nmap <LocalLeader>sp :set spl=pl<CR>

  " <se> set dictionary to English
  nmap <LocalLeader>se :set spl=en<CR>
  set spl=en
  set sps=best
endif

" <F1> toggle hlsearch (highlight search matches).
nmap <F1> :set hls!<CR>

" <F2>: toggle list (display unprintable characters).
nnoremap <F2> :set list!<CR>

" toggle line numbers
" map <F3> :set number!<CR>

" toggle syntax
map <F4> :if exists("g:syntax_on") <bar> syntax off <bar> else <bar> syntax on <bar> endif<CR>

" gpg stuff
nmap <F5> :% ! gpg --clearsign<CR>
nmap <F6> :% ! gpg --verify<CR>
nmap <F7> :% ! gpg --encrypt<CR>
nmap a<F7> :% ! gpg -a --encrypt<CR>
nmap <F8> :% ! gpg --decrypt<CR>

map <C-t><up> :tabr<cr>
map <C-t><down> :tabl<cr>
" map <C-t><left> :tabp<cr>
" map <C-t><right> :tabn<cr>

map <C-n> :tabnext<CR>
map <C-p> :tabprevious<CR>
map <C-t> :tabnew<CR>
map <C-e> :tabedit
map <C-r> :tabdo
map <C-s> :vsplit<CR>

inoremap <F9> <C-O>za
nnoremap <F9> za
onoremap <F9> <C-C>za
vnoremap <F9> zf

" use ,ww to toggle line wrapping
nmap <LocalLeader>ww :set wrap! wrap?<cr>

" toggle paste mode.  Everything is inserted literally - no indending
set pastetoggle=<F11>

if has('autocmd')

  function! ResCur()
    if line("'\"") <= line("$")
      normal! g`"
      return 1
    endif
  endfunction

  " clean up the \r at the end of lines
  function! StripTrailingCarriageReturn()
    exec "normal ma" | " this saves the current position in the file
    %s/\r//e
    exec "normal `a" | " this restores the current position in the file
  endfunction

  " this function as the name suggests strips the trailing
  " white characters from the end of the lines
  function! StripTrailingWhitespace()
    exec "normal ma" | " this saves the current position in the file
    %s/\s\+$//e
    exec "normal `a" | " this restores the current position in the file
  endfunction

  " this function modifies automatically the version number
  " and the last modified timestamp
  function! VersionUpdate()
    if &modified
      let endl = min ([20,line("$")]) " we will search max 20 first lines 
      exec "normal ma" | " this saves the current position in the file
      try
        exe ":1,".endl." s/\$Id.*\$/$Id: ".strftime("%Y%m%d")."$/e"
        exe ":1,".endl." s/\$Date.*\$/$Date: ".strftime("%F %T")."$/e"
      catch
      endtry
      exec "normal `a" | " this restores the current position in the file
    endif
  endfunction

  function! FileCleanUp()
    call StripTrailingCarriageReturn()
    call StripTrailingWhitespace()
  endfunction

  function! FileCleanUpCases()
    exec "normal ma" | " this saves the current position in the file
    exec ":%! cjc.pl"
    call StripTrailingCarriageReturn()
    call StripTrailingWhitespace()
    exec "normal `a" | " this restores the current position in the file
  endfunction

  augroup ResCur
    au!
    au BufWinEnter * call ResCur()
  augroup END

  au BufWrite * call VersionUpdate()
  " clean up trailing white spaces in my scripts
  au BufWrite $HOME/store/tools/* call StripTrailingWhitespace()
  " clean up files after reading in the cases subdirectory
  au BufRead $HOME/store/juniper/* call FileCleanUpCases()

  augroup Openssl-enc
    au!
    au BufNewFile,BufReadPre *.enc :set secure viminfo= noswapfile nobackup nowritebackup history=0
    au BufRead *.enc :% ! openssl enc -a -d -aes-256-cbc
    au BufWrite *.enc :% ! openssl enc -a -aes-256-cbc
  augroup END

  augroup Makefile
    au!
    au BufRead Makefile :set noexpandtab
  augroup END

"  augroup Openssl-enca
"    au!
"    au BufNewFile,BufReadPre *.enca :set secure viminfo= noswapfile nobackup nowritebackup history=0 binary
"    au BufRead *.enca :% ! openssl enc -a -d -aes-256-cbc
"    au BufWrite *.enca :% ! openssl enc -a -aes-256-cbc
"  augroup END

  augroup VimConfig
    au!
    au BufWritePost ~/.vimrc so ~/.vimrc
    "au BufWritePost .vimrc   so ~/.vimrc
  augroup END
endif

" local changes
if filereadable(expand("~/.vimrc.local"))
  so ~/.vimrc.local
endif

set secure

" #################################
" # adding custome header variables
" #################################
function! AddStdHeader()
  let s:line=line(".")
  call append(s:line," $Id$")
  call append(s:line+1," $Date$")
  call append(s:line+2," $Author: Marek Lukaszuk$")
  unlet s:line
endfunction

abbre fc call FileCleanUpCases()
abbre ah call AddStdHeader()
abbre sws call StripTrailingWhitespace()
abbre wu call VersionUpdate()
abbre te tabedit
