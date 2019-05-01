import os
os.environ[ "ITK_GLOBAL_DEFAULT_NUMBER_OF_THREADS" ] = "4"
os.environ[ "ANTS_RANDOM_SEED" ] = "3"
import ants
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from numpy.polynomial import Legendre
from scipy import linalg
from scipy.stats.stats import pearsonr
# exec(open("src/sfJointReg.py").read())
powers_areal_mni_itk = pd.read_csv(ants.get_data('powers_mni_itk'))
rdir = "../"
id = '2001'
t1fn = rdir + 'data/LS' + id + "/unprocessed/3T/T1w_MPR1/LS"+id+"_3T_T1w_MPR1_gdc.nii.gz"
# now the bold data
boldfnsL = rdir + "data/LS2001/LS2001fmri/unprocessed/3T/rfMRI_REST1_LR/LS2001_3T_rfMRI_REST1_LR_gdc.nii.gz"
boldfnsR = rdir + "data/LS2001/LS2001fmri/unprocessed/3T/rfMRI_REST1_RL/LS2001_3T_rfMRI_REST1_RL_gdc.nii.gz"
# get the ref data
reffns1 = rdir + 'data/LS2001/LS2001fmri/unprocessed/3T/rfMRI_REST1_LR/LS2001_3T_rfMRI_REST1_LR_SBRef_gdc.nii.gz'
reffns2 = rdir + 'data/LS2001/LS2001fmri/unprocessed/3T/rfMRI_REST1_RL/LS2001_3T_rfMRI_REST1_RL_SBRef_gdc.nii.gz'

##  Distortion correction (without a field map)

i1 = ants.image_read( reffns1 )
i2 = ants.image_read( reffns2 )
und = ants.build_template( i1, ( i1, i2 ), 3, gradient_step = 0.5 )
t1 = ants.image_read( t1fn ).n3_bias_field_correction( 8 ).n3_bias_field_correction( 4 )
bmask = ants.get_mask( und, low_thresh = und.mean() * 0.75, high_thresh=1e9, cleanup = 3 ).iMath_fill_holes()
# ants.plot( und, bmask, axis=2, overlay_alpha = 0.33 )
# this is a fragile approach - not really recommended - but it is quick
t1mask = ants.get_mask( t1, low_thresh = t1.mean() * 1.1, high_thresh=1e9, cleanup = 5 ).iMath_fill_holes()
# ants.plot( t1, t1mask, axis=2, overlay_alpha = 0.33 )
t1rig = ants.registration( und * bmask, t1 * t1mask, "BOLDRigid" )
t1reg = ants.registration( und * bmask, t1 * t1mask, "SyNOnly",
  initialTransform = t1rig['fwdtransforms'],
  synMetric = 'CC', synSampling = 2, regIterations = (5) )
###########################


# The distortion to the T1 is greatly reduced.

# Brain masking
# Use the BOLD mask to extract the brain from the t1

t1maskFromBold = ants.apply_transforms( t1, bmask, t1reg['invtransforms'],
                                      interpolator = 'nearestNeighbor' )
t1 = ants.n4_bias_field_correction( t1, t1mask, 8 ).n4_bias_field_correction( t1mask, 4 )
bmask =  ants.apply_transforms( und, t1mask, t1reg['fwdtransforms'],
  interpolator = 'nearestNeighbor' ).morphology("close",3)
ofn = rdir + "features/LS" + id + "_mask_py.nii.gz"
ants.image_write( bmask, ofn )
t1toBOLD = ants.apply_transforms( und, t1, t1reg['fwdtransforms'] )
ofn = rdir + "features/LS" + id + "_t1ToBold_py.nii.gz"
ants.image_write( t1toBOLD, ofn )

## Tissue segmentation
# a simple method
################################################
qt1 = ants.iMath_truncate_intensity( t1, 0, 0.95 )
t1seg = ants.kmeans_segmentation( qt1, 3, t1mask, 0.2 )
volumes = ants.label_stats( t1seg['segmentation'], t1seg['segmentation'] )

boldseg = ants.apply_transforms( und, t1seg['segmentation'],
  t1reg['fwdtransforms'], interpolator = 'nearestNeighbor' )

## Template mapping
# include prior information e.g. from meta-analysis or anatomy

myvoxes = range(powers_areal_mni_itk.shape[0])
anat = powers_areal_mni_itk['Anatomy']
syst = powers_areal_mni_itk['SystemName']
Brod = powers_areal_mni_itk['Brodmann']
xAAL  = powers_areal_mni_itk['AAL']
ch2 = ants.image_read( ants.get_ants_data( "ch2" ) )
treg = ants.registration( t1 * t1mask, ch2, 'SyN' )

concatx2 = treg['invtransforms'] + t1reg['invtransforms']
pts2bold = ants.apply_transforms_to_points( 3, powers_areal_mni_itk, concatx2,whichtoinvert = ( True, False, True, False ) )
locations = pts2bold.iloc[:,:3].values
ptImg = ants.make_points_image( locations, bmask, radius = 3 )
networks = powers_areal_mni_itk['SystemName'].unique()
dfnpts = np.where( powers_areal_mni_itk['SystemName'] == networks[5] )
dfnImg = ants.mask_image(  ptImg, ptImg, level = dfnpts[0].tolist(), binarize=False )

# plot( und, ptImg, axis=3, window.overlay = range( ptImg ) )

bold2ch2 = ants.apply_transforms( ch2, und,  concatx2, whichtoinvert = ( True, False, True, False ) )


# Extracting canonical functional network maps
## preprocessing

csfAndWM = ( ants.threshold_image( boldseg, 1, 1 ) +
             ants.threshold_image( boldseg, 3, 3 ) ).morphology("erode",1)
bold = ants.image_read( boldfnsR )
boldList = ants.ndimage_to_list( bold )
avgBold = ants.get_average_of_timeseries( bold, range( 5 ) )
boldUndTX = ants.registration( und, avgBold, "SyN", regIterations = (15,4),
  synMetric = "CC", synSampling = 2, verbose = False )
boldUndTS = ants.apply_transforms( und, bold, boldUndTX['fwdtransforms'], imagetype = 3  )
motCorr = ants.motion_correction( boldUndTS, avgBold,
    type_of_transform="Rigid", verbose = True )
tr = ants.get_spacing( bold )[3]
highMotionTimes = np.where( motCorr['FD'] >= 0.5 )
goodtimes = np.where( motCorr['FD'] < 0.5 )
avgBold = ants.get_average_of_timeseries( motCorr['motion_corrected'], range( 5 ) )
#######################
nt = len(motCorr['FD'])
plt.plot(  range( nt ), motCorr['FD'] )
plt.show()
#################################################
mycompcor = ants.compcor( motCorr['motion_corrected'],
  filter_type='polynomial', degree=4 )
##########

smth = ( 1.0, 1.0, 1.0, 2.0 ) # this is for sigmaInPhysicalCoordinates = F
simg = ants.smooth_image( motCorr['motion_corrected'], smth, sigma_in_physical_coordinates = False )
gmseg = ants.threshold_image( boldseg, 2, 2 )
gmmat = ants.timeseries_to_matrix( simg, gmseg )
nuisance = mycompcor['components']
nuisance = np.c_[ nuisance, motCorr['FD'] ]
nuisance = np.c_[ nuisance, mycompcor['basis'] ]
gmmat = regress_components( gmmat[goodtimes[0],:], nuisance[goodtimes[0],:] )

dfnmat = ants.timeseries_to_matrix( simg, ants.threshold_image( dfnImg, 1, dfnImg.max() ) )
dfnmat = regress_components( dfnmat[goodtimes[0],:], nuisance[goodtimes[0],:] )
# dfnmatf = frequencyFilterfMRI( dfnmat, tr = tr, freqLo = 0.01, freqHi = 0.1,  opt = "trig" )
dfnsignal = dfnmat.mean( axis = 1 )

gmmatDFNCorr = np.zeros( gmmat.shape[1] )
for k in range( gmmat.shape[1] ):
    gmmatDFNCorr[ k ] = pearsonr( dfnsignal, gmmat[:,k] )[0]

corrImg = ants.make_image( gmseg, gmmatDFNCorr  )
corrImgPos = corrImg * ants.threshold_image( corrImg, 0.25, 1 )
ants.plot( avgBold, corrImgPos, axis=2, overlay_alpha = 0.6, cbar=False, nslices = 24, ncol=8, cbar_length=0.3, cbar_vertical=True )


"""

needs to be translated to python still

TODO:
  ilr - image based linear regression
  frequencyFilterfMRI - scipy probably butter filtfilt


getNetworkBeta <-function( motcorrIn, networkName = 'Default Mode' ) {

*implement*   noiseu = compcor( ccmat, ncompcor = 10 )
  smth = c( 1.0, 1.0, 1.0, 2.0 ) # this is for sigmaInPhysicalCoordinates = F
  simg = smoothImage( motcorrIn$moco_img, smth, sigmaInPhysicalCoordinates = F )
  gmmat = timeseries2matrix( simg, thresholdImage( boldseg, 2, 2 ) )
  tr = antsGetSpacing( bold )[4]
*implement*   gmmatf = frequencyFilterfMRI( gmmat, tr = tr, freqLo = 0.01, freqHi = 0.1,  opt = "trig" )

  goodtimes = rep( TRUE, dim( motcorrIn$moco_img )[4] )
  goodtimes[ 1:10 ] = FALSE  # signal stabilization
  highMotionTimes = which( motcorrIn$fd$MeanDisplacement >= 0.5 )
  for ( highs in -2:2 )
    highMotionTimes = c( highMotionTimes, highMotionTimes + highs )
  highMotionTimes = sort( unique( highMotionTimes ))
  goodtimes[ highMotionTimes ] = FALSE

  dfnpts = which( powers_areal_mni_itk$SystemName == networkName )
  print( paste(networkName, length(dfnpts)))
  dfnmask = maskImage( ptImg, ptImg, level = dfnpts, binarize = T )
  dfnmat = timeseries2matrix( simg, dfnmask )
  dfnmatf = frequencyFilterfMRI( dfnmat, tr = tr, freqLo = 0.01, freqHi = 0.1,  opt = "trig" )
  dfnsignal = rowMeans( data.matrix( dfnmatf ) )
  locmat = data.matrix( data.frame( gmmatf ))[goodtimes,]
  dnz = aslDenoiseR( locmat, dfnsignal[goodtimes], covariates = motcorrIn$fd[goodtimes,],
                     crossvalidationgroups = 8, selectionthresh = 0.2  )
  dfndf = data.frame( signal = dfnsignal, noiseu = noiseu, fd = motcorrIn$fd )
  dfndf = data.frame( signal = dfnsignal[goodtimes], noiseu = dnz$noiseu, fd = dnz$covariates )
  myform = paste( " mat ~ ", paste( names( dfndf ), collapse = "+") )
*implement* dfnmdl = ilr( dfndf, list( mat = locmat ),  myform )
  dfnBetaImg = makeImage(  thresholdImage( boldseg, 2, 2 ),  dfnmdl$tValue["signal",] )
  return( dfnBetaImg )
  }
dfnBetaImgR = getNetworkBeta( motcorr, 'Default Mode' )
dfnBetaImgL = getNetworkBeta( motcorrL, 'Default Mode' )
handR = getNetworkBeta( motcorr, "Sensory/Somatomotor Hand" )
handL = getNetworkBeta( motcorrL, "Sensory/Somatomotor Hand" )
mouthR = getNetworkBeta( motcorr, "Sensory/Somatomotor Mouth" )
mouthL = getNetworkBeta( motcorrL, "Sensory/Somatomotor Mouth" )
mouth = mouthL + mouthR
hand  = handL + handR
# vizBetaImg = getNetworkBeta( "Visual" )
# salBetaImg = getNetworkBeta( "Salience" )
####################################

# Structural functional joint registration
id1 = '2001'
s1f1 = ants.image_read( paste0( rdir, "features/LS", id1, '_dfnBetaImg.nii.gz' ) )
s1f2 = ants.image_read( paste0( rdir, "features/LS", id1, '_undistort.nii.gz' ) )
s1f3 = ants.image_read( paste0( rdir, "features/LS", id1, '_t1ToBold.nii.gz' ) )
s1fv = ants.image_read( paste0( rdir, "features/LS", id1, '_vizBetaImg.nii.gz' ) )
s1mask = ants.image_read( paste0( rdir, "features/LS", id1, '_mask.nii.gz' ) )
id2 = '3026'
s2f1 = ants.image_read( paste0( rdir, "features/LS", id2, '_dfnBetaImg.nii.gz' ) )
s2f2 = ants.image_read( paste0( rdir, "features/LS", id2, '_undistort.nii.gz' ) )
s2f3 = ants.image_read( paste0( rdir, "features/LS", id2, '_t1ToBold.nii.gz' ) )
s2fv = ants.image_read( paste0( rdir, "features/LS", id2, '_vizBetaImg.nii.gz' ) )
s2mask = ants.image_read( paste0( rdir, "features/LS", id2, '_mask.nii.gz' ) )
#############
jrig = ants.registration( s1f3 * s1mask, s2f3  * s2mask, "Affine"  )
ureg = ants.registration( s1f3, s2f3, "SyNOnly", initialTransform = jrig$fwd,  mask = s1mask )
jreg = ants.registration( s1f3, s2f3, "SyNOnly", initialTransform = jrig$fwd,  mask = s1mask,
  multivariateExtras = list(
   list( "mattes", s1fv, s2fv, 1, 32 ),
   list( "mattes", s1f1, s2f1, 1, 32 ) ), verbose = FALSE )
#############
vizWarped = ants.apply_transforms( s1f1, s2fv, ureg$fwdtransforms )
metric = antsrMetricCreate( s1fv, vizWarped, type="Correlation" )
strWarped = ants.apply_transforms( s1f1, s2f3, ureg$fwdtransforms )
smetric = antsrMetricCreate( s1f3, strWarped, type="Correlation" )
print( paste("univar-dfn", antsrMetricGetValue( metric ), 'str', antsrMetricGetValue( smetric ) ) )
#############
dfnWarped = ants.apply_transforms( s1f1, s2f1, jreg$fwdtransforms )
vizWarped = ants.apply_transforms( s1f1, s2fv, jreg$fwdtransforms )
metric = antsrMetricCreate( s1fv, vizWarped, type="Correlation" )
strWarped = ants.apply_transforms( s1f1, s2f3, jreg$fwdtransforms )
smetric = antsrMetricCreate( s1f3, strWarped, type="Correlation" )
print( paste("mulvar-dfn", antsrMetricGetValue( metric ), 'str', antsrMetricGetValue( smetric ) ) )
#############

# Visualize the "fixed" subject and DFN first.

# Then show the "deformed" subject and DFN second.

plot( s1f3, s1f1, alpha = 1.0, axis = 3, window.overlay = c(3, max(dfnBetaImg )),
      nslices = 24, ncolumns = 6, doCropping=FALSE )
plot( strWarped, dfnWarped, alpha = 1.0, axis = 3, window.overlay = c(3, max(dfnBetaImg )),
      nslices = 24, ncolumns = 6, doCropping=FALSE  )
"""
