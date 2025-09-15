resource "aws_s3_bucket" "state" {
  bucket = "dp-stack-tf-state-upcloud"
}

# resource "upcloud_managed_object_storage" "this" {
#   name              = "dp-stack-tf-state-upcloud"
#   region            = "europe-1"
#   configured_status = "started"

#   network {
#     family = "IPv4"
#     name   = "example-private-net"
#     type   = "public"
#   }
# }
