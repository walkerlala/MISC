fuck_cscope() {
    echo "Building crefs in CWD (for C/C++ project)..."
    find . -name '*.[cph]*' > cscope.files
    cscope -b -k -q
}

git_track_all_remote_branch() {
    for i in $(git branch -r | grep -vE "HEAD|master"); do git branch --track ${i#*/} $i; done
}

install_shadowsocks_libev() {
    apt-get install software-properties-common -y
    add-apt-repository ppa:max-c-lv/shadowsocks-libev -y
    apt-get update
    apt install shadowsocks-libev -y
}
