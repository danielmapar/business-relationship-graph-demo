#!/bin/bash

# Set AWS region
export AWS_DEFAULT_REGION=us-east-2

# List all task definition families
families=$(aws ecs list-task-definition-families --status ACTIVE --query 'families[]' --output text)

for family in $families; do
    # Get all active task definition ARNs for this family
    task_defs=$(aws ecs list-task-definitions --family-prefix $family --status ACTIVE --query 'taskDefinitionArns[]' --output text)
    
    for task_def in $task_defs; do
        echo "Deregistering task definition: $task_def"
        aws ecs deregister-task-definition --task-definition $task_def > /dev/null
    done
done

# Wait a bit for deregistrations to complete
sleep 5

# Delete all INACTIVE task definitions in batches of 10
inactive_tasks=($(aws ecs list-task-definitions --status INACTIVE --query 'taskDefinitionArns[]' --output text))

if [ ${#inactive_tasks[@]} -gt 0 ]; then
    echo "Deleting inactive task definitions in batches..."
    
    # Process in batches of 10
    for ((i=0; i<${#inactive_tasks[@]}; i+=10)); do
        batch=("${inactive_tasks[@]:i:10}")  # Take up to 10 items
        
        echo "Deleting batch of ${#batch[@]} task definitions..."
        aws ecs delete-task-definitions --task-definitions ${batch[@]}
    done
fi

# List and delete all Step Functions state machines
state_machines=$(aws stepfunctions list-state-machines --query 'stateMachines[*].stateMachineArn' --output text)

if [ -n "$state_machines" ]; then
    for machine in $state_machines; do
        echo "Deleting state machine: $machine"
        aws stepfunctions delete-state-machine --state-machine-arn $machine
    done
    echo "Step Functions cleanup complete!"
else
    echo "No Step Functions state machines found."
fi

# List and delete all EventBridge schedules and schedule groups
# First, delete all schedules in each schedule group
schedule_groups=$(aws scheduler list-schedule-groups --query 'ScheduleGroups[*].Name' --output text)

if [ -n "$schedule_groups" ]; then
    for group in $schedule_groups; do
        echo "Processing schedule group: $group"
        
        # List and delete all schedules in this group
        schedules=$(aws scheduler list-schedules --group-name $group --query 'Schedules[*].Name' --output text)
        if [ -n "$schedules" ]; then
            for schedule in $schedules; do
                echo "Deleting schedule: $schedule in group: $group"
                aws scheduler delete-schedule --name $schedule --group-name $group
            done
        fi
    done
fi

# Delete default group schedules
default_schedules=$(aws scheduler list-schedules --query 'Schedules[*].Name' --output text)
if [ -n "$default_schedules" ]; then
    for schedule in $default_schedules; do
        echo "Deleting schedule: $schedule in default group"
        aws scheduler delete-schedule --name $schedule
    done
fi

## We don't want to delete to delete groups, because those are terraform managed ###
# Delete schedule groups (except default group)
# if [ -n "$schedule_groups" ]; then
#     for group in $schedule_groups; do
#         if [ "$group" != "default" ]; then
#             echo "Deleting schedule group: $group"
#             aws scheduler delete-schedule-group --name $group
#         else
#             echo "Skipping default group"
#         fi
#     done
# fi

# Delete log groups that start with /sigtunnel/
log_groups=$(aws logs describe-log-groups --query "logGroups[?starts_with(logGroupName, '/sigtunnel/')].logGroupName" --output text)

if [ -n "$log_groups" ]; then
    for log_group in $log_groups; do
        echo "Deleting log group: $log_group"
        aws logs delete-log-group --log-group-name "$log_group"
    done
fi

# Clean up S3 buckets starting with sigtunnel-workspace-
workspace_buckets=$(aws s3api list-buckets --query "Buckets[?starts_with(Name, 'sigtunnel-workspace-')].Name" --output text)

if [ -n "$workspace_buckets" ]; then
    for bucket in $workspace_buckets; do
        echo "Emptying bucket: $bucket"
        
        # First remove all objects
        aws s3 rm s3://$bucket --recursive
    done
fi

echo "Cleanup complete in us-east-2 region!"