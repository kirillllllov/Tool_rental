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
            }
        }

        stage('Run tests') {
            steps {
                bat 'python -m pytest -v'
            }
        }

        stage('Deploy to main') {
            when {
                branch 'main'
            }
            steps {
                bat '''
                    taskkill /F /IM python.exe
                    start /B python app.py
                '''
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