# Deployment Guide

This document describes how deployments work for sportnumerics.com and how to debug common issues.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     GitHub Actions (CI/CD)                   │
│  Triggers: push to main, workflow_dispatch                  │
└─────────────────────────────────────────────────────────────┘
                              │
                    ┌─────────┴──────────┐
                    │                    │
           ┌────────▼────────┐  ┌────────▼────────┐
           │   Backend       │  │   Frontend      │
           │   (ECS Fargate) │  │   (Lambda)      │
           └────────┬────────┘  └────────┬────────┘
                    │                    │
           ┌────────▼────────┐  ┌────────▼────────┐
           │  S3 Data Bucket │  │   CloudFront    │
           │  (JSON/Parquet) │  │   (CDN)         │
           └─────────────────┘  └─────────────────┘
```

## Deployment Workflows

### Backend Deployment
**File**: `.github/workflows/deploy-backend.yml`  
**Triggers**: 
- Push to `main` with changes to `backend/**`
- Manual dispatch via GitHub UI

**Steps**:
1. Checkout code
2. Assume AWS role: `rankings-deployment-role-prod`
3. Initialize Terraform (`backend/infra/environments/prod`)
4. Build multi-arch Docker image (arm64 + amd64)
5. Push to ECR: `rankings-backend-prod`
6. Register new ECS task definition

**IAM Role**: `arn:aws:iam::265978616089:role/rankings-deployment-role-prod`

**To trigger manually**:
```bash
cd backend
./deploy.sh prod   # Build + push Docker image
./run.sh prod      # Trigger ECS task run
```

### Frontend Deployment
**File**: `.github/workflows/deploy-frontend.yml`  
**Triggers**:
- Push to `main` with changes to `frontend/**`
- Manual dispatch

**Steps**:
1. Checkout code
2. Setup Node.js 20 + npm cache
3. Restore Next.js build cache
4. Assume AWS role: `rankings-deployment-role-prod`
5. Run `frontend/deploy.sh prod`:
   - `npm install`
   - Set env vars: `DATA_BUCKET`, `GIT_SHA`, `BUILD_TIME`
   - `npm run build` (standalone output)
   - Terraform apply (Lambda + CloudFront)
   - Invalidate CloudFront cache (`/*`)

**IAM Role**: `arn:aws:iam::265978616089:role/rankings-deployment-role-prod`

**To trigger manually**:
```bash
cd frontend
./deploy.sh prod
```

### Infrastructure Deployment
**File**: `.github/workflows/deploy-infra.yml`  
**Triggers**:
- Push to `main` with changes to `infrastructure/**`
- Manual dispatch

**Steps**:
1. Terraform apply on `infrastructure/environments/prod`
2. Updates: S3 buckets, IAM roles, permissions boundaries

**Terraform State**: `s3://sportnumerics-rankings-terraform-state/infrastructure/prod.tfstate`

## Key Resources

### Backend (Production)
- **ECS Cluster**: `rankings-backend-prod`
- **Task Definition**: `rankings-backend-prod` (family)
- **ECR Repository**: `rankings-backend-prod`
- **CloudWatch Logs**: `/rankings/prod/backend`
- **S3 Bucket**: `sportnumerics-rankings-bucket-prod`
- **Schedule**: Runs every 12 hours during season (Jan-May): `cron(0 */12 * JAN-MAY ?)`

### Frontend (Production)
- **Lambda**: `sportnumerics-ranking-frontend-prod`
- **CloudFront Distribution**: Check `frontend/infra/environments/prod` outputs
- **S3 Bucket**: `sportnumerics-rankings-bucket-prod` (reads data)
- **Domain**: `sportnumerics.com` (Route53 managed)

### Development Environment
- **Backend ECS**: `rankings-backend-dev`
- **Frontend Lambda**: `sportnumerics-ranking-frontend-dev`
- **S3 Bucket**: `sportnumerics-rankings-bucket-dev`
- **Domain**: `dev.sportnumerics.com`
- **Schedule**: Runs weekly on Mondays (Jan-May): `cron(0 0 ? JAN-MAY MON)`

## Debugging Common Issues

### 1. "2026 data not showing up"
**Symptoms**: Frontend only shows 2025, 2024, etc.

**Diagnosis**:
```bash
# Check if 2026 data exists in S3
aws s3 ls s3://sportnumerics-rankings-bucket-prod/data/2026/

# Check backend logs for errors
aws logs tail /rankings/prod/backend --since 6h --format short | grep -i error

# Check last successful scrape
aws logs describe-log-streams --log-group-name /rankings/prod/backend \
  --order-by LastEventTime --descending --max-items 1
```

**Common causes**:
- Backend scraper crashed before syncing data
- NCAA/MCLA source website changes (403, HTML structure)
- S3 sync failed

**Fix**:
- Check PR #23 (graceful 403 handling)
- Check PR #19 (User-Agent + MCLA HTML updates)
- Trigger manual backend run: `cd backend && ./run.sh prod 2026`

### 2. "Terraform apply failed in CI"
**Symptoms**: GitHub Actions shows Terraform error

**Common causes**:
- IAM permissions missing
- Resource already exists (naming conflict)
- Terraform state lock

**Fix**:
```bash
# Check Terraform state
aws s3 ls s3://sportnumerics-rankings-terraform-state/

# Unlock if stuck (DANGEROUS - only if no one else is running)
terraform -chdir=infrastructure/environments/prod force-unlock <LOCK_ID>

# Import existing resource
terraform -chdir=infrastructure/environments/prod import <RESOURCE> <AWS_ID>
```

### 3. "CloudFront showing stale data"
**Symptoms**: Changes deployed but site unchanged

**Diagnosis**:
```bash
# Check CloudFront invalidation status
aws cloudfront list-invalidations --distribution-id <DIST_ID>

# Check Lambda function update time
aws lambda get-function --function-name sportnumerics-ranking-frontend-prod \
  --query 'Configuration.LastModified'
```

**Fix**:
```bash
# Manual invalidation
aws cloudfront create-invalidation \
  --distribution-id <DIST_ID> \
  --paths "/*"
```

### 4. "Backend scraper timing out"
**Symptoms**: ECS task stopped with exit code 137 (OOM) or timeout

**Diagnosis**:
```bash
# Check task stopped reason
aws ecs describe-tasks --cluster rankings-backend-prod \
  --tasks <TASK_ARN> --query 'tasks[0].stoppedReason'

# Check memory usage in logs
aws logs tail /rankings/prod/backend --since 1h | grep -i memory
```

**Fix**:
- Increase task memory in `backend/infra/modules/task/main.tf` (currently 6144 MB)
- Increase timeout (currently 30min default for ECS tasks)

### 5. "/api/health shows 'unknown' for gitSha"
**Symptoms**: Health endpoint returns `"gitSha": "unknown"`

**Diagnosis**:
```bash
# Check if build-info.json was created during build
# (Should happen in GitHub Actions, not locally)
cat frontend/public/build-info.json
```

**Fix**: See PR #21 - build info is written during `npm run build` via `scripts/write-build-info.js`

## Manual Operations

### Trigger Backend Scrape (Production)
```bash
cd backend
./run.sh prod          # Run with current year
./run.sh prod 2025     # Run specific year
```

### Trigger Backend Scrape (Dev)
```bash
cd backend
./run.sh dev 2025
```

### Check Backend Task Status
```bash
aws ecs list-tasks --cluster rankings-backend-prod
aws ecs describe-tasks --cluster rankings-backend-prod --tasks <TASK_ARN>
```

### View Logs
```bash
# Production backend
aws logs tail /rankings/prod/backend --follow

# Dev backend
aws logs tail /rankings/dev/backend --follow

# Filter for errors
aws logs tail /rankings/prod/backend --since 2h --format short | grep -i error
```

### Check S3 Data
```bash
# List available years
aws s3 ls s3://sportnumerics-rankings-bucket-prod/data/

# Check specific year's data
aws s3 ls s3://sportnumerics-rankings-bucket-prod/data/2026/ --recursive

# Download a file for inspection
aws s3 cp s3://sportnumerics-rankings-bucket-prod/data/2026/teams/mcla.json -
```

## IAM Roles & Permissions

### Deployment Roles
Created by `infrastructure/modules/cicd/main.tf`:

- **`rankings-deployment-role-prod`**: Full access to prod resources
- **`rankings-deployment-role-dev`**: Scoped to dev resources only (Stage=dev tag)
- **Permissions Boundary**: `rankings-permissions-boundary` (limits all created roles)

### Runtime Roles
Created by `backend/infra/modules/task/main.tf` and `frontend/infra/modules/task/main.tf`:

- **`rankings-backend-task-role-{env}`**: S3 read/write access to data bucket
- **`rankings-backend-execution-role-{env}`**: ECR pull, CloudWatch logs
- **`rankings-backend-scheduler-role-{env}`**: Trigger ECS tasks
- **`rankings-frontend-lambda-role-{env}`**: S3 read access, CloudWatch logs

## Terraform State

All Terraform state is stored in S3:

- **Bucket**: `sportnumerics-rankings-terraform-state`
- **Backend (prod)**: `backend/prod.tfstate`
- **Backend (dev)**: `backend/dev.tfstate`
- **Frontend (prod)**: `frontend/prod.tfstate`
- **Frontend (dev)**: `frontend/dev.tfstate`
- **Infrastructure (prod)**: `infrastructure/prod.tfstate`

**⚠️ NEVER** manually edit Terraform state. Use `terraform state` commands or `terraform import`.

## Health Checks

### Quick Smoke Test
```bash
# Frontend health (includes S3 connectivity)
curl https://sportnumerics.com/api/health | jq

# Check data API
curl https://sportnumerics.com/api/teams/mcla | jq '. | keys'

# Dev environment
curl https://dev.sportnumerics.com/api/health | jq
```

### Scheduled Health Monitoring
A cron job runs every 2 hours (managed via OpenClaw) that:
- Checks open PRs
- Reports disk status
- Monitors backend task health

## Rollback Procedures

### Backend Rollback
```bash
# List previous task definitions
aws ecs list-task-definitions --family-prefix rankings-backend-prod \
  --sort DESC --max-items 5

# Update service to use previous version
aws ecs update-service --cluster rankings-backend-prod \
  --service rankings-backend-prod \
  --task-definition rankings-backend-prod:<REVISION>
```

### Frontend Rollback
Rollback via Terraform (reverts to previous Lambda code):
```bash
cd frontend
git checkout <PREVIOUS_COMMIT>
./deploy.sh prod
```

Or roll forward with a hotfix PR.

## Cost Monitoring

**Primary costs**:
- **CloudFront**: CDN bandwidth + requests
- **Lambda**: Frontend invocations + duration
- **ECS Fargate**: Backend task runs (12h intervals during season)
- **S3**: Storage + requests
- **CloudWatch Logs**: Ingestion + storage

**Cost optimization tips**:
- Reduce CloudWatch log retention (currently unlimited)
- Cache CloudFront aggressively
- Optimize Lambda memory allocation
- Minimize ECS task runtime

## Contact & Support

- **Repository**: https://github.com/sportnumerics/rankings
- **Primary maintainer**: Will
- **AWS Account**: 265978616089
- **Region**: us-west-2 (Oregon)

---

**Last Updated**: 2026-02-03
