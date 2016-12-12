#!/bin/bash
#this script executes the python script which loads information into reducedRow database
#meant to be run daily

flask-venv/bin/python loader.py auto 1

#array=( 3521 3524 3528 3532 3533 3922 4094 91 30 104 106 114 3647)
#for i in "${array[@]}"
#do
#    flask-venv/bin/python loader.py $i 2
#done
