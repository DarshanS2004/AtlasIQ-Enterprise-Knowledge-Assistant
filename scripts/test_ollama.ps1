$body = @{
    model = "llama3.2"
    messages = @(
        @{
            role = "user"
            content = "Reply with exactly the word ok."
        }
    )
    stream = $false
} | ConvertTo-Json -Depth 5

Invoke-RestMethod -Uri "http://localhost:11434/api/chat" -Method Post -ContentType "application/json" -Body $body | ConvertTo-Json -Depth 6
