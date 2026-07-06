package com.example;

import io.helidon.webserver.WebServer;
import io.helidon.webserver.http.HttpRouting;

public class Main {
    public static void main(String[] args) {
        // サーバーを起動
        // FastMCPでいう mcp.run() に相当
        WebServer server = WebServer.builder()
                .port(8080)
                .routing(HttpRouting.builder()
                // MCPサーバーが自動的に登録される（アノテーション処理による）
                )
                .build()
                .start();

        System.out.println("MCP Server started at http://localhost:8080/mcp");
        System.out.println("Press Ctrl+C to stop");
    }
}