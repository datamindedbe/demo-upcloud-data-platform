#!/bin/bash

aws s3 cp conditions.csv s3://dp-data-bucket/raw/ --profile upcloud-data
aws s3 cp encounters.csv s3://dp-data-bucket/raw/ --profile upcloud-data
aws s3 cp medications.csv s3://dp-data-bucket/raw/ --profile upcloud-data
aws s3 cp patients.csv s3://dp-data-bucket/raw/ --profile upcloud-data
