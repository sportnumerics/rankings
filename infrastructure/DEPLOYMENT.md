# Deployment Overview

This repo deploys via GitHub Actions. There are separate workflows for backend, frontend, and infrastructure. All production deploys assume the `rankings-deployment-role-prod` IAM role (OIDC via GitHub Actions).

## Workflows

### Backend (production)
- **Workflow:** `.github/workflows/deploy-backend.yml`
- **Trigger:** push to `main` with `backend/**` changes
- **Role:** `arn:aws:iam::265978616089:role/rankings-deployment-role-prod`
- **What it does:**
  - Runs `backend/deploy.sh prod` (builds + pushes image, updates ECS)
  - Triggers ECS task run via `backend/run.sh prod`

### Frontend (production)
- **Workflow:** `.github/workflows/deploy-frontend.yml`
- **Trigger:** push to `main` with `frontend/**` changes
- **Role:** `arn:aws:iam::265978616089:role/rankings-deployment-role-prod`
- **What it does:**
  - Runs `frontend/deploy.sh prod` (builds Next.js, uploads to S3, invalidates CloudFront)

### Infrastructure (production)
- **Workflow:** `.github/workflows/deploy-infra.yml`
- **Trigger:** push to `main` with `infrastructure/**` changes
- **Role:** `arn:aws:iam::265978616089:role/rankings-deployment-role-prod`
- **What it does:**
  - Runs `infrastructure/deploy.sh prod` (Terraform apply)

### PR Preview (dev)
- **Workflow:** `.github/workflows/deploy-pr-preview.yml`
- **Trigger:** PRs touching `frontend/**`
- **Role:** `arn:aws:iam::265978616089:role/rankings-deployment-role-dev`
- **What it does:**
  - Deploys the frontend to **dev** and comments a preview URL
  - URL: https://dev.sportnumerics.com

## Terraform State

Terraform state is stored in S3:
- **Bucket:** `sportnumerics-rankings-terraform-state`
- **Keys:**
  - `infrastructure/prod.tfstate`
  - `infrastructure/dev.tfstate`

## Debug Checklist

If a deploy fails or the site looks wrong:

1. **Check GitHub Actions logs** for the workflow that should have run.
2. **Verify role assumptions** (OIDC permissions, role ARN in workflow).
3. **Backend issues:**
   - ECS task didn’t roll? Check `backend/run.sh prod` output.
   - Confirm image pushed to ECR.
4. **Frontend issues:**
   - S3 upload success + CloudFront invalidation.
   - Verify the preview URL (dev) or `https://sportnumerics.com` (prod).
5. **Infra issues:**
   - Terraform errors usually indicate drift or missing permissions.
6. **Health endpoint:**
   - `GET /api/health` should return 200 and show `gitSha` / `buildTime`.
