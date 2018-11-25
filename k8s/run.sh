#!/bin/sh

kubectl apply -f .


kubectl create configmap nginx-conf --from-file=configs/nginx.conf
