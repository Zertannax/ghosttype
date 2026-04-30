param(
    [Parameter(Mandatory=$true)]
    [string]$Title,
    [string]$Body = "",
    [string]$Base = "main"
)

gh pr create --title "$Title" --body "$Body" --base "$Base"
