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