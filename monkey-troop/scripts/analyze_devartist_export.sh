#!/usr/bin/env bash

# read local properties, eg.g BASE_PATH
. local.properties

 echo 'SANITY CHECK'
 echo ' HASHING'
 python3 code/analyze.py ${BASE_DIR}/hashing_results/ dev_artist check
 echo ' QUERY'
 python3 code/analyze.py ${BASE_DIR}/query_results/ dev_artist check
 echo ' RANDOM'
 python3 code/analyze.py ${BASE_DIR}/random_results/ dev_artist check


echo 'EXPORTING'
echo '==== HASHING ===='
python3 code/analyze.py ${BASE_DIR}/hashing_results/ dev_artist exportsql
echo '==== QUERY ===='
python3 code/analyze.py ${BASE_DIR}/query_results/ dev_artist exportsql
echo '==== RANDOM ===='
python3 code/analyze.py ${BASE_DIR}/random_results/ dev_artist exportsql
