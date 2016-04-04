#!/bin/bash

# export FSLDIR=/usr/local/fsl
# export FSLOUTPUTTYPE=NIFTI_GZ
# export PATH=/usr/local/fsl/bin/:$PATH

root=/dat4/mw/hcp/single/100307
pushd $root
t1=$root/T1w
dmr=$t1/Diffusion

mkdir TVB && pushd TVB

# prep diffusion
mrconvert $dmr/data.nii.gz dwi.mif -fslgrad $dmr/b{vecs,vals}
dwi2mask dwi.mif mask.mif
dwiextract dwi.mif lowb.mif -bzero
mrconvert lowb.mif lowb.nii.gz

# prep fs results
mri_convert $t1/aparc+aseg.nii.gz aparc+aseg.nii.gz --out_orientation RAS -rt nearest
fslreorient2std aparc+aseg.nii.gz aparc+aseg-ro.nii.gz
mri_convert $t1/T1w_acpc_dc_restore.nii.gz T1.nii.gz --out_orientation RAS

# register
flirt -in lowb.nii.gz -ref T1.nii.gz -omat d2t.mat -out lowb-in-t1.nii.gz -cost mutualinfo
convert_xfm -omat t2d.mat -inverse d2t.mat
flirt -applyxfm -in aparc+aseg.nii.gz -ref lowb.nii.gz -out aparc+aseg-in-d.nii.gz -init t2d.mat -interp nearestneighbour
flirt -applyxfm -in T1.nii.gz -ref lowb.nii.gz -out t1-in-d.nii.gz -init t2d.mat

# register
flirt -in T1.nii.gz -ref lowb.nii.gz -omat t2d.mat -out T1-d.nii.gz -cost mutualinfo
flirt -applyxfm -in aparc+aseg.nii.gz -ref lowb.nii.gz -out aparc+aseg-d.nii.gz -init t2d.mat -interp nearestneighbour

# freeview -v T1-d.nii.gz lowb.nii.gz:colormap=heat aparc+aseg-d.nii.gz:colormap=jet

popd # TVB
popd # $root
