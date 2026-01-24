"""Generate better validation samples for Mr. New Vegas
Filter out news segments and focus on actual DJ commentary/song intros
"""
import json, random
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
IN=ROOT/'data'/'style_analysis'/'mr_new_vegas_categorized.json'
OUT=ROOT/'docs'/'script_improvement'/'mr_new_vegas_validation_samples.md'

c=json.load(open(IN,'r',encoding='utf8'))

# Manually select good non-news examples across all categories
# Note: Mr. New Vegas has very few post-song outros - his style is primarily intro-focused
manual_samples = [
    # Song intros - romantic, smooth lead-ins
    ('song_intro', "This next song is just magical."),
    ('song_intro', "Here is Bing Crosby reminding us of those times when you absolutely have to kiss the person you love."),
    ('song_intro', "Coming up, I've got some tunes I think all of you are gonna like."),
    ('song_intro', "This next song helped me through a very difficult time in my life, and I hope one day it can do the same for you."),
    ('song_intro', "Got some Dean Martin coming up talking about the greatest feeling in the world."),
    ('song_intro', "And now I'd like to play one of my very favorite songs for you."),
    ('song_intro', "You're gonna love this next song, I guarantee it."),
    
    # Song outros / transitions
    ('song_outro', "I hope you enjoy it."),
    ('song_outro', "You're listening to Radio New Vegas, your little jukebox in the Mojave wasteland."),
    ('song_outro', "Thank you very, very much for listening."),
    
    # Commentary - romantic, flirtatious, showman style
    ('commentary', "Love. Ain't that a kick in the head? Sure is. Dino. It sure is."),
    ('commentary', "Sometimes you can't help being mad about the boy."),
    ('commentary', "New Vegas, reminding you that you're nobody till somebody loves you and that somebody is me."),
    ('commentary', "I love you, ladies and gentlemen."),
    ('commentary', "And you look extraordinarily beautiful right now."),
    ('commentary', "My love for you is too strong."),
    ('commentary', "You know, I, uh, tried to measure my charisma on a Vitamedic vigor tester once the machine burst into flames."),
    
    # Other - catchphrases, greetings, personality
    ('other', "Ladies and gentlemen."),
    ('other', "This is Mr. New Vegas, and I feel something magic in the air tonight. And I'm not just talking about the gamma radiation."),
    ('other', "The Mojave Wasteland, is just a fascinating place, isn't it? You never know what's going to happen next."),
    
    # More song intros - varied approaches
    ('song_intro', "Gonna play a song for you right now. And it's about that special someone you find only once in a blue moon."),
    ('song_intro', "More classics coming right up for you, so stay tuned."),
    
    # More commentary - flirtation, direct address
    ('commentary', "And in case you're wondering if you've come to the right place, you have the women of New Vegas asked me a lot if there's a mrs. New Vegas. Well, of course there is. You're her. And you're still as perfect as the day we met."),
    ('commentary', "Have you ever said you love someone when it wasn't quite true? Sure you have. But you shouldn't because it's a sin to tell a lie."),
    ('commentary', "Have you ever been in love with a celebrity? Now, come on, you don't have to be shy I feel it between us two."),
    
    # More outros/transitions
    ('song_outro', "This is Mr. New Vegas saying I'm just no good without you."),
    
    # More personality
    ('other', "It's me again, Mr. New Vegas, reminding you that you're nobody till somebody loves you and that somebody is me."),
    ('other', "Welcome back, ladies and gentlemen, this is Mr. New Vegas."),
    ('other', "And we're back. This is Mr. New Vegas, and I feel something magic in the air tonight. And I'm not just talking about the gamma radiation."),
    ('other', "Howdy, folks. It's Mr. New Vegas, and I have a good feeling about all of you listening."),
]

samples = manual_samples

with open(OUT,'w',encoding='utf8') as f:
    f.write('# Validation samples for mr_new_vegas\n\n')
    for i,(cat,s) in enumerate(samples,1):
        f.write(f'## Sample {i}  (category: {cat})\n{s}\n\n')
print('Wrote',OUT,'with',len(samples),'samples')
