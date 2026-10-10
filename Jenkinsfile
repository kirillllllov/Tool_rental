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
                bat 'python -m pip install waitress'
            }
        }

        stage('Run tests') {
            steps {
                bat 'python -m pytest -v'
            }
        }

        stage('Deploy to main') {
            when {
                expression {
                    def b = env.GIT_BRANCH ?: env.BRANCH_NAME ?: ''
                    return b == 'main' || b == 'origin/main'
                }
            }
            steps {
                echo 'Ветка main: перезапускаем приложение'
                bat '''
                    taskkill /F /IM python.exe >nul 2>&1
                    timeout /t 2 /nobreak >nul
                    start "" cmd /c "waitress-serve --port=5000 app:app > app.log 2>&1"
                    timeout /t 5 /nobreak >nul
                    echo Проверяем, что приложение отвечает...
                    powershell -Command "(Invoke-WebRequest http://127.0.0.1:5000/ -UseBasicParsing).StatusCode"
                '''
            }
        }
    }

    post {
        success { echo 'Сборка и тесты завершились успешно' }
        failure { echo 'Ошибка сборки или тестирования' }
    }
}