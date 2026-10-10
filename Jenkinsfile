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
                expression {
                    def b = env.GIT_BRANCH ?: env.BRANCH_NAME ?: ''
                    return b == 'main' || b == 'origin/main'
                }
            }
            steps {
                withEnv(['BUILD_ID=dontKillMe']) {
                    bat '''
                        taskkill /F /IM python.exe >nul 2>&1
                        timeout /t 2 /nobreak >nul
                        ping -n 3 127.0.0.1 >nul
                        start "ToolRental" cmd /c "python app.py > app.log 2>&1"
                        timeout /t 2 /nobreak >nul
                        ping -n 4 127.0.0.1 >nul
                    '''
                }
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