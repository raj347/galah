set nocompatible        " Use Vim defaults (much better!)
set bs=2                " Allow backspacing over everything in insert mode
set backup              " Keep a backup file
set viminfo='20,\"50    " Read/write a .viminfo file, don't store more than 50 lines of registers
set history=50          " Keep 50 lines of command line history
set expandtab           " Expands <TAB> into spaces
set sw=4                " Auto indent is set to 4 spaces
set ts=4                " Number of spaces used for tab
set wrap                " Allows for wrap on sentences
set ruler               " Show the cursor position all the time
set number              " Show line numbers
syntax on               " Turn syntax highlighting on
"colorscheme default     " Set colorscheme
highlight Normal guibg=Black guifg=White
set background=dark showmatch
cmap <F5> :nohlsearch<Enter>
