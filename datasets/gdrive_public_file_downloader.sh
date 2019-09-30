#!/usr/bin/env bash

# code based on comment: https://gist.github.com/iamtekeste/3cdfd0366ebfd2c0d805#gistcomment-2359248

function gdrive_download () {
  CONFIRM=$(wget \
  --quiet \
  --save-cookies /tmp/cookies.txt \
  --keep-session-cookies \
  --no-check-certificate \
  "https://docs.google.com/uc?export=download&id=$1" -O- | \
  sed -rn 's/.*confirm=([0-9A-Za-z_]+).*/\1\n/p') \

  wget \
  --load-cookies /tmp/cookies.txt \
  "https://docs.google.com/uc?export=download&confirm=$CONFIRM&id=$1" -O $2

  rm -rf /tmp/cookies.txt
}