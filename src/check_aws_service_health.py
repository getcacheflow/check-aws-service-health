import os
import datetime
import boto3
from botocore.exceptions import NoCredentialsError

aws_access_key_id: str = os.getenv('AWS_ACCESS_KEY_ID', '')
aws_secret_access_key: str = os.getenv('AWS_SECRET_ACCESS_KEY', '')
aws_region: str = os.getenv('AWS_REGION', '')
aws_services: str = os.getenv('AWS_SERVICES', '')

print(f"aws_access_key_id: {aws_access_key_id}")
print(f"aws_secret_access_key: {aws_secret_access_key}")
print(f"aws_region: {aws_region}")
print(f"aws_services: {aws_services}")

def get_aws_health_status(service_names: list[str]) -> None:
    try:
        session = boto3.Session(
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=aws_region
        )
        health_client = session.client('health')

        all_results = []  # List to store results of all services

        response = health_client.describe_events(
                filter={
                    'startTimes': [
                        {
                            'from': datetime.datetime.now() - datetime.timedelta(days=7)
                        }
                    ],
                    'eventStatusCodes': [
                        'open',
                        'upcoming'
                    ],
                    'regions': [aws_region]
                }
            )
        
        print(f"Response: {response}")

        for service_name in service_names:
            print(f"\nChecking health status for {service_name}:")

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
    if aws_services:
        services_to_check: list[str] = aws_services.split(',')
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
