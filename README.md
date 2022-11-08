# aws-service-status
Python script for parsing and reporting on AWS Service Health Dashboard data

## To Run from the CLI

### Install the CLI tool
```bash
python3 -m venv .
source ./bin/activate
pip3 install -r requirements.txt
```

### Get a high level summary
```bash
./awsstatusdata.py
223 known services and 25 regions
1 current issues, 83 archived issues for 371 days
For more specific detail please specify a service name, region name, or both.
For a list of services specify 'services', for a list of regions specify 'regions'.
Example Usage:
        $> ./awsstatusdata.py services
        $> ./awsstatusdata.py lambda eu-west-1
```

### Specify the service and the region
```bash
./awsstatusdata.py lambda eu-west-2
223 known services and 25 regions
1 current issues, 83 archived issues for 371 days
0 current issues, 0 archived issues for lambda in eu-west-2
```

### Specify the region
```bash
./awsstatusdata.py eu-west-2
223 known services and 25 regions
1 current issues, 83 archived issues for 371 days
0 current issues, 1 archived issues for all services in eu-west-2

Archived Issues:
----------------
[
    {
        "date": "2022-07-10 17:56:38",
        "description": "10:56 AM PDT\u00a0We are investigating ...",
        "duration_mins": 191.0,
        "region_code": "eu-west-2",
        "region_name": "London",
        "service_code": "ec2",
        "service_name": "Amazon Elastic Compute Cloud",
        "summary": "[RESOLVED] Impaired EC2 Instances",
        "timeline": [
            [
                "10:56 AM PDT",
                "We are investigating instance impairments in a single Availability Zone ..."
            ],
            [
                "11:13 AM PDT",
                "Some instances in a single Availability Zone are ..."
            ],
            [
                "11:55 AM PDT",
                "We continue to investigate ..."
            ],
            [
                "12:25 PM PDT",
                "We have resolved the root cause ..."
            ],
            [
                "1:01 PM PDT",
                "We continue to make progress in ..."
            ],
            [
                "1:53 PM PDT",
                "We have resolved the impairments for ..."
            ],
            [
                "2:07 PM PDT",
                "Starting at 10:25 AM PDT, some EC2 instances ..."
            ]
        ],
        "timestamp": 1657475798
    }
]
```

### Specify the service
```bash
./awsstatusdata.py lambda
223 known services and 25 regions
1 current issues, 83 archived issues for 371 days
0 current issues, 2 archived issues for lambda in all regions

Archived Issues:
----------------
...
```

