user  nginx;
worker_processes  1;

error_log  /var/log/nginx/error.log warn;
pid        /var/run/nginx.pid;


events
{
    worker_connections  1024;
}


http
{
    include             /etc/nginx/mime.types;
    default_type        application/octet-stream;
    log_format  main    '$remote_addr - $remote_user [$time_local] "$request" '
                        '$status $body_bytes_sent "$http_referer" '
                        '"$http_user_agent" "$http_x_forwarded_for"';
    access_log          /var/log/nginx/access.log  main;
    sendfile            on;
    keepalive_timeout   65;
    {% if ssl is sameas true %}
    server
    {
        listen          80;
        server_name     {{ server_name }};
        # HTTPS redirect
        return 301 https://$host$request_uri;
    }
    {% endif %}

    server
    {
        {% if ssl is sameas true %}
        listen              443 ssl;
        ssl_certificate     {{ sslcertfile }};
        ssl_certificate_key {{ sslkeyfile }};
        {% else %}
        listen              80;
        {% endif %}
        server_name         {{ server_name }};

        # reverse proxy configuration
        {% for location in locations %}
            location {{ location.location }}
            {
                resolver                127.0.0.11;
                proxy_set_header        Host $host;
                proxy_set_header        X-Real-IP $remote_addr;
                proxy_set_header        X-Forwarded-For $proxy_add_x_forwarded_for;
                proxy_set_header        X-Forwarded-Proto $scheme;
                set $upstream_host {{ location.url }};
                {% if location.trailing_slash %}
                rewrite ^{{ location.location }}(.*) /$1 break;
                {% endif %}
                proxy_pass $upstream_host;
            }
        {% endfor %}

    }

}
