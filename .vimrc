syntax enable
syntax on
set backspace=indent,eol,start
autocmd FileType python setlocal foldmethod=indent
set foldlevel=99
set nu
set hlsearch
hi Search term=standout ctermfg=0 ctermbg=3
set tags=tags;/
filetype plugin on
set ts=4
set expandtab
set autoindent
set runtimepath^=~/.vim/bundle/ctrlp.vim
set t_Co=256
set cursorline
set cursorcolumn
set colorcolumn=88
highlight CursorLine cterm=none ctermbg=236
highlight CursorColumn cterm=none ctermbg=236
highlight colorcolumn cterm=none ctermbg=236
execute pathogen#infect()
filetype indent on
autocmd FileType python setlocal et sta sw=4 sts=4
autocmd FileType python set omnifunc=pythoncomplete#Complete
let g:pydiction_location = '~/.vim/tools/pydiction/complete-dict'
let g:pydiction_menu_height = 20
let g:NERDTreeWinPos = "right"
" 设置NerdTree
map <F3> :NERDTreeMirror<CR>
map <F3> :NERDTreeToggle<CR>
let mapleader = ","
let g:EasyMotion_smartcase = 1
let g:EasyMotion_startofline = 0 " keep cursor colum when JK motion
map <Leader><leader>h <Plug>(easymotion-linebackward)
map <Leader><Leader>k <Plug>(easymotion-j)
map <Leader><Leader>j <Plug>(easymotion-k)
map <Leader><leader>l <Plug>(easymotion-lineforward)
" 重复上一次操作, 类似repeat插件, 很强大
map <Leader><leader>. <Plug>(easymotion-repeat)
let g:neocomplete#enable_at_startup = 1
let g:neocomplete#enable_smart_case = 0
let g:neocomplete#sources#syntax#min_keyword_length = 1
let g:neocomplete#enable_auto_select = 0
let g:neocomplete#enable_insert_char_pre = 1
let g:SuperTabDefaultCompletionType="context"
if has("autocmd")
    autocmd BufRead *.txt set tw=78
    autocmd BufReadPost *
    \ if line("'\"") > 0 && line ("'\"") <= line("$") |
    \   exe "normal g'\"" |
    \ endif
endif
