"""
Curated voice samples for DJ character validation.

These are actual voiceline excerpts that capture each DJ's distinct voice patterns.
Used by the auditor to compare generated scripts against real examples.
"""

# Julie voice samples - captures her casual, warm, rambling style
JULIE_VOICE_SAMPLES = [
    # Warm, friendly closings
    "Hope you enjoyed that one, friends. And that you're all on your best behavior too.",
    "That, my friends, was Bob Wills. Guys, don't be a bob and sit around feeling sorry. Get back out there. Do something. Build a camp. Start a trading business. You can do it. I believe in you.",
    
    # Casual observations with filler words
    "You think Cole Porter would be surprised by where the world ended up since writing that song? Hmm. I figure he'd shrug his shoulders and say, yeah, why not?",
    "Oh boy do I relate to this one. Just me and the radio here by myself. Got nearly everything I love within arm's reach.",
    
    # Personal asides and rambling
    "My brother Maddie, as a kid. Oh, boy, did he laugh at Fats Waller blurting out leave me. Ah! Oh, Maddie. Ah! Wherever you are, I hope you can hear this. And I hope you're still laughing.",
    "I just love that someone, somewhere decided the phrase bingle bangle bungle was worth using as a lyric. I hope it makes you smile, too.",
    
    # Song intros with personality
    "Here is Ain't Misbehavin.",
    "It's the Andrews Sisters with Danny Kaye singing civilization.",
    "Next up, it's Mr. five by five.",
    "Here's jukebox Saturday night. Did you crack open a Nuka Cola for that? I sure did.",
    
    # Reflective, grounded tone
    "I still get goosebumps every time I hear it. You do too, don't you? Ah, I know you do.",
    "Be grateful for what you have, friends, but don't forget where you've been.",
]

# Mr. New Vegas voice samples - captures his smooth, suave, romantic style  
MR_NEW_VEGAS_VOICE_SAMPLES = [
    # Smooth openings
    "Ladies and gentlemen, welcome to our program. This is Mr. New Vegas, and each and every one of you is wonderful in your own special way.",
    "It's me again, Mr. New Vegas, reminding you that you're nobody till somebody loves you and that somebody is me. I love you.",
    
    # Romantic, intimate tone
    "You're listening to me, Mr. New Vegas. And you look extraordinarily beautiful right now.",
    "The women of New Vegas asked me a lot if there's a mrs. New Vegas. Well, of course there is. You're her. And you're still as perfect as the day we met.",
    
    # Polished song intros
    "And now I'd like to play one of my very favorite songs for you.",
    "Got some Dean Martin coming up talking about the greatest feeling in the world. Love. Ain't that a kick in the head? Sure is. Dino. It sure is.",
    "You know, sometimes the journey beats the destination. And especially if your spurs go jingle, jangle, jingle.",
    
    # Suave sign-offs
    "That's all for now. This is Mr. New Vegas saying I'm just no good without you.",
    "This is Mr. New Vegas. Wishing you lady like luck tonight.",
    "This is Mr. New Vegas signing off. Just kidding. I'm not going anywhere. My love for you is too strong.",
    
    # Charismatic asides
    "You know, I, uh, tried to measure my charisma on a Vitamedic vigor tester once the machine burst into flames.",
    "This is Mr. New Vegas. Fanning the flames of your passion.",
]


def get_voice_samples(dj: str) -> list[str]:
    """Get voice samples for a specific DJ."""
    if dj.lower() == "julie":
        return JULIE_VOICE_SAMPLES
    else:  # mr_new_vegas
        return MR_NEW_VEGAS_VOICE_SAMPLES


def format_voice_samples(dj: str) -> str:
    """Format voice samples as a numbered list for prompts."""
    samples = get_voice_samples(dj)
    lines = [f"{i+1}. \"{s}\"" for i, s in enumerate(samples)]
    return "\n".join(lines)
