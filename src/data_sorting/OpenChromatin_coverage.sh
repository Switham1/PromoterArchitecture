#!/bin/bash -e
#% of nucleotides falling within open chromatin
#$1 is promoter bed file
#$2 is the folder name
#$3 is the motifs bed file location
#$4 is the TFBS motifs_mapped bed file


#make directory if doesn't already exist
mkdir -p ../../data/output/$2/chromatin_coverage/

#retrieve filename from file path
xbase=${1##*/}
xpref=${xbase%.*}
coverageBed -a $1 -b ../../data/ATAC-seq/potter2018/Roots_NaOH_peaks_all.bed > ../../data/output/$2/chromatin_coverage/${xpref}RootOpenChrom.bp_covered.txt
coverageBed -a $1 -b ../../data/ATAC-seq/potter2018/Shoots_NaOH_peaks_all.bed > ../../data/output/$2/chromatin_coverage/${xpref}ShootOpenChrom.bp_covered.txt
coverageBed -a $1 -b ../../data/ATAC-seq/potter2018/intersectRootsShoots_PeaksInBoth.bed > ../../data/output/$2/chromatin_coverage/${xpref}ShootRootIntersectOpenChrom.bp_covered.txt

#Also run bedtools intersect and output files to the same location (not currently used by any subsequent scripts)
intersectBed -wo -a $1 -b ../../data/ATAC-seq/potter2018/Roots_NaOH_peaks_all.bed > ../../data/output/$2/chromatin_coverage/${xpref}RootOpenChrom.intersect.txt
intersectBed -wo -a $1 -b ../../data/ATAC-seq/potter2018/Shoots_NaOH_peaks_all.bed > ../../data/output/$2/chromatin_coverage/${xpref}ShootOpenChrom.intersect.txt
intersectBed -wo -a $1 -b ../../data/ATAC-seq/potter2018/intersectRootsShoots_PeaksInBoth.bed > ../../data/output/$2/chromatin_coverage/${xpref}ShootRootIntersectOpenChrom.intersect.txt

##Also run bedtools intersect on promoter motifs and output files to the same location
intersectBed -wo -a $3 -b ../../data/ATAC-seq/potter2018/intersectRootsShoots_PeaksInBoth.bed > ../../data/output/$2/chromatin_coverage/${xpref}ShootRootIntersectOpenChrom.motifsintersect.bed
intersectBed -wa -a $4 -b ../../data/ATAC-seq/potter2018/intersectRootsShoots_PeaksInBoth.bed > ../../data/output/$2/chromatin_coverage/${xpref}ShootRootIntersectOpenChrom.motifsmappedintersect.bed