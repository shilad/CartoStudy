#!/usr/bin/env bash

for dir in content nav verification; do
    old=static/images/maps-orig/$dir
    new=static/images/maps/$dir
    rm -rf $new
    mkdir -p $new
    ls $old/ | while read f; do
        png="$new/$f"
        jpg="${png/png/jpg}"
        echo "creating $jpg"
        convert -background white -alpha remove -crop 1600x1600+400+0 -quality 75 "$old/$f" "$jpg"
    done
done