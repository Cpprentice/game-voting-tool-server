@echo off
REM docker run --rm -v "%~dp0:/local" openapitools/openapi-generator-cli:v7.10.0 %*
docker run --rm -v "%~dp0:/local" openapitools/openapi-generator-cli:v7.10.0 generate -c /local/fastapi-openapi-generator-config.yaml
