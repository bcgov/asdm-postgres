output "readme" {
    value = <<TEXT

  export PGHOST=${var.workspace}_postgres
  export PGUSER=padmin
  export PGDATABASE=postgres
  export PGPASSWORD=${random_string.postgresSuperPassword.result}

  docker run -ti --rm \
    --net=${var.network} \
    -e PGHOST -e PGUSER -e PGDATABASE -e PGPASSWORD \
    postgres${var.images["postgres"]} psql

    TEXT

}

resource "local_file" "env" {
    content     = <<TEXT
PGHOST=${var.workspace}_postgres
PGPORT=${var.externalPort}
PGUSER=padmin
PGDATABASE=postgres
PGPASSWORD=${random_string.postgresSuperPassword.result}
    TEXT
    filename = "${var.hostRootPath}/env"
}
