
module "network_private" {
  source = "../../modules/network"
  workspace = "${var.workspace}"  
}

module "projectdb_postgres" {
  source  = "../../modules/postgres"
  hostRootPath = "${var.hostRootPath}"
  workspace = "${var.workspace}"
  externalPort = "4000"
  network = "${module.network_private.private_network_name}"
#  upgrade_support_for_gssapi_authentication = "true"
#  krb_realm = "AD.LOCAL"
}

output "README" {
  value = "${module.projectdb_postgres.readme}"
}