#!/bin/bash
array=( 3521 3524 3528 3532 3533 3922 91 30 104 106 114 3647)
for i in "${array[@]}"
do
    flask-venv/bin/python loader.py $i 4
done
