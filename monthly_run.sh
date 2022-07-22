#!/bin/bash
# A script that gets data from the APIs each month, packages it and puts it into the OCFL repo, then (optionally) syncs the OCFL repo with AWS Oni
# Written by Simon Kruik
# 2022-07-21
#

PROGRAM_NAME=$0

function usage {
	echo "usage: $PROGRAM_NAME [-w|--insitu] [-n|--ict] [-o|-ocfl_repo <location>] [-a|--aws_sync_script <location>] start_date end_date"
	echo ""
	echo "Environment Variables:"
	echo "python3_location=<filepath to your python3 installation> (defaults to executing which python3 to get filepath from PATH variable)"
	echo "api_file_location=<filepath to the insitu_api.py and eagleio_api.py scripts> (defaults to pwd)"
	
	exit 1
}

# Stage 0: Option Parsing/Handling:

options=$(getopt -l "insitu,ict,ocfl_repo:,aws_sync_script::" -- "wno:a::" "$@")
while [[ "$#" -gt 2 ]]
do
# echo "$#" # Testing the shift 
case $1 in
 -w|--insitu)
	echo "Getting the Insitu data from WA"
	;;
 -n|--ict)
	echo "Getting the ICT data from NSW"
	;;
 -o|--ocfl_repo)
	shift
	echo "OCFL Repo located at: ${1}"
	;;
 -a|--aws_sync_script)
	shift
	echo "AWS Sync Script located at: ${1}"
	;;
 --)
	shift
	break;;
esac
shift
done

# Stage 1: Pulling the data down
if [[ -z "${python3_location}" ]]; then
	PYTHON_PATH=`which python3`
else
	PYTHON_PATH="${python3_location}"
fi

echo "Running with ${PYTHON_PATH}"


if [[ -z "${api_file_location}" ]]; then
	API_PATH=`pwd`
else
	API_PATH="${api_file_location}"
fi

echo "Looking for API scripts in ${API_PATH}"


# Stage 2: Depositing the data in OCFL repo

# Stage 3: Synchronising the OCFL repo in AWS


# Giving help function
if [[ "$#" -eq 0 ]]; then
	usage
fi
