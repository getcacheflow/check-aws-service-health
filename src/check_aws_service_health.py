import argparse
import os
import boto3
from botocore.exceptions import NoCredentialsError

aws_access_key_id: str = os.getenv('aws-access-key-id')
aws_secret_access_key: str = os.getenv('aws-secret-access-key')
aws_region: str = os.getenv('aws-region')

def get_aws_health_status(service_names: list[str]) -> None:
    try:
        session = boto3.Session(
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=aws_region
        )
        health_client = session.client('health')

        all_results = []  # List to store results of all services

        for service_name in service_names:
            print(f"\nChecking health status for {service_name}:")
            response = health_client.describe_events(
                Filters=[{'Name': 'service-name', 'Values': [service_name]}],
                MaxResults=10
            )

            for event in response['Events']:
                result = f"Service: {service_name}, Event ID: {event['EventId']}, Status: {event['Status']}"
                all_results.append(result)
                print(result)
                
                # If any service is unhealthy, exit with non-zero status
                if event['Status']!= 'OK':
                    print(f"\033[91m{service_name} is reported as unhealthy.\033[0m")
                    
        # Print all results before exiting
        for result in all_results:
            print(result)
        
        # Determine if any service is unhealthy
        if any(status!= 'OK' for status in all_results):
            print("\nOne or more services are unhealthy. Exiting with status 1.")
            return False
        
        return True
    
    except NoCredentialsError:
        print("No AWS credentials found")
        exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        exit(1)


def main():
    parser = argparse.ArgumentParser(description='Check AWS service health.')
    parser.add_argument('-h', '--help', action='version', version='%(prog)s 1.0', help='Show this message and exit.', default=False)
    
    args = parser.parse_args()

    if args.help:
        print("Available services:")
        print(", ".join(['Amazon S3', 'Amazon CloudFront', 'Amazon EC2', 'Amazon ECS', 'Amazon SQS', 'Amazon RDS', 'Amazon SSM', 'Route 53']))
        exit(1)

    services_env_var: str = os.getenv('AWS_SERVICES', '')
    if services_env_var:
        services_to_check: list[str] = services_env_var.split(',')
    else:
        print("No services specified. Exiting.")
        exit(1)

    healthy: bool = get_aws_health_status(services_to_check)
    if healthy:
        print("All services are healthy.")
    else:
        print("At least one service is unhealthy.")
        exit(1)

if __name__ == "__main__":
    main()
