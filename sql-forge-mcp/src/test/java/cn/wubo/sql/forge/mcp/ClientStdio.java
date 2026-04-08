/*
 * Copyright 2024 - 2024 the original author or authors.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 * https://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
package cn.wubo.sql.forge.mcp;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import io.modelcontextprotocol.client.McpClient;
import io.modelcontextprotocol.client.transport.ServerParameters;
import io.modelcontextprotocol.client.transport.StdioClientTransport;
import io.modelcontextprotocol.json.McpJsonMapper;
import io.modelcontextprotocol.spec.McpSchema.CallToolRequest;
import io.modelcontextprotocol.spec.McpSchema.CallToolResult;
import io.modelcontextprotocol.spec.McpSchema.ListToolsResult;

import java.nio.file.Paths;
import java.util.Map;
import java.util.UUID;

/**
 * With stdio transport, the MCP server is automatically started by the client. But you
 * have to build the server jar first:
 *
 * <pre>
 * ./mvnw clean install -DskipTests
 * </pre>
 */
public class ClientStdio {

    public static void main(String[] args) throws JsonProcessingException {
        String jarPath = Paths.get("target",
                "sql-forge-mcp-0.0.1-SNAPSHOT.jar").toAbsolutePath().toString();

        var stdioParams = ServerParameters.builder("java")
                .args("-Dfile.encoding=UTF-8", "-jar", jarPath)
                .build();

        var transport = new StdioClientTransport(stdioParams, McpJsonMapper.createDefault());
        var client = McpClient.sync(transport)
                .build();

        client.initialize();

        // List and demonstrate tools
        ListToolsResult toolsList = client.listTools();
        System.out.println("Available Tools = " + toolsList);

        CallToolResult getMetaDataDatabaseResult = client.callTool(new CallToolRequest("getMetaDataDatabase", null));
        System.out.println("getMetaDataDatabaseResult = " + getMetaDataDatabaseResult.content());

        CallToolResult sqlForgeMetaDataTablesResult = client.callTool(new CallToolRequest("sqlForgeMetaDataTables", null));
        System.out.println("sqlForgeMetaDataTablesResult = " + sqlForgeMetaDataTablesResult.content());

        CallToolResult executeSQLResult = client.callTool(new CallToolRequest("executeSQL", Map.of("sql", "select * from users")));
        System.out.println("executeSQLResult = " + executeSQLResult.content());


        ObjectMapper objectMapper = new ObjectMapper();
        String json = objectMapper.writeValueAsString(Map.of(
                "type", "page",
                "title", "页面标题"));

        CallToolResult amisTemplateSaveResult = client.callTool(new CallToolRequest("amisTemplateSave", Map.of("id", UUID.randomUUID().toString(), "context", json)));
        System.out.println("amisTemplateSaveResult = " + amisTemplateSaveResult.content());

        client.closeGracefully();
    }

}
