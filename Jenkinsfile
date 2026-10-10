pipeline {
    agent any

    stages {
        stage('Checkout') { steps { checkout scm } }
        stage('Install dependencies') { steps { bat 'python -m pip install -r requirements.txt' } }
        stage('Run tests') { steps { bat 'python -m pytest -v' } }

        stage('Deploy to main') {
            when {
                expression {
                    def b = env.GIT_BRANCH ?: env.BRANCH_NAME ?: ''
                    return b == 'main' || b == 'origin/main'
                }
            }
            steps {
                bat '''
                    taskkill /F /IM python.exe >nul 2>&1
                    powershell -NoProfile -Command "Start-Sleep -Seconds 2"
                    start "" cmd /c "python app.py > app.log 2>&1"
                    powershell -NoProfile -Command "Start-Sleep -Seconds 3"
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