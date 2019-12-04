# sae-postgres

## Getting Started

### Running Client

```
export PATH=$PATH:.
pip install -r requirements.txt

export LOG_LEVEL=INFO
export PGDATABASE=postgres
export PGHOST=postgres
export PGPORT=5432
export PGUSER=postgres
export PGPASSWORD=postgres

cli script --script list_databases

cli grants --user test_user --out grants.log

```

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
    -e LOG_LEVEL -e PGHOST -e PGPORT -e PGDATABASE -e PGUSER -e PGPASSWORD \
    -v `pwd`:/work -w /work \
    sae-postgres-tests python setup.py test
```
