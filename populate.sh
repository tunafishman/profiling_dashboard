#!/bin/bash
array=( 91 104 106 3521 3524 3528)
for i in "${array[@]}"
do
    flask/bin/python loader.py $i 1 
done
