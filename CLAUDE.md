<!-- telbase:start -->
## Telbase Deployment

Deploy: `telbase deploy --local --json --auto` (stack auto-detected on deploy)

### File Storage

Deploy with `--storage` to provision R2 file storage. These env vars are auto-injected:

| Variable | Purpose |
|----------|--------|
| `R2_ENDPOINT` | S3-compatible endpoint URL |
| `R2_ACCESS_KEY_ID` | Access key |
| `R2_SECRET_ACCESS_KEY` | Secret key |
| `R2_BUCKET_NAME` | Bucket name |

Use `@aws-sdk/client-s3` with these env vars. Storage is S3-compatible.

### Troubleshooting

| Issue | Command |
|-------|--------|
| Deploy failed | `telbase deploys status <id>` |
| Empty logs | Wait 2 min (GCP), then `telbase logs --lines 50` |
| Missing DATABASE_URL | Provider-injected. Check: `telbase db status` |
| Build cache stale | `telbase deploy --clear-cache` |
| Wrong ORM detected | `telbase deploy --db-type <prisma\|drizzle>` |
<!-- telbase:end -->
