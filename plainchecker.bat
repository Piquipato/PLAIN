@echo off

IF "%PLAIN_ENV%"=="" (
    SET "PLAIN_ENV=C:\Users\geneticalapaz\AppData\Local\anaconda3\envs\webdriver"
)

CALL conda activate "%PLAIN_ENV%"

python -m plainchecker %*