#!/usr/bin/env bash

set -euo pipefail
export LC_ALL=C
# export TMPDIR=/media/mrueda/4TB/tmp
# zip='/usr/bin/pigz -p 1'
declare -A collections=(["analyses"]="/Users/mferri/Desktop/B2RI_MongoDB_training/CINECA_synthetic_cohort_EUROPE_UK1/bff/analyses.json" ["biosamples"]="/Users/mferri/Desktop/B2RI_MongoDB_training/CINECA_synthetic_cohort_EUROPE_UK1/bff/biosamples.json" ["cohorts"]="/Users/mferri/Desktop/B2RI_MongoDB_training/CINECA_synthetic_cohort_EUROPE_UK1/bff/cohorts.json" ["diseases"]="/Users/mferri/Desktop/B2RI_MongoDB_training/CINECA_synthetic_cohort_EUROPE_UK1/bff/diseases.json" ["individuals"]="/Users/mferri/Desktop/B2RI_MongoDB_training/CINECA_synthetic_cohort_EUROPE_UK1/bff/individuals.json" ["runs"]="/Users/mferri/Desktop/B2RI_MongoDB_training/CINECA_synthetic_cohort_EUROPE_UK1/bff/runs.json" ["genomicVariations"]="/Users/mferri/Desktop/B2RI_MongoDB_training/CINECA_synthetic_cohort_EUROPE_UK1/bff/genomicVariationsVcf_subset50.json")


# Load the data into Mongo DB
for collection in "${!collections[@]}"
do
 echo "Loading collection...$collection"
  echo "COMMAND: mongoimport--jsonArray --uri "URI" --file ${collections[$collection]} --collection $collection"

done
echo "# Finished OK"