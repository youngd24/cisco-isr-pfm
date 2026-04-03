"""Library for reading and manipulating AU audio files."""

import struct

AU_MAGIC = b'.snd'


def read_au_header(f):
    magic = f.read(4)
    if magic != AU_MAGIC:
        raise ValueError(f"Not a valid AU file (magic: {magic})")
    data_offset = struct.unpack('>I', f.read(4))[0]
    data_size   = struct.unpack('>I', f.read(4))[0]
    encoding    = struct.unpack('>I', f.read(4))[0]
    sample_rate = struct.unpack('>I', f.read(4))[0]
    channels    = struct.unpack('>I', f.read(4))[0]
    return {
        'data_offset': data_offset,
        'data_size':   data_size,
        'encoding':    encoding,
        'sample_rate': sample_rate,
        'channels':    channels,
    }


def concat_au(file1, file2, outfile):
    with open(file1, 'rb') as f1, open(file2, 'rb') as f2:
        h1 = read_au_header(f1)
        h2 = read_au_header(f2)

        if h1['encoding'] != h2['encoding']:
            raise ValueError(f"Encoding mismatch: {h1['encoding']} vs {h2['encoding']}")
        if h1['sample_rate'] != h2['sample_rate']:
            raise ValueError(f"Sample rate mismatch: {h1['sample_rate']} vs {h2['sample_rate']}")
        if h1['channels'] != h2['channels']:
            raise ValueError(f"Channel mismatch: {h1['channels']} vs {h2['channels']}")

        f1.seek(h1['data_offset'])
        f2.seek(h2['data_offset'])

        audio1 = f1.read()
        audio2 = f2.read()

    combined_size = len(audio1) + len(audio2)

    with open(outfile, 'wb') as out:
        out.write(AU_MAGIC)
        out.write(struct.pack('>I', 24))
        out.write(struct.pack('>I', combined_size))
        out.write(struct.pack('>I', h1['encoding']))
        out.write(struct.pack('>I', h1['sample_rate']))
        out.write(struct.pack('>I', h1['channels']))

        out.write(audio1)
        out.write(audio2)

    return {
        'sample_rate':  h1['sample_rate'],
        'channels':     h1['channels'],
        'encoding':     h1['encoding'],
        'output_bytes': combined_size,
        'outfile':      outfile,
    }
