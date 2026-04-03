#!/bin/bash
#

echo "Cleaning wav files"
find ./wav/ -name *.wav -exec rm {} \;

echo "Cleaning au files"
find ./au/ -name *.au -exec rm {} \;

echo "Done"
