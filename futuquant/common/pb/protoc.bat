cd /d %~dp0
protoc.exe --python_out=./ GetGlobalState.proto
protoc.exe --python_out=./ Qot_Common.proto

