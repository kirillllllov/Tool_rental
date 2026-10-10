pipeline {
    agent any

    environment {
        APP_URL = 'http://127.0.0.1:5000/'
    }

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
                echo 'Останавливаем старое приложение...'
                bat '''
                    taskkill /F /IM python.exe >nul 2>&1
                    ping -n 3 127.0.0.1 >nul
                '''

                echo 'Запускаем приложение через waitress...'
                bat '''
                    start "" /B cmd /c "waitress-serve --port=5000 app:app > app.log 2>&1"
                    ping -n 6 127.0.0.1 >nul
                '''

                echo 'Health-check...'
                bat '''
                    curl -f -s -o nul http://127.0.0.1:5000/
                    if errorlevel 1 (
                        echo === Health-check FAILED ===
                        echo --- app.log ---
                        type app.log
                        exit /b 1
                    )
                    echo Health-check OK
                '''
            }
        }
    }

    post {
        success {
            echo 'Сборка, тесты и деплой прошли успешно'
        }
        failure {
            echo 'Пайплайн упал — см. логи выше'
        }
        always {
            echo "Результат: ${currentBuild.currentResult}"
        }
    }
}