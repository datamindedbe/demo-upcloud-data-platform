# Use the patient data

## Generate Synthea data

### Clone the repositories
git clone https://github.com/synthetichealth/synthea.git
git clone https://github.com/synthetichealth/synthea-international.git

### Copy Netherlands modules into Synthea
cp -r synthea-international/nl/* synthea/

### Generate 10000 Netherlands patients as CSV
./run_synthea -p 10000 "Noord-holland" Amsterdam

Output lands in output/csv/ with Netherlands addresses, names, and postal codes.

The key tables you'll use for the demo:
- patients.csv — full PII (name, birthdate, address, Belgian identifiers)
- conditions.csv — diagnoses linked to patient ID
- medications.csv — prescriptions
- encounters.csv — visits and appointments

### Upload the csv files to s3

Make sure you created the upcloud-data profiles in your ~/.aws/config file.
```
[profile upcloud-data]
region=europe-1
services=upcloud-data

[services upcloud-data]
s3 = 
  endpoint_url = https://<TODO>.upcloudobjects.com
iam =
  endpoint_url = https://<TODO>.upcloudobjects.com:4443/iam
sts =
  endpoint_url = https://<TODO>.upcloudobjects.com:4443/sts

```

Use the upload.sh script to upload the files to s3.

## Use the data

### Ingest step

Simple python script that uses pyiceberg to ingest the csv files into Iceberg tables.
It uses Lakekeeper as Rest catalog to manage the metadata.

### Transform step

Use trino to query and transform the Iceberg tables.