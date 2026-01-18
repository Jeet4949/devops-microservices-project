pipeline {
    agent any
    environment {
        // We call this v2 to distinguish it from your first project
        IMAGE_NAME = "jeet4949/my-python-app:v2" 
    }
    stages {
        stage('Checkout Code') {
            steps {
                echo 'Pulling code from GitHub...'
                // Jenkins will automatically pull from the repo we configure in the GUI
                checkout scm
            }
        }
        
        stage('Build Image') {
            steps {
                script {
                    echo 'Building Docker Image...'
                    // We only build the current directory (the python app)
                    sh "docker build -t $IMAGE_NAME ."
                }
            }
        }
        
        stage('Push to Docker Hub') {
            steps {
                script {
                    withCredentials([usernamePassword(credentialsId: 'docker-hub-creds', passwordVariable: 'DOCKER_PASS', usernameVariable: 'DOCKER_USER')]) {
                        sh "echo $DOCKER_PASS | docker login -u $DOCKER_USER --password-stdin"
                        sh "docker push $IMAGE_NAME"
                    }
                }
            }
        }
    }
}
