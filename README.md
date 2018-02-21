# aws-service-status
Python script for parsing and reporting on AWS Service Health Dashboard data

## To Run from the CLI

### Get a high level summary
```bash
pip install -r requirements.txt
python awsstatusdata.py
109 known services and 17 regions
0 current issues, 174 archived issues for 368 days
```

### Specify the service and the region
```bash
python awsstatusdata.py lambda london
109 known services and 17 regions
0 current issues, 174 archived issues for 368 days
0 current issues, 0 archived issues for lambda in eu-west-2
```

### Specify the region
```bash
109 known services and 17 regions
0 current issues, 174 archived issues for 368 days
0 current issues, 1 archived issues for all services in eu-west-2

Archived Issues:
----------------
{'date': 1490373984,
 'description': ' 9:46 AM PDT\xa0We are temporarily running low on t2.micro '
                'instance capacity in the EU-WEST-2 Region. All other instance '
                'types are available. For customers that do receive an '
                'Insufficient Capacity Error for an instance launch request, '
                'we recommend using t2.nano, t2.small, t2.medium, t2.large or '
                'any of the other instance families. We are working to '
                'increase t2.micro instance capacity and expect to be back to '
                'normal levels within the next few hours. Instances that are '
                'currently running are not affected.12:10 PM PDT\xa0We have '
                'added additional t2.micro instance capacity in the EU-WEST-2 '
                'Region and are now successfully provisioning launches of new '
                't2.micro instances. Until t2.micro instance capacity returns '
                'to normal levels, some customers may continue to see '
                'Insufficient Capacity Errors for new launch requests. In '
                'those cases, we continue to recommend using t2.nano, '
                't2.small, t2.medium, t2.large or any of the other instance '
                'families. All other instance families (C4, D2, I3, M4, R4 and '
                'X1) and instances that are currently running remain '
                'unaffected. We expect t2.micro instance capacity to return to '
                'normal levels within the next hour. 1:08 PM PDT\xa0We can '
                'confirm that t2.micro instance capacity has now returned to '
                'normal levels in the EU-WEST-2 Region and we are no longer '
                'returning Insufficient Capacity Errors for new t2.micro '
                'instance launch requests. The issue has been resolved and the '
                'service is operating normally. ',
 'region_code': 'eu-west-2',
 'region_name': 'London',
 'service_code': 'ec2',
 'service_name': 'Amazon Elastic Compute Cloud',
 'summary': '[RESOLVED] t2.micro Instance Capacity'}
```

### Specify the service
```bash
python awsstatusdata.py lambda
109 known services and 17 regions
0 current issues, 174 archived issues for 368 days
0 current issues, 4 archived issues for lambda in all regions

Archived Issues:
----------------
{'date': 1503513333,
 'description': '11:35 AM PDT\xa0We are investigating increased API error '
                'rates and event processing latency in the EU-WEST-1 Region. '
                '12:22 PM PDT\xa0Between 10:35 AM and 12:15 PM PDT we '
                'experienced elevated API error rates and event processing '
                'latencies in the EU-WEST-1 Region. The issue has been '
                'resolved and the service is operating normally. ',
 'region_code': 'eu-west-1',
 'region_name': 'Ireland',
 'service_code': 'lambda',
 'service_name': 'AWS Lambda',
 'summary': '[RESOLVED] Increased API Error Rates'}
{'date': 1498180054,
 'description': ' 6:07 PM PDT\xa0We are investigating increased API error '
                'rates and latencies in the US-EAST-1 Region. 6:23 PM PDT\xa0'
                'We can confirm increased API error rates and latencies in the '
                'US-EAST-1 Region 6:30 PM PDT\xa0We can confirm increased API '
                'error rates and latencies in the US-EAST-1 Region. 7:47 PM '
                "PDT\xa0We are investigating issues in AWS Lambda's capacity "
                'management subsystem that are causing increased API error '
                'rates and latencies in the US-EAST-1 Region. 8:48 PM PDT\xa0'
                "We have identified issues in AWS Lambda's capacity subsystem "
                'related to the increased API error rates and latencies in the '
                'US-EAST-1 Region and continue to work toward resolution. 9:50 '
                'PM PDT\xa0As we work toward resolution we are temporarily '
                'suspending traffic to US-EAST-1 to restore capacity. '
                'Previously accepted events will be processed as soon as '
                'service is fully restored.10:25 PM PDT\xa0We have restored '
                'capacity and are processing Lambda invocations. API error '
                'rates and latencies remain temporarily elevated in the '
                'US-EAST-1 Region as we complete our resolution steps.11:39 PM '
                'PDT\xa0We have restored capacity and are processing Lambda '
                'invocations. Latencies for some asynchronous invocations may '
                'be temporarily elevated in the US-EAST-1 Region as we work '
                'through the backlog of events.Jun 23,  1:26 AM PDT\xa0We are '
                'currently experiencing elevated latencies for some '
                'asynchronus invocations in the US-EAST-1 Region and continue '
                'to work towards resolution.Jun 23,  3:05 AM PDT\xa0Between '
                'June 22 5:31 PM and June 23 2:32 AM PDT, we experienced '
                'increased error rates for APIs and increased latencies in the '
                "US-EAST-1 Region related to Lambda's capacity subsystem. The "
                'issue has been resolved and the service is operating '
                'normally.',
 'region_code': 'us-east-1',
 'region_name': 'N. Virginia',
 'service_code': 'lambda',
 'service_name': 'AWS Lambda',
 'summary': '[RESOLVED] Increased API Error Rates and Latencies'}
{'date': 1491873439,
 'description': ' 6:17 PM PDT\xa0We are investigating increased API error '
                'rates in the US-EAST-1 Region. 7:04 PM PDT\xa0We can confirm '
                'increased API error rates in the US-EAST-1 Region and are '
                'continuing to investigate. 8:13 PM PDT\xa0We continue to work '
                'towards full resolution. Customers may continue to experience '
                'increased latencies as we process accumulated events. 9:05 PM '
                'PDT\xa0Between 5:25 PM and 9:00 PM PDT we experienced '
                'elevated error rates and event processing latencies in the '
                'US-EAST-1 Region. The issue has been resolved and the service '
                'is operating normally.',
 'region_code': 'us-east-1',
 'region_name': 'N. Virginia',
 'service_code': 'lambda',
 'service_name': 'AWS Lambda',
 'summary': '[RESOLVED] Increased API Error Rates'}
{'date': 1488310576,
 'description': '11:38 AM PST\xa0We are confirming increased error rates and '
                'elevated latencies for AWS Lambda requests in the US-EAST-1 '
                'Region. Newly created functions and console editing are also '
                'affected. 2:47 PM PST\xa0We continue to experience elevated '
                'error rates and latencies for AWS Lambda API requests in the '
                'US-EAST-1 Region. New function creation, update of existing '
                'functions and console editing are now operating normally. We '
                'have identified the root cause and working to resolve the '
                'issue. 4:38 PM PST\xa0We continue to see recovery in error '
                'rates and latencies for AWS Lambda API requests in the '
                'US-EAST-1 Region. Some customers can still experience errors '
                'in new function creation, update of existing functions and '
                'console editing. We continue to work towards full resolution. '
                '7:13 PM PST\xa0Between 9:37 AM and 6:45 PM PST we experienced '
                'elevated error rates and latencies for Lambda APIs in the '
                'US-EAST-1 Region. New function creation, update of existing '
                'functions and console editing were also impacted. The issue '
                'has been resolved and the service is operating normally. Some '
                'customers may see delays in Lambda execution of asynchronous '
                'Lambda calls as we work through the asynchronous call '
                'backlog. ',
 'region_code': 'us-east-1',
 'region_name': 'N. Virginia',
 'service_code': 'lambda',
 'service_name': 'AWS Lambda',
 'summary': '[RESOLVED] Increased Error Rates'}
```

