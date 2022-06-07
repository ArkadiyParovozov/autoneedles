#!/bin/bash

# set gcloud path
gcloud=${GCLOUD_HOME:-gcloud}

# make gcloud configurations
gcloud_configs=()
IFS=$'\n' configs_out=($($gcloud config configurations list))

no_configs=('NAME' 'default')
for index in "${!configs_out[@]}"
  do
      IFS=$' ' config_details=(${configs_out[index]})
      config=${config_details[0]}
      if [[ ! ${no_configs[*]} =~ $config ]]
        then
          gcloud_configs=("${gcloud_configs[@]}" "$config")
      fi
  done

if ((${#gcloud_configs[@]}))
  then
    printf '\n gcloud configurations: %s\n' "${gcloud_configs[*]}"
  else
    printf '\n there is no gcloud configuration\n'
fi

# create logs directory
mkdir -p logs

# remove HOME directory
for config in "${gcloud_configs[@]}"
  do
    printf '\n gcloud configuration %s: cleanup started\n' "${config}"
    CLOUDSDK_ACTIVE_CONFIG_NAME="${config}" \
    "${gcloud}" cloud-shell ssh --authorize-session \
    --command="sudo rm -rf \$HOME"
    printf '\n gcloud configuration %s: cleanup finished\n' "${config}"
  done





