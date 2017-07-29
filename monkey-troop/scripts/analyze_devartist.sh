#!/usr/bin/env bash

# read local properties, eg.g BASE_PATH
. local.properties

 echo 'SANITY CHECK'
 echo ' HASHING'
 python3 code/analyze.py ${BASE_DIR}/hashing_results/ dev_artist check
 echo ' NOTHING'
 python3 code/analyze.py ${BASE_DIR}/nothing_results/ dev_artist check
 echo ' QUERY'
 python3 code/analyze.py ${BASE_DIR}/query_results/ dev_artist check
 echo ' RANDOM'
 python3 code/analyze.py ${BASE_DIR}/random_results/ dev_artist check


echo 'SUMMARY'
echo '==== HASHING ===='
python3 code/analyze.py ${BASE_DIR}/hashing_results/ dev_artist summary
echo '==== NOTHING ===='
python3 code/analyze.py ${BASE_DIR}/nothing_results/ dev_artist summary
echo '==== QUERY ===='
python3 code/analyze.py ${BASE_DIR}/query_results/ dev_artist summary
echo '==== RANDOM ===='
python3 code/analyze.py ${BASE_DIR}/random_results/ dev_artist summary

# echo 'FAILS'
# echo '\t HASHING'
# python3 code/analyze.py ${BASE_DIR}/hashing_results/ dev_artist fails
# echo '\t NOTHING'
# python3 code/analyze.py ${BASE_DIR}/nothing_results/ dev_artist fails
# echo '\t QUERY'
# python3 code/analyze.py ${BASE_DIR}/query_results/ dev_artist fails
# echo '\t RANDOM'
# python3 code/analyze.py ${BASE_DIR}/random_results/ dev_artist fails
