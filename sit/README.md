# SIT Tone Files

This directory contains Special Information Tones (SIT) in `.au` format for use with a Cisco ISR, along with the script used to generate them.

## What are SIT Tones?

SIT tones are three-tone sequences played by the PSTN before a recorded announcement to indicate why a call could not be completed. Each class is identified by a unique combination of three tones at fixed frequencies, where each tone is either "short" (0.380s) or "long" (0.760s).

### Tone Frequencies

| Tone | Frequency |
|------|-----------|
| Low  | 913.8 Hz  |
| Mid  | 1370.6 Hz |
| High | 1776.7 Hz |

## SIT Classes

| File | Code | Class | Tone Pattern | Duration Pattern |
|------|------|-------|--------------|------------------|
| `1_IC_Intercept.au`    | IC | Intercept             | Low-Mid-High | Short-Short-Short (000) |
| `2_VC_Vacant_Code.au`  | VC | Vacant Code           | Low-Mid-High | Short-Short-Long  (001) |
| `3_RO_Reorder.au`      | RO | Reorder / Local Congestion    | Low-Mid-High | Short-Long-Short  (010) |
| `4_NC_No_Circuit.au`   | NC | No Circuit / Toll Congestion  | Low-Mid-High | Long-Short-Short  (100) |
| `5_IO_Ineffective_Other.au` | IO | Ineffective Other  | Low-Mid-High | Long-Long-Short   (110) |
| `6_UC_Nuisance.au`     | UC | Nuisance / Restricted | Low-Mid-High | Short-Long-Long   (011) |
| `7_RS_Reserved.au`     | RS | Reserved (Future)     | Low-Mid-High | Long-Short-Long   (101) |
| `8_XX_Unassigned.au`   | XX | Unassigned / Test     | Low-Mid-High | Long-Long-Long    (111) |

## Audio Format

The files are encoded for Cisco IOS compatibility:

- **Format:** `.au` (Sun/NeXT audio)
- **Codec:** G.711 µ-law (`pcm_mulaw`)
- **Sample rate:** 8000 Hz
- **Channels:** Mono

## Generating the Files

### Prerequisites

`ffmpeg` must be installed:

```bash
# Debian/Ubuntu
sudo apt install ffmpeg

# RHEL/CentOS/Fedora
sudo dnf install ffmpeg

# macOS
brew install ffmpeg
```

### Run the Script

```bash
cd sit/
bash generate_sit_files.sh
```

The script regenerates all eight `.au` files in the current directory. When complete, it prints:

```
Done. All SIT files are ready for TFTP upload.
```

## Deploying to a Cisco ISR

Upload the `.au` files to the router via TFTP and reference them in your IOS dial-peer or call treatment configuration. The files should be placed in the router's flash storage or served from a TFTP server accessible to the router.
