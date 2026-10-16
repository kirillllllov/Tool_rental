stage('Deploy to main') {
    when {
        expression {
            def b = env.GIT_BRANCH ?: env.BRANCH_NAME ?: ''
            return b == 'main' || b == 'origin/main'
        }
    }
    steps {
        powershell '''
            Write-Host "=== Остановка предыдущего экземпляра приложения ==="
            Get-NetTCPConnection -LocalPort 5000 -State Listen -ErrorAction SilentlyContinue |
                ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }
            Start-Sleep -Seconds 2

            Write-Host "=== Запуск приложения ==="
            if (-not (Test-Path logs)) { New-Item -ItemType Directory -Path logs | Out-Null }

            Start-Process -FilePath "python" -ArgumentList "app.py" `
                -RedirectStandardOutput "app.log" -RedirectStandardError "app.err.log" -NoNewWindow

            Start-Sleep -Seconds 5

            try {
                $response = Invoke-WebRequest -Uri 'http://127.0.0.1:5000/' -UseBasicParsing -TimeoutSec 10
                if ($response.StatusCode -ne 200) { throw "Bad status: $($response.StatusCode)" }
            } catch {
                Write-Host "ОШИБКА: приложение не ответило на запрос."
                Get-Content app.log -ErrorAction SilentlyContinue
                Get-Content app.err.log -ErrorAction SilentlyContinue
                exit 1
            }

            Write-Host "=== Приложение успешно запущено ==="
            Write-Host "Адрес сайта: http://127.0.0.1:5000"
        '''
    }
}