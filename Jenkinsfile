pipeline {
    agent any

    environment {
        DOCKER_HUB_USER = 'koptelovkir535363'
        IMAGE_NAME      = 'tool-rental-app'
        DOCKER_CREDS_ID = 'docker-hub-credentials'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Run tests') {
            steps {
                bat 'docker compose run --rm app python -m pytest -v'
            }
        }

        stage('Build Docker image') {
            steps {
                bat 'docker compose build app'

                // Тегируем под Docker Hub: уникальный тег сборки + latest
                bat "docker tag ${DOCKER_HUB_USER}/${IMAGE_NAME}:latest ${DOCKER_HUB_USER}/${IMAGE_NAME}:${env.BUILD_NUMBER}"
            }
        }

        stage('Push to Docker Hub') {
            steps {
                script {
                    withDockerRegistry(credentialsId: DOCKER_CREDS_ID, url: '') {
                        bat "docker push ${DOCKER_HUB_USER}/${IMAGE_NAME}:${env.BUILD_NUMBER}"
                        bat "docker push ${DOCKER_HUB_USER}/${IMAGE_NAME}:latest"
                    }
                }
            }
        }

        stage('Deploy to main') {
            when {
                expression {
                    def b = env.GIT_BRANCH ?: env.BRANCH_NAME ?: ''
                    return b == 'main' ||
                           b == 'origin/main' ||
                           b == 'refs/heads/main'
                }
            }

            steps {
                bat 'docker compose up -d --build'

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
        success {
            echo 'Тесты, сборка и пуш в Docker Hub завершены успешно. Если собиралась main, приложение развернуто.'
        }
        failure {
            echo 'Ошибка тестирования, сборки, пуша или развертывания.'
        }
        always {
            echo 'Pipeline завершён.'
        }
    }
}