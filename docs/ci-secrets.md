# CI/CD Secrets Checklist (Dev and Prod)

This project supports two authentication modes for Google Cloud in GitHub Actions:

- Service Account JSON (simple)
- Workload Identity Federation (recommended)

The deploy workflows auto‑detect which mode you use. Configure exactly one per environment.

## Dev environment (deploy-dev.yml)

Required (choose ONE auth path):

- Service Account JSON
  - : contents of the service account JSON key

- OR Workload Identity Federation
  - : full provider resource (e.g., )
  - : email of the service account (e.g., )

Non‑auth secrets:

-  (e.g., )
-  (e.g., )
- 
- 
-  (e.g., )

Defaults in workflow:

- Region: 
- Artifact Registry repo: 
- Cloud Run service: 

## Prod environment (deploy.yml)

Required (choose ONE auth path):

- Service Account JSON
  - 

- OR Workload Identity Federation
  - 
  - 

Non‑auth secrets:

- 
-  (e.g., )
-  (Artifact Registry repo name)
-  (service name)
- 
- , , 
- 
- 
-  = 

## Quick set via gh CLI (examples)



## Troubleshooting

- Error: 
  - Ensure you set either the SA JSON secret OR both WIF secrets for the environment.
  - Forked PRs do not inherit secrets; use a protected branch or run in your repo.

- Error: 
  - Confirm service account has  and  and can access the Cloud SQL instance.

