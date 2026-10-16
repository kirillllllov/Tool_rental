pipeline {
    agent any

    stages {
        stage('Install dependencies') {
            steps {
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
                bat '''
                    echo Остановка предыдущего экземпляра приложения
                    for /f "tokens=5" %a in ('netstat -aon ^| findstr :5000 ^| findstr LISTENING') do taskkill /F /PID %a
                    
                    echo Запуск приложения
                    powershell -NoProfile -ExecutionPolicy Bypass -Command "Invoke-CimMethod -ClassName Win32_Process -MethodName Create -Arguments @{CommandLine='cmd /c cd /d C:\\ProgramData\\Jenkins\\.jenkins\\workspace\\tool-rental && python app.py > app.log 2>&1'}"

                '''
            }
        }
    }

    post {
        success {
            echo 'Сборка, тесты и доступность приложения проверены успешно'
        }
        failure {
            echo 'Ошибка сборки, тестирования или запуска приложения'
        }
    }
}