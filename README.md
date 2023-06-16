# OVH Database Backup

Minimal script to trigger the dump of a [OVH Web Cloud Database](https://www.ovhcloud.com/en/web-cloud/databases/), then wait for its availability. This script does *NOT* work with a [Public Cloud Database](https://www.ovhcloud.com/en/public-cloud/databases/)).

This script is meant for usage as a Kubernetes `Job` triggered before deployment using Helm or Argo hooks.

## Config

You need :
- the name of the "service" (see picture below), as env var `BACKUP_SERVICE_NAME`
- the name of the database (see picture below), as env var `BACKUP_DATABASE_NAME`
- credentials : Application Key, Application Secret, Consumer Key (see paragraph below), as standard env vars `OVH_APPLICATION_KEY` / `OVH_APPLICATION_SECRET` / `OVH_CONSUMER_KEY`
- OVH Endpoint : defaults to `ovh-eu`
- LOG_LEVEL : defaults to `INFO`. Accepts Python standard levels (upper case). *Caution* : `DEBUG` will output public expirable URL of the backup, which is a sensitive information.

## Credentials

You need credentials with the following authorizations :
- `GET /hosting/privateDatabase/*/database/*/dump`
- `GET /hosting/privateDatabase/*/database/*/dump/*`
- `POST /hosting/privateDatabase/*/database/*/dump`

You can create an OVH app and credentials with those permissions using following URL (adapt for API endpoints other than `ovh-eu`): https://eu.api.ovh.com/createToken/?GET=/hosting/privateDatabase/*/database/*/dump&GET=/hosting/privateDatabase/*/database/*/dump/*&POST=/hosting/privateDatabase/*/database/*/dump

## Usage

#### Python
Tested with Python 3.9, 3.10 and 3.11

```bash
# optional venv
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
export BACKUP_SERVICE_NAME=... 
export BACKUP_DATABASE_NAME=... 
export OVH_APPLICATION_KEY=... 
export OVH_APPLICATION_SECRET=... 
export OVH_CONSUMER_KEY=...
python -m ovh_db_backup
```

#### Docker

```bash
docker run --rm \
 -e BACKUP_SERVICE_NAME=... \
 -e BACKUP_DATABASE_NAME=... \
 -e OVH_APPLICATION_KEY=... \
 -e OVH_APPLICATION_SECRET=... \ 
 -e OVH_CONSUMER_KEY=... \
 ghcr.io/illuin-tech/ovh-db-backup
```

#### Kubernetes

Example job (and secret holding env vars):
```kubernetes
---
apiVersion: v1
kind: Secret
metadata:
  name: ovh-db-backup
type: Opaque
stringData:
  BACKUP_SERVICE_NAME: ...
  BACKUP_DATABASE_NAME: ...
  OVH_APPLICATION_KEY: ...
  OVH_APPLICATION_SECRET: ...
  OVH_CONSUMER_KEY: ...
---
apiVersion: batch/v1
kind: Job
metadata:
  generateName: ovh-db-backup-
spec:
  ttlSecondsAfterFinished: 86400
  template:
    spec:
      containers:
        - name: ovh-db-backup
          image: ghcr.io/illuin-tech/ovh-db-backup
          envFrom:
            - secretRef:
                name: ovh-db-backup
      restartPolicy: Never
```
