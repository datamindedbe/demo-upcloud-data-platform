# Troubleshooting zitadel configuration

If you encounter issues connecting to Zitadel using the cli/terraform.
The following steps can be useful:
- https://<HOST>/.well-known/openid-configuration (check whether it is https or http)
    - if it is http, your client should connect using insecure = true
- check whether both https and grpc traffic works by using:
    - grpcurl <HOST>:443 zitadel.admin.v1.AdminService/Healthz
    - curl https://<HOST>:443/admin/v1/healthz
    - both these calls should return an {}