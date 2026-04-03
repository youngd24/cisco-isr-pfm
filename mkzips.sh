#!/bin/bash
#
if [[ ! -d zips ]]; then
	mkdir -p zips
fi

echo "Creating au zip file"
zip -r zips/au.zip . -i "au/*"

echo "Creating wav zip file"
zip -r zips/wav.zip . -i "wav/*"

echo "Creating ulaw zip file"
zip -r zips/ulaw.zip . -i "ulaw/*"

echo "Done"
