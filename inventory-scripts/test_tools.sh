#!/bin/bash

# Script to test out and time the various python shell scripts in this directory

echo "The whole command line: $@"
tool_to_test=$1

function exists_in_list() {
    LIST=$1
    DELIMITER=$2
    VALUE=$3
    LIST_WHITESPACES=$(echo $LIST | tr "$DELIMITER" " ")
    for x in $LIST_WHITESPACES; do
        if [ "$x" = "$VALUE" ]; then
            return 0
        fi
    done
    return 1
}

scripts_to_not_test="Inventory_Modules.py recovery_stack_ids.py lock_down_stack_sets_role.py ArgumentsClass.py \
account_class.py ALZ_CheckAccount.py CT_CheckAccount.py delete_bucket_objects.py enable_drift_detection.py \
find_my_LZ_versions.py move_stack_instances.py RunOnMultiAccounts.py UpdateRoleToMemberAccounts.py vpc_modules.py \
recover_stack_ids.py setup.py decorators.py read_stackset_results.py"

scripts_that_require_response="enable_drift_detection_stacksets.py"

declare -a arrScripts

#if [[ -n "$tool_to_test" && "$tool_to_test" = "all" ]]; then
#  arrScripts=("$tool_to_test")
if [[ -n "$tool_to_test" && "$tool_to_test" != "all" ]]; then
  shift
  test_params=$@
  echo "Running $tool_to_test with params: $test_params"
  output_file="test_output_$tool_to_test.txt"
  echo $(date) > "$output_file"
  echo python "$tool_to_test" "$test_params" >> "$output_file"
#  $(python "$tool_to_test" "$test_params" >> "$output_file" ; echo $? >> "$output_file" ; echo $(date) >> "$output_file" ) &
  $(python "$tool_to_test" $test_params >> "$output_file" ; echo $? >> "$output_file" ; echo $(date) >> "$output_file" ) &
else
  shift
  test_params=$@
  echo "Running $tool_to_test with params: $test_params"
  for file in *.py
  do
    if exists_in_list "$scripts_to_not_test" " " "$file" ; then
        echo "Not trying to run $file"
    elif exists_in_list "$scripts_that_require_response" " " "$file"]; then
        echo "Skipping because $file needs specific input"
    else
      echo "Will test run $file"
      arrScripts=("${arrScripts[@]}" "$file")
    fi
  done
fi

summary_file="test_output_summary.$(date).txt"
for item in "${arrScripts[@]}"
do
  echo "Running $item"
  output_file="test_output_$item.txt"
  echo $(date) > "$output_file"
  $(echo "Script: $item Params: $test_params" >> $output_file ; python "$item" $test_params >> "$output_file" ; echo $? >> "$output_file" ; echo $(date) >> "$output_file" ) &
  $(begin_date=$(date) ; echo -n $item $test_params >> "$summary_file"; echo -n " | " >> "$summary_file"; echo -n $begin_date >> "$summary_file"; echo -n " | " >> "$summary_file"; echo $(date) >> "$summary_file") &
done
