
pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                checkout scm
                echo 'Исходный код получен из GitHub'
            }
        }

        stage('Install dependencies') {
            steps {
                sh 'python3 --version'
                sh 'python3 -m pip install -r requirements.txt'
                sh 'python3 -m pip install pytest'
            }
        }

        stage('Run tests') {
            steps {
                sh 'python3 -m pytest -v'
            }
        }
    }

    post {
        success {
            echo 'Сборка и тесты завершились успешно'
        }
        failure {
            echo 'Ошибка сборки или тестирования'
        }
    }
}