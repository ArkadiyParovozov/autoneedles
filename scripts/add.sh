#!/bin/bash

# set gcloud path
gcloud=${GCLOUD_HOME:-gcloud}

# get first argument as gcloud configuration name
gcloud_configs=$1

# create gcloud configuration and authorize with google account
$gcloud config configurations create "$gcloud_configs" && $gcloud auth login
