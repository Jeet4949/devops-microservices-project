pipeline {
    agent any

    stages {
        stage('Deploy to AWS Cloud') {
            steps {
                sshagent(credentials: ['aws-ec2-key']) {
                    sh '''
                        ssh -o StrictHostKeyChecking=no ubuntu@13.60.18.181 "
                            cd devops-microservices-project &&
                            git pull origin main &&
                            sudo docker-compose down &&
                            sudo docker-compose up -d --build
                        "
                    '''
                }
            }
        }
    }
}
