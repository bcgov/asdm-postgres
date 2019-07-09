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
PGHOST=projectdb_postgres
PGDATABASE=postgres
PGUSER=padmin
PGPASSWORD=your_database_secret_password

docker build --tag sae-postgres-tests .

docker run -ti --rm \
    --net=projectdb_vnet \
    -e PGHOST -e PGUSER -e PGDATABASE -e PGPASSWORD \
    -v `pwd`:/work -w /work \
    sae-postgres-tests python setup.py test

```
