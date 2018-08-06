fuck_cscope() {
    echo "Building crefs in CWD (for C/C++ project)..."
    find . -name '*.[cph]*' > cscope.files
    cscope -b -k -q
}

git_track_all_remote_branch() {
    for i in $(git branch -r | grep -vE "HEAD|master"); do git branch --track ${i#*/} $i; done
}
