# Edge浏览器远程调试诊断脚本
# 在Windows PowerShell中运行此脚本

Write-Host "🔍 Edge浏览器远程调试诊断" -ForegroundColor Cyan
Write-Host "=" * 50 -ForegroundColor Cyan

# 1. 检查Edge进程
Write-Host "`n📋 检查Edge进程..." -ForegroundColor Yellow
$edgeProcesses = Get-Process -Name "msedge" -ErrorAction SilentlyContinue
if ($edgeProcesses) {
    Write-Host "✅ 找到 $($edgeProcesses.Count) 个Edge进程:" -ForegroundColor Green
    foreach ($process in $edgeProcesses) {
        Write-Host "   PID: $($process.Id), 内存: $([math]::Round($process.WorkingSet64/1MB, 2))MB" -ForegroundColor White
        
        # 尝试获取命令行参数
        try {
            $commandLine = (Get-WmiObject Win32_Process -Filter "ProcessId = $($process.Id)").CommandLine
            if ($commandLine -like "*remote-debugging-port*") {
                Write-Host "   ✅ 命令行包含远程调试参数" -ForegroundColor Green
                Write-Host "   参数: $commandLine" -ForegroundColor Gray
            } else {
                Write-Host "   ❌ 命令行不包含远程调试参数" -ForegroundColor Red
                Write-Host "   参数: $commandLine" -ForegroundColor Gray
            }
        } catch {
            Write-Host "   ⚠️ 无法获取命令行参数" -ForegroundColor Yellow
        }
    }
} else {
    Write-Host "❌ 没有找到Edge进程" -ForegroundColor Red
}

# 2. 检查端口监听
Write-Host "`n👂 检查端口9222监听状态..." -ForegroundColor Yellow
$portInfo = netstat -an | Select-String ":9222"
if ($portInfo) {
    Write-Host "✅ 端口9222正在监听:" -ForegroundColor Green
    $portInfo | ForEach-Object { Write-Host "   $_" -ForegroundColor White }
} else {
    Write-Host "❌ 端口9222没有监听" -ForegroundColor Red
}

# 3. 检查防火墙规则
Write-Host "`n🛡️ 检查防火墙状态..." -ForegroundColor Yellow
try {
    $firewallProfile = Get-NetFirewallProfile -Profile Domain,Public,Private
    foreach ($profile in $firewallProfile) {
        Write-Host "   $($profile.Name): $($profile.Enabled)" -ForegroundColor White
    }
    
    # 检查是否有阻止9222端口的规则
    $firewallRules = Get-NetFirewallRule | Where-Object { $_.DisplayName -like "*9222*" -or $_.DisplayName -like "*Edge*" }
    if ($firewallRules) {
        Write-Host "   找到相关防火墙规则:" -ForegroundColor Yellow
        $firewallRules | ForEach-Object { Write-Host "     $($_.DisplayName): $($_.Action)" -ForegroundColor White }
    } else {
        Write-Host "   没有找到相关防火墙规则" -ForegroundColor White
    }
} catch {
    Write-Host "   ⚠️ 无法检查防火墙状态: $($_.Exception.Message)" -ForegroundColor Yellow
}

# 4. 测试本地连接
Write-Host "`n🔌 测试本地连接..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:9222/json/version" -TimeoutSec 5 -ErrorAction Stop
    Write-Host "✅ 本地HTTP请求成功!" -ForegroundColor Green
    Write-Host "   状态码: $($response.StatusCode)" -ForegroundColor White
    Write-Host "   响应长度: $($response.Content.Length) 字符" -ForegroundColor White
    Write-Host "   响应内容: $($response.Content)" -ForegroundColor Gray
} catch {
    Write-Host "❌ 本地HTTP请求失败: $($_.Exception.Message)" -ForegroundColor Red
}

# 5. 测试TCP连接
Write-Host "`n🔗 测试TCP连接..." -ForegroundColor Yellow
try {
    $tcpClient = New-Object System.Net.Sockets.TcpClient
    $tcpClient.ReceiveTimeout = 5000
    $tcpClient.SendTimeout = 5000
    $tcpClient.Connect("localhost", 9222)
    
    if ($tcpClient.Connected) {
        Write-Host "✅ TCP连接成功" -ForegroundColor Green
        
        # 尝试发送HTTP请求
        $stream = $tcpClient.GetStream()
        $request = "GET /json/version HTTP/1.1`r`nHost: localhost:9222`r`nConnection: close`r`n`r`n"
        $requestBytes = [System.Text.Encoding]::UTF8.GetBytes($request)
        
        $stream.Write($requestBytes, 0, $requestBytes.Length)
        $stream.Flush()
        
        # 读取响应
        $buffer = New-Object byte[] 4096
        $response = ""
        $totalBytes = 0
        
        $timeout = [DateTime]::Now.AddSeconds(5)
        while ([DateTime]::Now -lt $timeout) {
            if ($stream.DataAvailable) {
                $bytesRead = $stream.Read($buffer, 0, $buffer.Length)
                if ($bytesRead -gt 0) {
                    $totalBytes += $bytesRead
                    $response += [System.Text.Encoding]::UTF8.GetString($buffer, 0, $bytesRead)
                } else {
                    break
                }
            } else {
                Start-Sleep -Milliseconds 100
            }
        }
        
        if ($totalBytes -gt 0) {
            Write-Host "✅ 收到HTTP响应: $totalBytes 字节" -ForegroundColor Green
            Write-Host "   响应内容:" -ForegroundColor Gray
            Write-Host $response -ForegroundColor Gray
        } else {
            Write-Host "❌ TCP连接成功但没有HTTP响应" -ForegroundColor Red
        }
        
        $tcpClient.Close()
    } else {
        Write-Host "❌ TCP连接失败" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ TCP连接错误: $($_.Exception.Message)" -ForegroundColor Red
}

# 6. 检查Edge用户数据目录
Write-Host "`n📁 检查Edge用户数据目录..." -ForegroundColor Yellow
$edgeDataPath = "$env:LOCALAPPDATA\Microsoft\Edge\User Data"
if (Test-Path $edgeDataPath) {
    Write-Host "✅ Edge用户数据目录存在: $edgeDataPath" -ForegroundColor Green
    
    # 检查是否有锁文件
    $lockFiles = Get-ChildItem -Path $edgeDataPath -Name "*lock*" -Recurse -ErrorAction SilentlyContinue
    if ($lockFiles) {
        Write-Host "   找到锁文件:" -ForegroundColor Yellow
        $lockFiles | ForEach-Object { Write-Host "     $_" -ForegroundColor White }
    }
} else {
    Write-Host "❌ Edge用户数据目录不存在" -ForegroundColor Red
}

# 7. 建议的解决方案
Write-Host "`n💡 建议的解决方案:" -ForegroundColor Cyan
Write-Host "1. 完全关闭所有Edge进程:" -ForegroundColor White
Write-Host "   Get-Process -Name 'msedge' | Stop-Process -Force" -ForegroundColor Gray

Write-Host "`n2. 使用完整参数重新启动Edge:" -ForegroundColor White
Write-Host "   & 'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe' --remote-debugging-port=9222 --remote-allow-origins=* --disable-web-security --user-data-dir=C:\temp\edge-debug" -ForegroundColor Gray

Write-Host "`n3. 或者尝试使用Chrome:" -ForegroundColor White
Write-Host "   & 'C:\Program Files\Google\Chrome\Application\chrome.exe' --remote-debugging-port=9222 --remote-allow-origins=*" -ForegroundColor Gray

Write-Host "`n4. 检查Windows Defender或其他安全软件是否阻止了连接" -ForegroundColor White

Write-Host "`n=" * 50 -ForegroundColor Cyan
Write-Host "🔍 诊断完成" -ForegroundColor Cyan
