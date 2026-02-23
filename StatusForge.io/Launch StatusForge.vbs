Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")

' Get the exact folder where this shortcut lives
currentFolder = fso.GetParentFolderName(WScript.ScriptFullName)

' Set the working directory so the installer knows where to build
WshShell.CurrentDirectory = currentFolder

' Target the invisible Python runner inside your specific sandbox
pythonwPath = currentFolder & "\venv\Scripts\pythonw.exe"

' Target your specific script inside the Engine folder
scriptPath = currentFolder & "\Engine\presence.py"

' --- THE AUTO-INSTALLER ---
' Check if the invisible Python runner is missing (meaning it's a first-time setup)
If Not fso.FileExists(pythonwPath) Then
    ' Pop open a visible terminal window to build the sandbox and install dependencies
    installCmd = "cmd.exe /c ""title StatusForge First-Time Setup && echo Forging the environment... Please wait. && python -m venv venv && call venv\Scripts\activate.bat && pip install -r requirements.txt && echo. && echo Setup complete! Booting engine... && timeout /t 3"""
    WshShell.Run installCmd, 1, True
End If
' --------------------------

' Command Windows to launch it with a 0 (Completely Hidden)
WshShell.Run """" & pythonwPath & """ """ & scriptPath & """", 0, False
