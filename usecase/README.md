# Clone both repos
git clone https://github.com/synthetichealth/synthea.git
git clone https://github.com/synthetichealth/synthea-international.git

# Copy Belgium modules into Synthea
cp -r synthea-international/nl/* synthea/


# Generate 500 Belgian patients as CSV
./run_synthea -p 10000 "Noord-holland" Amsterdam

Output lands in output/csv/ with Belgian addresses, names, and postal codes.

The key tables you'll use for the demo:
- patients.csv — full PII (name, birthdate, address, Belgian identifiers)
- conditions.csv — diagnoses linked to patient ID
- medications.csv — prescriptions
- encounters.csv — visits and appointments