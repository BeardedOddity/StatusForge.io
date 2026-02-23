Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")

' Get the exact folder where this shortcut lives
currentFolder = fso.GetParentFolderName(WScript.ScriptFullName)

' Target the invisible Python runner inside your specific sandbox
pythonwPath = currentFolder & "\venv\Scripts\pythonw.exe"

' Target your specific script inside the Engine folder
scriptPath = currentFolder & "\Engine\presence.py"

' Command Windows to launch it with a 0 (Completely Hidden)
WshShell.Run """" & pythonwPath & """ """ & scriptPath & """", 0, False