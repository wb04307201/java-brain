package cn.wubo.sql.forge.mcp;

import org.springframework.ai.tool.annotation.Tool;
import org.springframework.ai.tool.annotation.ToolParam;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestClient;

import java.util.Map;
import java.util.UUID;

@Service
public class SqlForgeService {

    private final String apiBaseUrl;
    private final RestClient restClient;

    public SqlForgeService(@Value("${sql-forge.api.url:http://localhost:8081}") String apiBaseUrl, RestClient restClient) {
        this.apiBaseUrl = apiBaseUrl;
        this.restClient = restClient;
    }

    @Tool(description = "获取数据库信息")
    private String getMetaDataDatabase() {
        return restClient.get()
                .uri("/sql/forge/api/database/getMetaDataDatabase")
                .accept(MediaType.APPLICATION_JSON)
                .retrieve()
                .body(String.class);
    }


    @Tool(description = "获取数据库表信息")
    private String sqlForgeMetaDataTables() {
        return restClient.get()
                .uri("/sql/forge/api/database/metaDataTables")
                .accept(MediaType.APPLICATION_JSON)
                .retrieve()
                .body(String.class);
    }

    @Tool(description = "执行SQL查询并返回结果集")
    public String executeSQL(@ToolParam(description = "要执行的SQL语句") String sql) {
        return restClient.post()
                .uri("/sql/forge/api/database/execute")
                .contentType(MediaType.APPLICATION_JSON)
                .body(Map.of("sql", sql))
                .retrieve()
                .body(String.class);
    }

    @Tool(description = "保存页面JSON配置模板")
    public String amisTemplateSave(@ToolParam(description = "模板id") String id, @ToolParam(description = "JSON配置模板") String context) {
        return restClient.put()
                .uri("/sql/forge/api/template/amis")
                .contentType(MediaType.APPLICATION_JSON)
                .body(Map.of("id", id, "context", context))
                .retrieve()
                .body(String.class);
    }


    public static void main(String[] args) {
        RestClient restClient = RestClient.builder().baseUrl("http://localhost:8081")
                .defaultHeader("Content-Type", "application/json")
                .defaultHeader("Accept", "application/json")
                .build();

        SqlForgeService sqlForgeService = new SqlForgeService("http://localhost:8081", restClient);

        String result = sqlForgeService.getMetaDataDatabase();
        System.out.println(result);

        String tables = sqlForgeService.sqlForgeMetaDataTables();
        System.out.println(tables);

        String executeSQL = sqlForgeService.executeSQL("select * from users");
        System.out.println(executeSQL);

        String save = sqlForgeService.amisTemplateSave(UUID.randomUUID().toString(), "{\"type\": \"page\", \"title\": \"页面标题\", \"body\": [{\"type\": \"input-text\", \"label\": \"用户名\", \"name\": \"username\"}]}");
        System.out.println(save);
    }


}
