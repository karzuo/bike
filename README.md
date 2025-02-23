
2.
Requires permissions on both external table and the GCS. Use BigLaek if possible.

Each of the following predefined Identity and Access Management roles includes this permission:

BigQuery Data Editor (roles/bigquery.dataEditor)
BigQuery Data Owner (roles/bigquery.dataOwner)
BigQuery Admin (roles/bigquery.admin)
You also need the following permissions to access the Cloud Storage bucket that contains your data:

storage.buckets.get
storage.objects.get
storage.objects.list (required if you are using a URI wildcard)
The Cloud Storage Storage Admin (roles/storage.admin) predefined Identity and Access Management role includes these permissions.

If you are not a principal in any of these roles, ask your administrator to grant you access or to create the external table for you.

https://cloud.google.com/bigquery/docs/external-data-cloud-storage?utm_source=google&utm_medium=cpc&utm_campaign=japac-SG-all-en-dr-SKWS-all-all-trial-DSA-dr-1710102&utm_content=text-ad-none-none-DEV_c-CRE_645025797114-ADGP_Hybrid%20%7C%20SKWS%20-%20BRO%20%7C%20DSA%20-Data%20Analytics-BigQuery-KWID_39700075148142364-dsa-1958795857833&userloc_9062499-network_g&utm_term=KW_&gad_source=1&gclid=CjwKCAiAiOa9BhBqEiwABCdG8-c0hWVDSGi4wrqvl5n4RFN1QXH-xbiTQvrYl2KrhnPdfA-vON457hoCtaoQAvD_BwE&gclsrc=aw.ds

* create a dataset in same location as the gcs bucket if not yet created.
* big lake not created due to costs, but is just one small step

* set google credentials env var
