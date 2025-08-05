# iac/monitoring.tf

resource "aws_sns_topic" "alarm_topic" {
  name = "gym-app-alarms"
  kms_master_key_id = "alias/aws/sns"
}

resource "aws_sns_topic_subscription" "email_subscription" {
  topic_arn = aws_sns_topic.alarm_topic.arn
  protocol  = "email"
  endpoint  = "akashd44@sheridancollege.ca" 
}

resource "aws_cloudwatch_metric_alarm" "ec2_cpu_alarm" {
  alarm_name          = "gym-web-server-cpu-high"
  comparison_operator = "GreaterThanOrEqualToThreshold"
  evaluation_periods  = "2"
  metric_name         = "CPUUtilization"
  namespace           = "AWS/EC2"
  period              = "60" # In seconds
  statistic           = "Average"
  threshold           = "70" # 70 percent
  alarm_description   = "This metric fires when the EC2 CPU is over 70% for 2 minutes."
  alarm_actions       = [aws_sns_topic.alarm_topic.arn]

  dimensions = {
    InstanceId = aws_instance.web_server.id
  }
}