---
name: docker-build-push
description: Build and push multi-platform Docker images to Google Artifact Registry. Use when user asks to build, push, or deploy a Docker image with a tag. Triggers: "build and push", "push docker image", "build with tag", "deploy image".
context: fork
---

# Docker Build and Push

Build and push multi-platform Docker images to Google Artifact Registry for any teammelosys repository.

## How to Use

1. **Detect repository name** from current working directory (basename of git root or pwd)
2. **Detect project type** to determine build command
3. **Build and push** with the detected settings

## Registry Pattern

```
europe-north1-docker.pkg.dev/nais-management-233d/teammelosys/{REPO_NAME}
```

Replace `{REPO_NAME}` with the actual repository name (e.g., `melosys-api`, `melosys-web`, `melosys-eessi`).

## Detect Repository Name

```bash
# Get repo name from git remote or directory name
REPO_NAME=$(basename "$(git rev-parse --show-toplevel 2>/dev/null || pwd)")
echo "Repository: $REPO_NAME"
```

## Detect Project Type and Build

| Project Type | Detection | Build Command |
|-------------|-----------|---------------|
| Maven/Java/Kotlin | `pom.xml` exists | `make build-fast` or `mvn package -DskipTests` |
| Node.js/pnpm | `pnpm-lock.yaml` exists | `pnpm install && pnpm build` |
| Node.js/npm | `package-lock.json` exists | `npm ci && npm run build` |
| Makefile only | `Makefile` exists | `make build` |

## Build and Push Command

```bash
docker buildx build --platform linux/amd64,linux/arm64 \
  -t europe-north1-docker.pkg.dev/nais-management-233d/teammelosys/${REPO_NAME}:TAG \
  --push .
```

Replace `TAG` with user-specified tag.

## Complete Workflow

1. **Detect repo name**: `REPO_NAME=$(basename "$(git rev-parse --show-toplevel 2>/dev/null || pwd)")`
2. **Build the application** based on project type (see table above)
3. **Run buildx build** with `--push`
4. **Report**: tag, platforms, manifest digest

## Setup (if buildx not configured)

```bash
docker buildx create --name multiplatform --use --driver docker-container || docker buildx use multiplatform
```

## Error Handling

### Authentication expired
Message: "Reauthentication failed"
Solution: Ask user to run `gcloud auth login`, then retry

### No matching manifest for linux/amd64
Cause: Image built only for arm64
Solution: Use `--platform linux/amd64,linux/arm64` flag

### No Dockerfile found
Solution: Check if Dockerfile exists in repo root. Some repos may have it in a subdirectory.

## Output Format

After successful push:
```
Done!

Image details:
- Repository: {REPO_NAME}
- Tag: europe-north1-docker.pkg.dev/nais-management-233d/teammelosys/{REPO_NAME}:TAG
- Platforms: linux/amd64, linux/arm64
- Manifest digest: sha256:...
