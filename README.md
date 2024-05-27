*** ABANDONED -- AWS Requires an elevated support account ***

# Check AWS Service Health

This GitHub Action checks the health status of specified AWS services.

## Usage

Add the following to your workflow file:

```yaml
name: Check AWS Service Health 
uses: yourusername/check-aws-services-action@v1 
with: 
  services: 'Amazon S3,Amazon RDS'
```
Replace `yourusername` with your GitHub username or organization name.

## Inputs

- `services`: Comma-separated list of AWS services to check. Required.

## License

MIT
