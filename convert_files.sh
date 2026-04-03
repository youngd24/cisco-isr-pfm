#!/bin/bash
#
# Script to convert ulaw files to wav and/or au using sox.
# Usage: convert_files.sh [wav|au]
#   If no argument is given, both formats are generated.
#

subdirs="wx dictate followme silence phonetic digits ha letters"

# Determine which formats to process
case "$1" in
    wav)  formats="wav" ;;
    au)   formats="au" ;;
    "")   formats="wav au" ;;
    *)
        echo "Usage: $0 [wav|au]"
        echo "  No argument generates both formats."
        exit 1
        ;;
esac

# Create directory structure
echo "Checking directory structure..."
for dir in $formats; do
    echo -n "  Checking dir: $dir "
    if [[ ! -d $dir ]]; then
        echo "(created)"
        mkdir -p "$dir"
    else
        echo "(already exists)"
    fi
    for subdir in $subdirs; do
        echo -n "  Checking subdir: $dir/$subdir "
        if [[ ! -d "$dir/$subdir" ]]; then
            echo "(created)"
            mkdir -p "$dir/$subdir"
        else
            echo "(already exists)"
        fi
    done
done

# Convert files
echo ""
echo "Converting ulaw files..."
for i in $( find ./ulaw -name "*.ulaw" -printf '%P\n' ); do
    filename="${i%.*}"
    for fmt in $formats; do
        echo "  [$fmt] converting: $filename"
        sox -t ul -r 8000 -c1 "ulaw/$filename.ulaw" "$fmt/$filename.$fmt" pad 0.1 0
    done
done

echo ""
echo "Done."
