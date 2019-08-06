output "readme" {
    value = <<TEXT

  export PGHOST=${var.workspace}_postgres
  export PGUSER=padmin
  export PGDATABASE=postgres
  export PGPASSWORD=${random_string.postgresSuperPassword.result}

  docker run -ti --rm \
    --net=${var.network} \
    -e LOG_LEVEL -e PGHOST -e PGUSER -e PGDATABASE -e PGPASSWORD \
    postgres${var.images["postgres"]} psql

    TEXT

}

resource "local_file" "env" {
    content     = <<TEXT
export LOG_LEVEL=DEBUG
export PGHOST=${var.workspace}_postgres
export PGPORT=5432
export PGDATABASE=postgres
export PGUSER=padmin
export PGPASSWORD=${random_string.postgresSuperPassword.result}
    TEXT
    filename = "${var.hostRootPath}/env"
}
