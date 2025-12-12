#!/bin/bash

# t2.micro CPU 크레딧 최적화 스크립트
# EC2 인스턴스에서 실행하여 CPU 크레딧 사용량을 모니터링하고 최적화

echo "=== t2.micro CPU 크레딧 최적화 ==="

# CPU 크레딧 잔량 확인
echo "현재 CPU 크레딧 잔량:"
aws ec2 describe-instance-credit-specifications \
    --instance-ids $(curl -s http://169.254.169.254/latest/meta-data/instance-id) \
    --query 'InstanceCreditSpecifications[0].CpuCredits' \
    --output text

# CPU 사용률 모니터링 설정
echo "CPU 사용률 모니터링을 설정합니다..."

# CloudWatch 에이전트 설치
wget https://s3.amazonaws.com/amazoncloudwatch-agent/amazon_linux/amd64/latest/amazon-cloudwatch-agent.rpm
sudo rpm -U ./amazon-cloudwatch-agent.rpm

# CloudWatch 설정 파일 생성
sudo tee /opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.json > /dev/null << 'EOF'
{
    "metrics": {
        "namespace": "HybridChatbot/CPU",
        "metrics_collected": {
            "cpu": {
                "measurement": ["cpu_usage_idle", "cpu_usage_iowait"],
                "metrics_collection_interval": 60
            }
        }
    }
}
EOF

# CloudWatch 에이전트 시작
sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl \
    -a fetch-config -m ec2 -c file:/opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.json -s

# CPU 크레딧 최적화를 위한 설정
echo "CPU 크레딧 최적화 설정을 적용합니다..."

# CPU 거버너를 powersave로 설정 (크레딧 절약)
echo 'GOVERNOR="powersave"' | sudo tee /etc/sysconfig/cpupower

# 불필요한 서비스 중지
sudo systemctl stop postfix
sudo systemctl disable postfix

# 메모리 최적화
echo "vm.swappiness=10" | sudo tee -a /etc/sysctl.conf
sudo sysctl -p

# 로그 로테이션 설정
sudo tee /etc/logrotate.d/hybrid-chatbot > /dev/null << 'EOF'
/var/log/hybrid-chatbot.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 644 ec2-user ec2-user
}
EOF

echo "=== 최적화 완료 ==="
echo "CPU 크레딧 모니터링: aws ec2 describe-instance-credit-specifications --instance-ids \$(curl -s http://169.254.169.254/latest/meta-data/instance-id)"
echo "CPU 사용률 확인: top -bn1 | grep 'Cpu(s)'"
echo "메모리 사용률 확인: free -h"
