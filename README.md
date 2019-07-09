# sae-postgres

## Getting Started

### Preparing Postgres

```
cd terraform/workspaces/projectdb

cp terraform.tfvars.example terraform.tfvars

echo "hostRootPath=\"`pwd`/_tmp\"" >> terraform.tfvars

terraform init

terraform apply
```

### Executing Test Suite

```
. terraform/workspaces/projectdb/_tmp/env

docker build --tag sae-postgres-tests .

docker run -ti --rm \
    --net=projectdb_vnet \
    -e PGHOST -e PGPORT -e PGDATABASE -e PGUSER -e PGPASSWORD \
    -v `pwd`:/work -w /work \
    sae-postgres-tests python setup.py test
```
