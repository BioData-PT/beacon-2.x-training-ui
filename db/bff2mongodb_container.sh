#!/usr/bin/env bash
#
#   Script that loads BFF data into Mongo DB
#
#   Last Modified: Oct/19/2021
#
#   Version 2.0.0
#
#   Copyright (C) 2021 Manuel Rueda (manuel.rueda@crg.eu)
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, see <https://www.gnu.org/licenses/>.
#
#   If this program helps you in your research, please cite.

set -euo pipefail
export LC_ALL=C
# export TMPDIR=/media/mrueda/4TB/tmp
# zip='/usr/bin/pigz -p 1'
mongoimport=mongoimport
mongodburi=mongodb://root:example@db-beacon:27017/beacon?authSource=admin
mongosh=mongosh
declare -A collections=(["analyses"]="data/analyses.json" ["biosamples"]="data/biosamples.json" ["cohorts"]="data/cohorts.json" ["diseases"]="data/diseases.json" ["individuals"]="data/individuals.json" ["runs"]="data/runs.json" ["genomicVariations"]="data/genomicVariationsVcf_subset50.json")

function usage {

    USAGE="""
    Usage: $0
    """
    echo "$USAGE"
    exit 1
}

# Check #arguments
if [ $# -ne 0 ]
 then
  usage
fi

# Load the data into Mongo DB
for collection in "${!collections[@]}"
do
 echo "Loading collection...$collection"
 echo "COMMAND: $mongoimport --jsonArray --uri "$mongodburi" --file ${collections[$collection]} --collection $collection"
 $mongoimport --jsonArray --uri "$mongodburi" --file ${collections[$collection]} --collection $collection || echo "Could not load <${collections[$collection]}> for <$collection>"
 echo "Indexing collection...$collection"
 $mongosh "$mongodburi" << EOF
db.$collection.createIndex( {"\$**":1}, { name: "$collection"} )
exit
EOF
done
# $zip -dc /home/mrueda/test_beacon/beacon_164371015506201/vcf/genomicVariationsVcf.json.gz | $mongoimport --jsonArray --uri "$mongodburi" --collection genomicVariations || echo "Could not load <beacon_164371015506201/vcf/genomicVariationsVcf.json.gz> for <genomicVariations>"
# $mongosh "$mongodburi"<<EOF
# db.genomicVariations.createIndex( {"\$**":1}, { name: "genomicVariations"} )
# exit
# EOF

# All done
echo "# Finished OK"