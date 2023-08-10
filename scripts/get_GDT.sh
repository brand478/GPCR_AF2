#!/bin/bash
# https://github.com/JoanaMPereira/CASP14_high_accuracy
workdir=$1
mol2process=$2
lga='/proj/berzelius-2021-85/users/x_zeych/LGA_package_src/lga'

cd $workdir

# Get AAMOL label for peptides
$lga -aa -ch1:B  -ch2:B $mol2process > $mol2process.res
# Use LGA alignment records to select resces for GDT calculations
cat MOL2/$mol2process > MOL2/$mol2process.copy
grep "^AAMOL1 " $mol2process.res >> MOL2/$mol2process.copy
grep "^AAMOL2 " $mol2process.res >> MOL2/$mol2process.copy

# Calculate structural alignment for GDC_TS and using CA, the default settign is 5Å, it can be altered with -d:n
$lga -3 -sia -al -atom:CA -d:4 $mol2process.copy > $mol2process.gdc_ts_ha

# calculate GDT_TS
# cat $mol2process.gdc_ts_ha | grep "GDT PERCENT_AT" | awk '{ V=($4+$6+$10+$18)/4.0; printf "GDT_TS = %6.2f\n",V; }'
# awk '/GDT PERCENT_AT/ {printf "GDT_TS = %6.2f\n", ($4+$6+$10+$18)/4.0}' $mol2process.gdc_ts_ha
rm $mol2process.res
rm MOL2/$mol2process.copy