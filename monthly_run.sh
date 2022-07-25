#!/bin/bash
# A script that gets data from the APIs each month, packages it and puts it into the OCFL repo, then (optionally) syncs the OCFL repo with AWS Oni
# Written by Simon Kruik
# 2022-07-21
#

# For using in bash, get start and dates with `date +%Y-%m | sed "s/-/ /g"` and `date +%Y-%m -d 'next month' | sed "s/-/ /g"`

PROGRAM_NAME=$0
function usage {
	echo "usage: $PROGRAM_NAME [-w|--insitu] [-n|--ict] [-o|-ocfl_repo <location>] [-a|--aws_sync_script <location>] start_date end_date"
	echo "start_date and end_date should be in format yyyy-mm (ISO 8601), e.g. 2022-02"
	echo ""
	echo "Environment Variables:"
	echo "python3_location=<filepath to your python3 installation> (defaults to executing which python3 to get filepath from PATH variable)"
	echo "api_file_location=<filepath to the repo containing insitu_api.py and eagleio_api.py scripts> (defaults to pwd)"


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
	INSITU=true
	;;
 -n|--ict)
	echo "Getting the ICT data from NSW"
	ICT=true
	;;
 -o|--ocfl_repo)
	shift
	echo "OCFL Repo located at: ${1}"
	OCFL_REPO=$1
	;;
 -a|--aws_sync_script)
	shift
	echo "AWS Sync Script located at: ${1}"
	AWS_SCRIPT=$1
	;;
 --)
	shift
	break;;
esac
shift
done

START_DATE=$1
END_DATE=$2

# Stage 1: Pulling the data down
if [[ -z "${python3_location}" ]]; then
	PYTHON_PATH=`which python3`
else
	PYTHON_PATH="${python3_location}"
fi

echo "Looking for python3 at ${PYTHON_PATH}"


if [[ -z "${api_file_location}" ]]; then
	API_PATH=`pwd`
else
	API_PATH="${api_file_location}"
fi

echo "Looking for API scripts in ${API_PATH}"

if [[ $ICT -eq true ]]; then

	echo "Clearing all files in ${API_PATH}/api_calls/ict_data/"
	rm -f ${API_PATH}/api_calls/ict_data/*
	$PYTHON_PATH $API_PATH/api_calls/eagleio_data.py $START_DATE $END_DATE

fi

if [[ $INSITU -eq true ]]; then

	echo "Clearing all files in ${API_PATH}/api_calls/insitu_data/"
	rm -f ${API_PATH}/api_calls/insitu_data/*
	$PYTHON_PATH $API_PATH/api_calls/insitu_data.py $START_DATE $END_DATE

fi


# Stage 1.5: Packaging the data into RO-Crates

echo "Clearing all files in ${API_PATH}/sensor-data/"
rm -f ${API_PATH}/sensor-data/*
cd ${API_PATH}

if [[ $ICT -eq true ]]; then

	$PYTHON_PATH $API_PATH/open_data.py --api --folder $API_PATH/api_calls/ict_data/

fi

if [[ $INSITU -eq true ]]; then

	$PYTHON_PATH $API_PATH/open_data.py --api --folder $API_PATH/api_calls/insitu_data/

fi

# Stage 2: Depositing the data in OCFL repo

# Stage 3: Synchronising the OCFL repo in AWS


# Giving help function
if [[ "$#" -eq 0 ]]; then
	usage
fi

exit 0
