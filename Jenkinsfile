pipeline {
    agent any

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
    }

    post {
        success {
            echo 'CI pipeline completed successfully!'
        }

        failure {
            echo 'CI pipeline failed. Check the Jenkins console output.'
        }

        always {
            sh 'rm -rf .jenkins-venv'
        }
    }
}
