#!/bin/bash

task_counter=0
declare -a files=(
    "prepro_00_create_html_manifest.py"
    "prepro_00_create_thread2formulasTSV.py"
    "prepro_00_modify_formula_representation.py"
    "prepro_00_create_initial_parsers.py"
    "prepro_01_create_raw_maps_from_parsers.py"
    "prepro_02_modify_raw_map_of_comments.py"
    "prepro_03_create_more_maps.py"
    "prepro_04_create_question2title_latex2slt.py"
)
task_total="${#files[@]}"

error_exit() {
    echo "... [Task $1/$2 ERROR] $3 aborted."
    exit 1
}

for file in ${files[@]}; do
    task_counter=$((task_counter+1))
    echo
    echo
    echo "... [Task ${task_counter}/${task_total}] Running $file ..."
    python ${file} || error_exit ${task_counter} ${task_total} ${file}
    echo "... [Task ${task_counter}/${task_total}] Success!"
done

