pipeline {
    agent any

    options {
        timestamps()
        disableConcurrentBuilds()
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Check Python') {
            steps {
                // Для Windows-агента замените sh на bat.
                sh 'python3 --version'
                sh 'python3 -m pip --version'
            }
        }

        stage('Install dependencies') {
            steps {
                sh 'python3 -m pip install -r requirements.txt'
            }
        }

        stage('Automated tests') {
            steps {
                sh 'python3 -m pytest -v'
            }
        }
    }

    post {
        success {
            echo 'CI completed successfully.'
        }
        failure {
            echo 'CI failed. Review the console output.'
        }
        always {
            echo 'Pipeline finished.'
        }
    }
}
