#!/bin/bash

if [ "X$1" == "X" ]; then
    echo "Usage: install.sh destination"
    exit 0;
fi
dest=$1

mkdir -p $dest

if [ ! -d $dest ]; then
    echo "Unable to create destination directory"
    exit 1;
fi

cp *.pl *.cgi *.html $dest
cp htaccess $dest/.htaccess
chmod a+x $dest/*.pl $dest/*.cgi

mkdir -p $dest/lib
cp lib/* $dest/lib

