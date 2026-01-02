@echo off
REM docker run --rm -v "%~dp0:/local" openapitools/openapi-generator-cli:v7.10.0 %*
docker run --rm -v "%~dp0:/local" openapitools/openapi-generator-cli:v7.10.0 generate -c /local/fastapi-openapi-generator-config.yaml

docker run --rm -v "%~dp0:/local" openapitools/openapi-generator-cli:v7.10.0 generate -c /local/typescript-openapi-generator-config.yaml
robocopy %~dp0\typescript\ %~dp0\..\gvt-typescript-client\ /E /MOVE
