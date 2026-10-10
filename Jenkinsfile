pipeline {
    agent any

    stages {
        stage('Checkout') { steps { checkout scm } }
        stage('Install dependencies') { steps { bat 'python -m pip install -r requirements.txt' } }
        stage('Run tests') { steps { bat 'python -m pytest -v' } }

        stage('Deploy to main') {
            when { branch 'main' }
            steps {
                bat '''
                    taskkill /F /IM python.exe >nul 2>&1
                    timeout /t 2 /nobreak >nul
                    start /B python app.py
                    timeout /t 3 /nobreak >nul
                    echo Приложение запущено
                '''
            }
        }
    }

    post {
        success { echo 'Сборка и тесты завершились успешно' }
        failure { echo 'Ошибка сборки или тестирования' }
    }
}