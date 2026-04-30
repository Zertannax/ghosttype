param(
    [Parameter(Mandatory=$true)]
    [string]$Title,
    [string]$Description = "",
    [string]$DueDate = ""
)

$repoInfo = gh repo view --json owner,name | ConvertFrom-Json
$owner = $repoInfo.owner.login
$repo = $repoInfo.name

$cmd = "gh api repos/$owner/$repo/milestones -X POST -f title=`"$Title`""
if ($Description) { $cmd += " -f description=`"$Description`"" }
if ($DueDate) { $cmd += " -f due_on=`"${DueDate}T00:00:00Z`"" }

Invoke-Expression $cmd
