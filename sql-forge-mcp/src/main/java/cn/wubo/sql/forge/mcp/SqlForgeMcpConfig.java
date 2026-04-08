package cn.wubo.sql.forge.mcp;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.client.RestClient;

@Configuration
public class SqlForgeMcpConfig {

    @Bean
    public RestClient restClient(@Value("${sql-forge.api.url:http://localhost:8081}") String apiBaseUrl) {
        return RestClient.builder()
                .baseUrl(apiBaseUrl)
                .build();
    }

}
