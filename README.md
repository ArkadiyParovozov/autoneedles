### auto-attack with needles via gshells in parallel
- https://shell.cloud.google.com
- https://github.com/Arriven/db1000n

### how to set up
- install gcloud cli

  https://cloud.google.com/sdk/docs/install
- create google accounts

  https://accounts.google.com/signup/v2/webcreateaccount?biz=false&flowEntry=SignUp
- create gcloud configurations and authorize with google accounts

  ``gcloud config configurations create {config_name} && gcloud auth login``

### how to use
  ``python gshell_attack.py --attack_time=18000 --shells_num=8 --needles_args="-log-format console"``
  
  ``python gshell_attack.py --attack_time=18000 --shells_num=8``
  
  ``python gshell_attack.py --shells_num=8``

  ```python gshell_attack.py --help
     usage: gshell_attack.py [-h] [--attack_time ATTACK_TIME] [--shells_num SHELLS_NUM] [--needles_args NEEDLES_ARGS]

     attack with needles via gshells

     optional arguments:
      -h, --help                    show this help message and exit
      --attack_time ATTACK_TIME     minimum attack time in seconds (default: 1)
      --shells_num SHELLS_NUM       a number of gshells (default: 4)
      --needles_args NEEDLES_ARGS   db1000n arguments (default: )
  ```