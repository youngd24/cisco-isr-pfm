#!/usr/bin/env python3
"""Concatenate two AU audio files, stripping the second file's header."""

import sys
from lib.au import concat_au

if __name__ == '__main__':
    if len(sys.argv) != 4:
        print(f"Usage: {sys.argv[0]} file1.au file2.au output.au")
        sys.exit(1)

    result = concat_au(sys.argv[1], sys.argv[2], sys.argv[3])
    print(f"Sample rate : {result['sample_rate']} Hz")
    print(f"Channels    : {result['channels']}")
    print(f"Encoding    : {result['encoding']}")
    print(f"Output size : {result['output_bytes']} bytes of audio data")
    print(f"Written to  : {result['outfile']}")
