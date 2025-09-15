locals {
  # For more details look here: https://upcloud.com/docs/products/managed-object-storage/availability/
  default_region_zone_mapping = {
    "europe-1" = "fi-hel1"
    "europe-2" = "de-fra1"
    "europe-3" = "se-sto1"
  }
  zone = local.default_region_zone_mapping[var.region]
}