"""AWS EventBridge-based scheduler for automated data ingestion."""

import logging
import json
from typing import Dict, Any, Optional

import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


class EventBridgeScheduler:
    """
    AWS EventBridge scheduler for automated satellite data downloads.
    
    Creates and manages EventBridge rules for triggering Lambda functions
    or other AWS services on a schedule.
    """
    
    def __init__(
        self,
        region: str = 'us-east-1',
        aws_access_key_id: Optional[str] = None,
        aws_secret_access_key: Optional[str] = None
    ):
        """
        Initialize EventBridge scheduler.
        
        Args:
            region: AWS region
            aws_access_key_id: AWS access key (optional)
            aws_secret_access_key: AWS secret key (optional)
        """
        # Initialize EventBridge client
        session_kwargs = {'region_name': region}
        if aws_access_key_id and aws_secret_access_key:
            session_kwargs.update({
                'aws_access_key_id': aws_access_key_id,
                'aws_secret_access_key': aws_secret_access_key
            })
        
        self.events_client = boto3.client('events', **session_kwargs)
        self.region = region
        logger.info("EventBridge scheduler initialized")
    
    def create_schedule_rule(
        self,
        rule_name: str,
        schedule_expression: str,
        description: str = "Satellite data ingestion schedule",
        enabled: bool = True
    ) -> str:
        """
        Create an EventBridge schedule rule.
        
        Args:
            rule_name: Name of the rule
            schedule_expression: Cron or rate expression
                Examples:
                - "cron(0 2 * * ? *)" - Daily at 2 AM UTC
                - "rate(1 hour)" - Every hour
            description: Rule description
            enabled: Whether the rule is enabled
            
        Returns:
            ARN of the created rule
        """
        try:
            response = self.events_client.put_rule(
                Name=rule_name,
                ScheduleExpression=schedule_expression,
                State='ENABLED' if enabled else 'DISABLED',
                Description=description
            )
            
            rule_arn = response['RuleArn']
            logger.info(f"Created EventBridge rule: {rule_name} ({rule_arn})")
            return rule_arn
            
        except ClientError as e:
            logger.error(f"Error creating EventBridge rule: {e}")
            raise
    
    def add_lambda_target(
        self,
        rule_name: str,
        lambda_arn: str,
        input_data: Optional[Dict[str, Any]] = None,
        target_id: str = "1"
    ) -> bool:
        """
        Add a Lambda function as a target for the EventBridge rule.
        
        Args:
            rule_name: Name of the rule
            lambda_arn: ARN of the Lambda function
            input_data: Optional input data to pass to Lambda
            target_id: Unique identifier for the target
            
        Returns:
            True if successful
        """
        try:
            target = {
                'Id': target_id,
                'Arn': lambda_arn
            }
            
            if input_data:
                target['Input'] = json.dumps(input_data)
            
            self.events_client.put_targets(
                Rule=rule_name,
                Targets=[target]
            )
            
            logger.info(f"Added Lambda target to rule {rule_name}: {lambda_arn}")
            return True
            
        except ClientError as e:
            logger.error(f"Error adding Lambda target: {e}")
            raise
    
    def add_sns_target(
        self,
        rule_name: str,
        sns_topic_arn: str,
        input_data: Optional[Dict[str, Any]] = None,
        target_id: str = "1"
    ) -> bool:
        """
        Add an SNS topic as a target for the EventBridge rule.
        
        Args:
            rule_name: Name of the rule
            sns_topic_arn: ARN of the SNS topic
            input_data: Optional input data
            target_id: Unique identifier for the target
            
        Returns:
            True if successful
        """
        try:
            target = {
                'Id': target_id,
                'Arn': sns_topic_arn
            }
            
            if input_data:
                target['Input'] = json.dumps(input_data)
            
            self.events_client.put_targets(
                Rule=rule_name,
                Targets=[target]
            )
            
            logger.info(f"Added SNS target to rule {rule_name}: {sns_topic_arn}")
            return True
            
        except ClientError as e:
            logger.error(f"Error adding SNS target: {e}")
            raise
    
    def delete_rule(self, rule_name: str) -> bool:
        """
        Delete an EventBridge rule.
        
        Args:
            rule_name: Name of the rule to delete
            
        Returns:
            True if successful
        """
        try:
            # First, remove all targets
            targets_response = self.events_client.list_targets_by_rule(Rule=rule_name)
            if targets_response.get('Targets'):
                target_ids = [t['Id'] for t in targets_response['Targets']]
                self.events_client.remove_targets(
                    Rule=rule_name,
                    Ids=target_ids
                )
            
            # Then delete the rule
            self.events_client.delete_rule(Name=rule_name)
            logger.info(f"Deleted EventBridge rule: {rule_name}")
            return True
            
        except ClientError as e:
            logger.error(f"Error deleting EventBridge rule: {e}")
            return False
    
    def enable_rule(self, rule_name: str) -> bool:
        """
        Enable an EventBridge rule.
        
        Args:
            rule_name: Name of the rule
            
        Returns:
            True if successful
        """
        try:
            self.events_client.enable_rule(Name=rule_name)
            logger.info(f"Enabled EventBridge rule: {rule_name}")
            return True
        except ClientError as e:
            logger.error(f"Error enabling rule: {e}")
            return False
    
    def disable_rule(self, rule_name: str) -> bool:
        """
        Disable an EventBridge rule.
        
        Args:
            rule_name: Name of the rule
            
        Returns:
            True if successful
        """
        try:
            self.events_client.disable_rule(Name=rule_name)
            logger.info(f"Disabled EventBridge rule: {rule_name}")
            return True
        except ClientError as e:
            logger.error(f"Error disabling rule: {e}")
            return False
    
    def list_rules(self, name_prefix: str = "") -> list:
        """
        List all EventBridge rules.
        
        Args:
            name_prefix: Optional prefix to filter rules
            
        Returns:
            List of rule information
        """
        try:
            kwargs = {}
            if name_prefix:
                kwargs['NamePrefix'] = name_prefix
            
            response = self.events_client.list_rules(**kwargs)
            
            rules = []
            for rule in response.get('Rules', []):
                rules.append({
                    'name': rule['Name'],
                    'arn': rule['Arn'],
                    'state': rule['State'],
                    'schedule': rule.get('ScheduleExpression', 'N/A'),
                    'description': rule.get('Description', '')
                })
            
            return rules
            
        except ClientError as e:
            logger.error(f"Error listing rules: {e}")
            return []
