pipeline {
    agent any

    environment {
        DOCKER_CREDENTIALS_ID = 'docker-hub-credentials'         // ID из шага 2
        IMAGE_NAME            = 'koptelovkir535363/tool-rental'       // ваш образ
        IMAGE_TAG             = "${env.BUILD_NUMBER}"            // уникальный тег на каждую сборку
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build Docker image') {
            steps {
                // Собираем и тегируем образ сразу двумя тегами:
                // latest — для удобства, BUILD_NUMBER — для отката
                bat "docker build -t ${env.IMAGE_NAME}:${env.IMAGE_TAG} -t ${env.IMAGE_NAME}:latest ."
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
                        docker.image("${env.IMAGE_NAME}:latest").push()
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
                // Теперь поднимаем уже существующий образ с Docker Hub,
                // а не пересобираем локально — гарантирует, что на сервере
                // работает именно то, что запушено
                bat "docker compose pull app"
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
        success { echo 'Сборка, тесты и деплой завершены успешно.' }
        failure { echo 'Ошибка сборки, тестирования или развертывания.' }
        always  { echo 'Pipeline завершён.' }
    }
}