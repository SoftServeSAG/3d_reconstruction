#!/usr/bin/env bash

. ./gdrive_public_file_downloader.sh  --source-only  # importing function to use

DATASET_NAME=published_frog_testdata
ARCHIVE_NAME="/tmp/${DATASET_NAME}.zip"
# https://drive.google.com/open?id=1MFpJGMrDTFNN274GbrhYsA3FRvO0nUDV
DATASET_GDRIVE_ID=1MFpJGMrDTFNN274GbrhYsA3FRvO0nUDV

echo "Downloading dataset [${DATASET_NAME}] as [${ARCHIVE_NAME}]"
gdrive_download ${DATASET_GDRIVE_ID} ${ARCHIVE_NAME}

echo "Unpacking..."
unizip -z ${ARCHIVE_NAME} -d `pwd`

echo "Deleting temps:"
rm ${ARCHIVE_NAME}

echo "Result: "
ls -l $DATASET_NAME

