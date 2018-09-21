@echo off
set workdir=%~dp0
set workdir=%workdir:~0,-1%
echo current work dir: %workdir%

python  "%workdir%\runCtaTrading.py"


