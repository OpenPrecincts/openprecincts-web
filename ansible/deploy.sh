#!/bin/sh
set -e
export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES
# export AWS_DEFAULT_PROFILE=pgp

ansible-galaxy install -r requirements.yml
ansible-playbook openprecincts.yml -i inventory/ -l openprecincts_$1

