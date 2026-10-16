pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

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
            echo === Остановка предыдущего экземпляра приложения ===
            powershell -NoProfile -ExecutionPolicy Bypass -Command "$connections = Get-NetTCPConnection -LocalPort 5000 -State Listen -ErrorAction SilentlyContinue; $connections | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }"
            powershell -NoProfile -Command "Start-Sleep -Seconds 2"

            echo === Запуск приложения ===
            if not exist logs mkdir logs

            powershell -NoProfile -ExecutionPolicy Bypass -Command "Invoke-CimMethod -ClassName Win32_Process -MethodName Create -Arguments @{CommandLine='cmd /c cd /d C:\\ProgramData\\Jenkins\\.jenkins\\workspace\\tool-rental && python app.py > app.log 2>&1'}"

            powershell -NoProfile -Command "Start-Sleep -Seconds 5"

            powershell -NoProfile -ExecutionPolicy Bypass -Command "$response = Invoke-WebRequest -Uri 'http://127.0.0.1:5000/' -UseBasicParsing -TimeoutSec 10; if ($response.StatusCode -ne 200) { exit 1 }"

            if errorlevel 1 (
                echo ОШИБКА: приложение не ответило на запрос.
                type app.log
                exit /b 1
            )

            echo === Приложение успешно запущено ===
            echo Адрес сайта: http://127.0.0.1:5000
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