param(
    [Parameter(Mandatory=$true)]
    [string]$Title,
    [string]$Body = "",
    [string]$Label = "",
    [string]$Milestone = ""
)

$cmd = "gh issue create --title `"$Title`" --body `"$Body`""
if ($Label) { $cmd += " --label `"$Label`"" }
if ($Milestone) { $cmd += " --milestone `"$Milestone`"" }

Invoke-Expression $cmd
