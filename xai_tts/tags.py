INLINE_TAGS = {
    "Pauses": ["pause", "long-pause", "hum-tune"],
    "Laughter & Crying": ["laugh", "chuckle", "giggle", "cry"],
    "Mouth Sounds": ["tsk", "tongue-click", "lip-smack"],
    "Breathing": ["breath", "inhale", "exhale", "sigh"]
}

WRAP_TAGS = {
    "Volume & Intensity": ["soft", "whisper", "loud", "build-intensity", "decrease-intensity"],
    "Pitch & Speed": ["higher-pitch", "lower-pitch", "slow", "fast"],
    "Vocal Style": ["sing-song", "singing", "emphasis"]
}

def get_all_tags():
    return {
        "inline": INLINE_TAGS,
        "wrap": WRAP_TAGS
    }
