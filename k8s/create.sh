#!/bin/bash

# Get the Personal Access Token from https://gitlab.com/profile/personal_access_tokens
DOCKER_PASSWORD="$1"

if [[ -n $DOCKER_PASSWORD ]]; then
  kubectl create secret docker-registry registry.gitlab.com --docker-server=https://registry.gitlab.com --docker-username=docker-readonly --docker-password="$DOCKER_PASSWORD" --docker-email=pablo@anche.no
else
	echo "Skipping docker secret. You need to specify it as a parameter"
fi
kubectl create configmap nginx-libreborme --from-file=configs/libreborme.conf
