
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
                bat 'python --version'
                bat 'python -m pip install -r requirements.txt'
                bat 'python -m pip install pytest'
            }
        }

        stage('Run tests') {
            steps {
                bat 'python -m pytest -v'
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