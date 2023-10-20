#!/bin/bash
# A script that gets data from the APIs each month, packages it and puts it into the OCFL repo, then (optionally) syncs the OCFL repo with AWS Oni
# Written by Simon Kruik
# 2022-07-21
#

# For using in bash, get start and dates with `date +%Y-%m | sed "s/-/ /g"` and `date +%Y-%m -d 'next month' | sed "s/-/ /g"`

PROGRAM_NAME=$0
function usage {
	echo "usage: $PROGRAM_NAME [-w|--insitu] [-n|--ict] [[-d|--deposit_script <location>] [-o|--ocfl_repo <location>]] [-a|--aws_sync_script <location>] start_date end_date"
	echo "start_date and end_date should be in format yyyy-mm (ISO 8601), e.g. 2022-02"
	echo ""
	echo "Environment Variables:"
	echo "python3_location=<filepath to your python3 installation> (defaults to executing which python3 to get filepath from PATH variable)"
	echo "api_file_location=<filepath to the repo containing insitu_api.py and eagleio_api.py scripts> (defaults to pwd)"


	exit 1
}

# Stage 0: Option Parsing/Handling:

options=$(getopt -l "insitu,ict,ocfl_repo:,deposit_script:,aws_sync_script::" -- "wno:d:a::" "$@")
while [[ "$#" -gt 2 ]]
do
# echo "$#" # Testing the shift 
case $1 in
 -w|--insitu)
	INSITU=true
	echo "Getting the Insitu data from WA"
	;;
 -n|--ict)
	ICT=true
	echo "Getting the ICT data from NSW"
	;;
 -o|--ocfl_repo)
	shift
	OCFL_REPO=$1
	echo "OCFL Repo located at: ${1}"
	;;
 -d|--deposit_script)
	shift
	DEPOSIT_SCRIPT=$1
	echo "OCFL Deposit script located at: ${DEPOSIT_SCRIPT}"
	;;
 -a|--aws_sync_script)
	shift
	AWS_SCRIPT=$1
	echo "AWS Sync Script located at: ${1}"
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
if [[ -v ICT ]]; then
	echo "Clearing all files in ${API_PATH}/api_calls/ict_data/"
	rm -f ${API_PATH}/api_calls/ict_data/*
	echo "Running: $PYTHON_PATH $API_PATH/api_calls/eagleio_data.py $START_DATE $END_DATE"
	$PYTHON_PATH $API_PATH/api_calls/eagleio_data.py $START_DATE $END_DATE
fi

if [[ -v INSITU ]]; then
	echo "Clearing all files in ${API_PATH}/api_calls/insitu_data/"
	rm -f ${API_PATH}/api_calls/insitu_data/*
	echo "Running: $PYTHON_PATH $API_PATH/api_calls/insitu_data.py $START_DATE $END_DATE"
	$PYTHON_PATH $API_PATH/api_calls/insitu_data.py $START_DATE $END_DATE
fi


# Stage 1.5: Packaging the data into RO-Crates
if [[ -v ICT ]] || [[ -v INSITU ]]; then
	echo "Clearing all files in ${API_PATH}/sensor-data/"
	rm -rf ${API_PATH}/sensor-data/*
	cd ${API_PATH}
fi

if [[ -v ICT ]]; then

	echo "Running: $PYTHON_PATH $API_PATH/open_data.py --api --folder $API_PATH/api_calls/ict_data/"
	$PYTHON_PATH $API_PATH/open_data.py --api --folder $API_PATH/api_calls/ict_data/

fi

if [[ -v INSITU ]]; then

	echo "Running: $PYTHON_PATH $API_PATH/open_data.py --api --folder $API_PATH/api_calls/insitu_data/"
	$PYTHON_PATH $API_PATH/open_data.py --api --folder $API_PATH/api_calls/insitu_data/

fi


# Stage 2: Depositing the data in OCFL repo
if [[ -v DEPOSIT_SCRIPT ]] && [[ -v OCFL_REPO ]]; then
	echo "Running: node $DEPOSIT_SCRIPT --repo $OCFL_REPO --name seafood $API_PATH/sensor-data/*" 
	node $DEPOSIT_SCRIPT --repo $OCFL_REPO --name seafood $API_PATH/sensor-data/*
fi

# node /home/skruik/src/ocfl-demos/ro-crate-deposit.js --repo /home/skruik/src/seafood-collection-v1-2-1/oni-express/ocfl --name seafood out_*

# Stage 3: Synchronising the OCFL repo in AWS

if [[ -v AWS_SCRIPT ]]; then
	echo "Running: $AWS_SCRIPT"
	cd `dirname $AWS_SCRIPT`
	source $AWS_SCRIPT
fi

# Stage 4: Re-index the site
	echo "Re-indexing site"
	curl https://salinity.research.uts.edu.au/config/index/run --header "Authorization: Bearer theseafoodtoken"

# Giving help function
if [[ "$#" -eq 0 ]]; then
	usage
fi

exit 0
