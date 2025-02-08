Option Explicit
Dim objFSO, objShell, objFile, jsonFile, scriptPath, rootPath, jsonData, aliasCommand, profilePath

' Create File System Object and Shell Object
Set objFSO = CreateObject("Scripting.FileSystemObject")
Set objShell = CreateObject("WScript.Shell")

' Get the directory where this VBScript is located
scriptPath = WScript.ScriptFullName
rootPath = objFSO.GetParentFolderName(scriptPath)

' Define JSON file path
jsonFile = rootPath & "\config.json"

' Check if config.json exists
If objFSO.FileExists(jsonFile) Then
    ' Read the existing JSON file
    Set objFile = objFSO.OpenTextFile(jsonFile, 1) ' Read mode
    jsonData = objFile.ReadAll
    objFile.Close
Else
    ' Save the rootPath in config.json
    Set objFile = objFSO.CreateTextFile(jsonFile, True)
    objFile.WriteLine "{""rootPath"": """ & rootPath & """}"
    objFile.Close
End If

' Check if Python is installed
Dim pythonCheck
pythonCheck = objShell.Run("python --version", 0, True)

If pythonCheck <> 0 Then
    WScript.StdOut.WriteLine "Python is not installed or not in the system PATH. Please install Python first."
    WScript.Quit
End If

' Run the Python script in a new command prompt window
objShell.Run "cmd.exe /k python """ & rootPath & "\main.py"" welcome", 1, False

