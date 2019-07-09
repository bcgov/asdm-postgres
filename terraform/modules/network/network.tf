resource "docker_network" "private_network" {
  name = "${var.workspace}_vnet"
}

output "private_network_name" {
  value = "${docker_network.private_network.name}"
}

