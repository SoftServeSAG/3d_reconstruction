#!/usr/bin/env bash

. ./gdrive_public_file_downloader.sh  --source-only  # importing function to use

DATASET_NAME=published_test_frog
ARCHIVE_NAME="/tmp/${DATASET_NAME}.zip"
#https://drive.google.com/open?id=1q3QfRB_D2_pWJIF0BFFHqbqYhk9ykgTA
DATASET_GDRIVE_ID=1q3QfRB_D2_pWJIF0BFFHqbqYhk9ykgTA

echo "Downloading dataset [${DATASET_NAME}] as [${ARCHIVE_NAME}]"
gdrive_download ${DATASET_GDRIVE_ID} ${ARCHIVE_NAME}

echo "Unpacking..."
unzip -q ${ARCHIVE_NAME} -d `pwd`

echo "Deleting temps"
rm ${ARCHIVE_NAME}

echo "Result: "
ls -l $DATASET_NAME

