#!/bin/bash
################################################################################
#
# generate_sit_files.sh
#
# Shell script to generate phone network SIT files in au format
# suitable for hosting on a Cisco ISR 
#
# Make sure ffmpeg is installed first
#
################################################################################

# Tone Frequencies (Hz)
ltone="913.8"
mtone="1370.6"
htone="1776.7"

# Durations (Seconds)
short="0.276"
long="0.380"
endpad="0.100"

# Audio Settings for Cisco IOS
bitrate="8000"
codec="pcm_mulaw"

# Function to generate the SIT file
# Usage: generate_sit <filename> <dur1> <dur2> <dur3>
generate_sit() {
    local outfile=$1
    local d1=$2
    local d2=$3
    local d3=$4

    echo "Generating $outfile..."
    
    ffmpeg -y -hide_banner -loglevel error \
    -f lavfi -i "sine=f=$ltone:d=$d1" \
    -f lavfi -i "sine=f=$mtone:d=$d2" \
    -f lavfi -i "sine=f=$htone:d=$d3" \
    -f lavfi -i "anullsrc=r=$bitrate:cl=mono,atrim=duration=$endpad" \
    -filter_complex "[0:a][1:a][2:a][3:a]concat=n=4:v=0:a=1" \
    -ar $bitrate -ac 1 -codec:a $codec "$outfile"
}

# --- SIT Class Generation ---

# Class 1: Intercept (IC) - Pattern: Short-Short-Short (000)
generate_sit "1_IC_Intercept.au" $short $short $short

# Class 2: Vacant Code (VC) - Pattern: Short-Short-Long (001)
generate_sit "2_VC_Vacant_Code.au" $short $short $long

# Class 3: Reorder / Local Congestion (RO) - Pattern: Short-Long-Short (010)
generate_sit "3_RO_Reorder.au" $short $long $short

# Class 4: No Circuit / Toll Congestion (NC) - Pattern: Long-Short-Short (100)
generate_sit "4_NC_No_Circuit.au" $long $short $short

# Class 5: Ineffective Other (IO) - Pattern: Long-Long-Short (110)
generate_sit "5_IO_Ineffective_Other.au" $long $long $short

# Class 6: Nuisance / Restricted (UC) - Pattern: Short-Long-Long (011)
generate_sit "6_UC_Nuisance.au" $short $long $long

# Class 7: Future/Reserved (101)
generate_sit "7_RS_Reserved.au" $long $short $long

# Class 8: Unassigned/Test (111)
generate_sit "8_XX_Unassigned.au" $long $long $long

echo "Done. All SIT files are ready for TFTP upload."
