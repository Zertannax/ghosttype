"""Creative writing AI patterns — fiction, storytelling, descriptive prose.

These detect the way modern LLMs write fiction: dense purple prose, told-not-shown
emotions, signature opening clichés, overworked metaphors, and the recurring
"his/her [body part] [verbed]" sentence shape that AI defaults to when describing
characters.

Every regex assumes word boundaries — bare nouns like "shadow" or "whisper" are
ubiquitous in human prose, so each pattern requires multi-word context.
"""

PATTERNS = [
    {
        "id": "CR-01",
        "category": "creative_opener",
        "regex": r"\bonce upon a time\b|\bin a world where\b|\blittle did (?:she|he|they) know\b|\bit was a (?:dark|cold|quiet) (?:and|night|morning)\b",
        "severity": 0.7,
        "description": "Cliché story opener (LLMs default to these when prompted for fiction)",
    },
    {
        "id": "CR-02",
        "category": "creative_purple_prose",
        "regex": r"\bcerulean (?:sky|eyes|gaze)\b|\bemerald (?:gaze|forest|eyes)\b|\bobsidian (?:hair|gaze|night)\b|\bcrimson (?:lips|tide|sky)\b",
        "severity": 0.8,
        "description": "Purple-prose colour adjectives (signature AI fiction tell)",
    },
    {
        "id": "CR-03",
        "category": "creative_told_emotion",
        "regex": r"\b(?:she|he|they) felt a (?:wave|surge|pang|rush) of\b|\ba (?:wave|surge|pang) of (?:emotion|sadness|joy|fear|relief)\b",
        "severity": 0.7,
        "description": "Told-not-shown emotion (AI tells emotions instead of dramatising)",
    },
    {
        "id": "CR-04",
        "category": "creative_body_action",
        "regex": r"\b(?:his|her|their) (?:eyes|heart|breath|chest) (?:caught|hitched|skipped|tightened|fluttered)\b|\bsuck(?:ed)? in a (?:sharp|quick) breath\b",
        "severity": 0.6,
        "description": "Generic body-reaction beat (AI fallback for showing reaction)",
    },
    {
        "id": "CR-05",
        "category": "creative_metaphor_overuse",
        "regex": r"\blike (?:a|an) (?:ancient|gentle|silent|distant|forgotten) \w+\b|\bas if the (?:world|sky|air|silence) (?:itself )?(?:had |were )?\w+\b",
        "severity": 0.5,
        "description": "Generic literary metaphor scaffolding (often empty)",
    },
    {
        "id": "CR-06",
        "category": "creative_atmosphere",
        "regex": r"\b(?:an?|the) (?:eerie|unsettling|deafening) silence\b|\bthe air (?:hung|grew) (?:thick|heavy|still)\b|\btime seemed to (?:stand still|slow|stop)\b",
        "severity": 0.6,
        "description": "Stock atmosphere line (AI fiction filler)",
    },
    {
        "id": "CR-07",
        "category": "creative_dialogue_tag",
        "regex": r"\b(?:she|he|they) (?:breathed|whispered|murmured),?\s+(?:softly|quietly|barely)\b|\bvoice (?:barely )?above a whisper\b",
        "severity": 0.6,
        "description": "Adverbial 'whispered softly' dialogue tag (writing-school anti-pattern)",
    },
    {
        "id": "CR-08",
        "category": "creative_eyes_meeting",
        "regex": r"\btheir eyes (?:met|locked|connected)\b|\bgazes (?:met|locked|held)\b|\beyes (?:burned|smouldered) into\b",
        "severity": 0.6,
        "description": "Romantic/dramatic eye-contact cliché",
    },
    {
        "id": "CR-09",
        "category": "creative_setting_aesthetic",
        "regex": r"\bbathed in (?:golden|moonlit|silver) light\b|\bdrenched in (?:moonlight|sunlight|shadow)\b|\bcaressed by the (?:wind|breeze|sun)\b",
        "severity": 0.7,
        "description": "AI-generated landscape-porn descriptor",
    },
    {
        "id": "CR-10",
        "category": "creative_revelation",
        "regex": r"\bin that (?:moment|instant), (?:she|he|they) (?:knew|realised|realized|understood)\b|\bit was then that\b|\beverything (?:changed|shifted) in an instant\b",
        "severity": 0.7,
        "description": "Cheap revelation transition (AI fiction climax filler)",
    },
    {
        "id": "CR-11",
        "category": "creative_narration_telling",
        "regex": r"\b(?:she|he|they) couldn'?t help but\b|\b(?:she|he|they) found (?:her|him|them)self\b|\b(?:she|he|they) was no stranger to\b",
        "severity": 0.6,
        "description": "Hedged-narration formula (told-not-shown with author intrusion)",
    },
    {
        "id": "CR-12",
        "category": "creative_internal_monologue",
        "regex": r"\b(?:thoughts|memories) (?:swirled|raced|flooded)\b|\b(?:her|his|their) mind (?:raced|reeled|spun)\b|\ba thousand thoughts\b",
        "severity": 0.6,
        "description": "Generic internal-monologue beat",
    },
    {
        "id": "CR-13",
        "category": "creative_sensory_combo",
        "regex": r"\bthe (?:scent|aroma) of \w+ (?:filled|hung in|wafted through)\b|\bthe taste of \w+ (?:lingered|coated|filled)\b",
        "severity": 0.5,
        "description": "Sensory-detail formula (AI default for 'show, don't tell')",
    },
    {
        "id": "CR-14",
        "category": "creative_resolution",
        "regex": r"\band so,? (?:the|her|his|their) (?:journey|story|tale) (?:began|continued|came to an end)\b|\band that was (?:the|how it) (?:end|all began)\b",
        "severity": 0.7,
        "description": "Storybook ending cliché",
    },
    {
        "id": "CR-15",
        "category": "creative_ai_tell",
        "regex": r"\bshiver \w+ down (?:her|his|their) spine\b|\bgoosebumps (?:crawled|prickled|rose)\b|\bblood ran cold\b|\bheart pounded in (?:her|his|their) chest\b",
        "severity": 0.7,
        "description": "Body-horror cliché bundle (AI fiction's go-to fear/excitement tells)",
    },
]
