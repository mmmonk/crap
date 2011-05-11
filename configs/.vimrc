if $HOSTNAME=~"solix"
  let weAreOnSolix=1
endif

set nocompatible 
set autoindent    " autoindent
"set autoread      " automatically read a file when it was modified outside of Vim
set background=dark
set backspace=indent,eol,start " powerful backspaces
set display=uhex  " include "uhex" to show unprintable characters as a hex number 
set enc=iso-8859-2
set esckeys       " recognize keys that start with <Esc> in Insert mode 
set expandtab     " spaces instead of tabs 
set ff=unix       " force unix fileformat
set ffs=unix,dos  " list of file formats to look for when editing a file
set hidden        " allows hidden buffers to stay unsaved
set ignorecase    " ignore case when using a search pattern
set incsearch     " Incremental search.
set laststatus=2  " when to use a status line for the last window 
set linebreak     " wrap long lines at a character in 'breakat'
set modeline
set modelines=1
set mouse=a
set nobackup      " no backups
set noerrorbells
set nosplitbelow
"set paste
set ruler
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
fixdel

filetype plugin on
filetype indent on

if !exists('weAreOnSolix')
  set ttyfast       " better terminal
  set completeopt=longest,menu,preview " completion options
  colorscheme desert
else
  set lazyredraw " do not redraw while running macros (much faster) (LazyRedraw)
endif

let maplocalleader=','        " all my macros start with ,

if has('diff')
  set diffopt=filler        " insert filler to make lines match up
  set diffopt+=iwhite       " ignore all whitespace
  if !exists('weAreOnSolix')
    set diffopt+=vertical     " make :diffsplit default to vertical
  endif
endif

if has("syntax")
  syntax on
endif

if has('gui_running')
  set guioptions-=T         " no toolbar
  "set number                " line numbers
  set guifont=Monospace\ 10 " gui font
  set nomh                  " no mouse hide
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
map <F3> :set number!<CR>

" toggle syntax
map <F4> :if exists("g:syntax_on") <bar> syntax off <bar> else <bar> syntax on <bar> endif<CR>

" gpg stuff
nmap <F5> :% ! gpg --clearsign<CR>
nmap <F6> :% ! gpg --verify<CR>
nmap <F7> :% ! gpg --encrypt<CR>
nmap a<F7> :% ! gpg -a --encrypt<CR>
nmap <F8> :% ! gpg --decrypt<CR>

" use ,ww to toggle line wrapping
nmap <LocalLeader>ww :set wrap! wrap?<cr>

" toggle paste mode.  Everything is inserted literally - no indending
set pastetoggle=<F11>

if has('autocmd')
  augroup openssl-enc
    au BufNewFile,BufReadPre *.enc :set secure viminfo= noswapfile nobackup nowritebackup history=0
    au BufRead *.enc :% ! openssl enc -d -aes-256-cbc 
    au BufWrite *.enc :% ! openssl enc -aes-256-cbc
  augroup END

"  augroup openssl-enca
"    au BufNewFile,BufReadPre *.enca :set secure viminfo= noswapfile nobackup nowritebackup history=0 binary
"    au BufRead *.enca :% ! openssl enc -a -d -aes-256-cbc 
"    au BufWrite *.enca :% ! openssl enc -a -aes-256-cbc
"  augroup END

  augroup VimConfig
    au!
    autocmd BufWritePost ~/.vimrc       so ~/.vimrc
    autocmd BufWritePost vimrc          so ~/.vimrc
  augroup END
endif

" local changes 
if filereadable(expand("~/.vimrc.local"))
  source ~/.vimrc.local
endif

set secure
