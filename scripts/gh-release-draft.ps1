param(
    [Parameter(Mandatory=$true)]
    [string]$Tag,
    [string]$Title = "",
    [string]$Notes = ""
)

$releaseTitle = if ($Title) { $Title } else { $Tag }
gh release create $Tag --title "$releaseTitle" --notes "$Notes" --draft
