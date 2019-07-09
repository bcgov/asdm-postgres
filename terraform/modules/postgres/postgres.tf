
data "docker_registry_image" "postgres" {
  name = "postgres${var.images["postgres"]}"
}

resource "docker_image" "postgres" {
  name          = "${data.docker_registry_image.postgres.name}"
  pull_triggers = ["${data.docker_registry_image.postgres.sha256_digest}"]
  keep_locally  = true
}

resource "docker_container" "postgres" {
  image = "${docker_image.postgres.latest}"
  name = "${var.workspace}_postgres"
  restart = "on-failure"
  command = [
    "-c",
    "config_file=/etc/postgresql/postgresql.conf"
  ]
  volumes = { 
    host_path = "${var.hostRootPath}/data/${var.workspace}_postgres"
    container_path = "/var/lib/postgresql/data"
  }
  volumes = { 
    host_path = "${var.hostRootPath}/config/${var.workspace}_postgres"
    container_path = "/etc/postgresql"
  }
  volumes = {
    host_path = "/etc/passwd"
    container_path = "/etc/passwd"
    read_only = true
  }
  env = [
      "POSTGRES_USER=padmin",
      "POSTGRES_PASSWORD=${random_string.postgresSuperPassword.result}"
  ]
  ports = [{ 
    internal = 5432
    external = "${var.externalPort}"
  }]

  networks_advanced = { name = "${var.network}" }

  healthcheck = {
    test = ["CMD-SHELL", "pg_isready -U padmin"]
    interval = "5s"
    timeout = "5s"
    start_period = "5s"
    retries = 20
  }

  labels = {
    CUSTOM_CONFIG_1 = "${local_file.pg_hba.id}"
    CUSTOM_CONFIG_2 = "${local_file.postgresql_conf.id}"
  }
}

data "template_file" "postgres_script" {
  template = "${file("${path.module}/scripts/psql.tpl")}"
  vars = {
     APP_DATABASE = "${var.workspace}",
     POSTGRES_APP_USERNAME = "${var.postgres["username"]}",
     POSTGRES_APP_PASSWORD = "${random_string.postgresAppPassword.result}"
  }
}

resource "local_file" "postgres_script" {
    content = "${data.template_file.postgres_script.rendered}"
    filename = "${var.hostRootPath}/${var.workspace}_postgres_script.psql"
}

resource "null_resource" "postgres_first_time_install" {
  provisioner "local-exec" {
    command = "${path.module}/scripts/wait-for-healthy.sh ${var.workspace}_postgres"
  }

  provisioner "local-exec" {
    environment = {
      SCRIPT_PATH = "${var.hostRootPath}"
      POSTGRES_HOST = "${var.workspace}_postgres"
      POSTGRES_USER = "padmin"
      POSTGRES_PASSWORD = "${random_string.postgresSuperPassword.result}"
    }
    command = "docker run --net=${var.network} -v $SCRIPT_PATH:/work postgres:9.6.9 psql postgresql://$POSTGRES_USER:$POSTGRES_PASSWORD@$POSTGRES_HOST -f /work/${var.workspace}_postgres_script.psql"
  }

  depends_on = ["docker_container.postgres"]
}

output "postgres_first_time_install_complete" {
  value = "${null_resource.postgres_first_time_install.id}"
}





// upgrade pg_hba.conf if necessary

data "template_file" "pg_hba" {
  template = "${file("${path.module}/scripts/pg_hba.conf.tpl")}"
  vars = {
     ADMIN_USER = "padmin"
     HOST_RULE = "${var.upgrade_support_for_gssapi_authentication ? "host all all 0.0.0.0/0 gss include_realm=0 krb_realm=${var.krb_realm}":"host all all all md5"}"
  }
}

resource "local_file" "pg_hba" {
  content = "${data.template_file.pg_hba.rendered}"
  filename = "${var.hostRootPath}/config/${var.workspace}_postgres/pg_hba.conf"
}



// upgrade postgresql.conf if necessary

data "template_file" "postgresql_conf" {
  template = "${file("${path.module}/scripts/postgresql.conf.tpl")}"
  vars = {
  }
}

resource "local_file" "postgresql_conf" {
  content = "${data.template_file.postgresql_conf.rendered}"
  filename = "${var.hostRootPath}/config/${var.workspace}_postgres/postgresql.conf"
}
