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
                bat 'nssm restart ToolRental'
                bat 'ping -n 6 127.0.0.1 >nul'
                bat 'curl -f -s -o nul http://127.0.0.1:5000/ || (echo Health-check FAILED & type service.err.log & exit /b 1)'
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