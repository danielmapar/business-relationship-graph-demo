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
echo "Cleaning up Step Functions state machines..."
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

echo "Cleanup complete in us-east-2 region!"