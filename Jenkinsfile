pipeline {
    agent any

    environment {
        DOCKER_CREDENTIALS_ID = 'docker-hub-credentials'
        IMAGE_NAME            = 'koptelovkir535363/tool-rental-backend'
        IMAGE_TAG             = "${env.BUILD_NUMBER}"
    }

    stages {
        stage('Checkout') {
            steps { checkout scm }
        }

        stage('Build Docker image') {
            steps {
                bat "docker build -t ${env.IMAGE_NAME}:${env.IMAGE_TAG} ."
            }
        }

        stage('Run tests') {
            steps {
                bat "docker run --rm ${env.IMAGE_NAME}:${env.IMAGE_TAG} python -m pytest -v"
            }
        }

        stage('Push to Docker Hub') {
            when {
                expression {
                    def b = env.GIT_BRANCH ?: env.BRANCH_NAME ?: ''
                    return b == 'main' || b == 'origin/main' || b == 'refs/heads/main'
                }
            }
            steps {
                script {
                    docker.withRegistry('https://registry.hub.docker.com', env.DOCKER_CREDENTIALS_ID) {
                        docker.image("${env.IMAGE_NAME}:${env.IMAGE_TAG}").push()
                    }
                }
            }
        }

        stage('Deploy to main') {
            when {
                expression {
                    def b = env.GIT_BRANCH ?: env.BRANCH_NAME ?: ''
                    return b == 'main' || b == 'origin/main' || b == 'refs/heads/main'
                }
            }
            steps {
                bat 'docker compose up -d'

                bat '''
                    echo Проверка доступности сайта через Nginx

                    powershell -NoProfile -ExecutionPolicy Bypass -Command "$ok = $false; for ($i = 0; $i -lt 15; $i++) { try { $r = Invoke-WebRequest -Uri 'http://127.0.0.1/' -UseBasicParsing -TimeoutSec 3; if ($r.StatusCode -eq 200) { $ok = $true; break } } catch {}; Start-Sleep -Seconds 2 }; if (-not $ok) { exit 1 }"

                    if errorlevel 1 (
                        echo ОШИБКА: сайт не отвечает.
                        docker compose ps
                        docker compose logs --tail=100
                        exit /b 1
                    )

                    echo Сайт успешно запущен: http://localhost
                '''
            }
        }
    }

    post {
        success { echo 'Сборка, тесты, push и деплой завершены успешно.' }
        failure { echo 'Ошибка на одном из этапов.' }
        always  { echo 'Pipeline завершён.' }
    }
}