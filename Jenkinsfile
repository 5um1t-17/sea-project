pipeline {
    agent any

    environment {
        DOCKER_IMAGE = '5um1t/sea-project'
    }

    stages {
        stage('Checkout') {
            steps {
                echo 'Source code checked out from GitHub'
            }
        }

        stage('Setup Python') {
            steps {
                sh '''
                    python3 --version
                    python3 -m venv .jenkins-venv
                    .jenkins-venv/bin/pip install --upgrade pip
                    .jenkins-venv/bin/pip install -r requirements.txt
                    .jenkins-venv/bin/pip install pytest pytest-asyncio
                '''
            }
        }

        stage('Run Tests') {
            steps {
                sh '''
                    .jenkins-venv/bin/python -m pytest -q
                '''
            }
        }

        stage('Build Docker Image') {
            steps {
                sh '''
                    docker build \
                      -t ${DOCKER_IMAGE}:${BUILD_NUMBER} \
                      -t ${DOCKER_IMAGE}:latest .
                '''
            }
        }

        stage('Push to Docker Hub') {
            steps {
                withCredentials([
                    usernamePassword(
                        credentialsId: 'dockerhub',
                        usernameVariable: 'DOCKER_USER',
                        passwordVariable: 'DOCKER_TOKEN'
                    )
                ]) {
                    sh '''
                        echo "$DOCKER_TOKEN" | docker login \
                          -u "$DOCKER_USER" \
                          --password-stdin

                        docker push ${DOCKER_IMAGE}:${BUILD_NUMBER}
                        docker push ${DOCKER_IMAGE}:latest

                        docker logout
                    '''
                }
            }
        }

        stage('Deploy to Kubernetes') {
            steps {
                sh '''
                    export KUBECONFIG=/var/lib/jenkins/.kube/config

                    kubectl apply -f k8s/deployment.yaml
                    kubectl apply -f k8s/service.yaml

                    kubectl set image deployment/telegram-bot \
                      telegram-bot=${DOCKER_IMAGE}:${BUILD_NUMBER}

                    kubectl rollout status deployment/telegram-bot \
                      --timeout=240s

                    kubectl get pods
                    kubectl get services
                '''
            }
        }
    }

    post {
        success {
            echo 'CI/CD pipeline completed successfully!'
        }

        failure {
            echo 'CI/CD pipeline failed. Check the Jenkins console output.'
        }

        always {
            sh 'rm -rf .jenkins-venv'
        }
    }
}
