package com.example;

import io.helidon.mcp.declarative.Mcp;
import io.helidon.mcp.server.McpToolContent;
import io.helidon.mcp.server.McpToolContents;
import java.util.List;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;

// これがMCPサーバーの本体
// FastMCPでいう mcp = FastMCP("hello-mcp") に相当
@Mcp.Path("/mcp")
@Mcp.Server("hello-mcp")
public class HelloMcpServer {

    // 最もシンプルなツール
    // FastMCPでいう @mcp.tool def greet(name: str) -> str
    @Mcp.Tool("Greet someone by name")
    public List<McpToolContent> greet(String name) {
        String message = "Hello, " + name + "!";
        return List.of(McpToolContents.textContent(message));
    }

    // 引数なしのツール
    @Mcp.Tool("Get current time")
    public List<McpToolContent> getCurrentTime() {
        String time = LocalDateTime.now()
                .format(DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss"));
        return List.of(McpToolContents.textContent("Current time: " + time));
    }

    // 複数引数のツール（型を明示）
    @Mcp.Tool("Add two numbers")
    public List<McpToolContent> add(int a, int b) {
        int result = a + b;
        return List.of(McpToolContents.textContent(
                String.format("%d + %d = %d", a, b, result)));
    }
}
