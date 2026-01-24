"""Generate better Julie validation samples with proper mix of intros, outros, and commentary"""
from pathlib import Path
OUT=Path(__file__).resolve().parents[1]/'docs'/'script_improvement'/'julie_validation_samples.md'

# Manually curated from transcript - showing her characteristic style across all categories
samples = [
    # Song intros - various styles
    ('song_intro', "Here is Ain't Misbehavin."),
    ('song_intro', "Coming up next is dark as a Dungeon by Tennessee Ernie Ford."),
    ('song_intro', "Here's jukebox Saturday night."),
    ('song_intro', "And now, in the unwieldy song title department, here's my answer to Driving Nails in My Coffin by Jerry Irby."),
    ('song_intro', "Here's the five stars with Atom Bomb Baby, a song that suggests they may not have made the most responsible choices when it came to relationships."),
    ('song_intro', "This next one goes out to all you dwellers looking for the perfect and I mean perfect spot for your camp. It's Bing Crosby singing Don't Fence Me In."),
    
    # Song outros - post-song reactions
    ('song_outro', "Hope that you all enjoyed that one, friends."),
    ('song_outro', "That was happy days are here again. Which, well, hey, you're alive, ain't ya? Pretty decent reason to be happy."),
    ('song_outro', "Oh my goodness, does that one swing. Oh, am I allowed to say that every part of that song is my favorite part? It's too hard to decide otherwise."),
    ('song_outro', "I feel like that could have gone on for another twenty minutes of solos, and it sure sounds like everyone playing would have loved doing it."),
    
    # Commentary - personal reflections and encouragement
    ('commentary', "I love that one because it sounds like a bunch of friends just hanging out and having a good time. Insect phobias aside, of course."),
    ('commentary', "Doesn't Billie Holiday just have the most beautiful voice. Every time I've heard that song since I was a little girl, I've just been carried away by it."),
    ('commentary', "I know it's not the same for everyone, but for me. There are moments where I miss where I came from and the family and friends no longer with us. Be grateful for what you have, friends, but don't forget where you've been."),
    ('commentary', "I still get goosebumps every time I hear it. You do too, don't you? Ah, I know you do."),
    ('commentary', "Oh boy do I relate to this one. Just me and the radio here by myself. Got nearly everything I love within arm's reach."),
    ('commentary', "No judgments here, friends. Let's call this one a cautionary tale about self-destructive behavior. I'm not telling you how to live your lives just trying to help you live your best ones."),
    
    # Other - quirky observations, humor
    ('other', "Oh, Cass, sweetie, raise your standards just a little bit. You're worth it."),
    ('other', "I just love that someone, somewhere decided the phrase bingle bangle bungle was worth using as a lyric. I hope it makes you smile, too."),
    ('other', "I can't be the only one who wants to see a duet with Mr. Two left hands here and Pigfoot Pete. Right. Who's with me?"),
    ('other', "Do you think at any point those guys said, hey, this is a weird thing to write a song about. Because I wonder about it all the time."),
    
    # More song intros with personality
    ('song_intro', "Hey there. Would you like to weirdly feel happy and sad at the same time? Well, here's your chance. It's bubbles in my beer."),
    ('song_intro', "Oh, this next song was one of my mom's favorites. She'd get so excited every time it came on the radio. Without fail. Here's opus number one by Tommy Dorsey."),
    
    # More commentary - advice, observations
    ('commentary', "It's true that there are people in the world who will let you down. But it should just make you appreciate the folks who are always there for you even more. Not everyone is a fair weather friend. You find the people who are there for you no matter what, and you stick together."),
    ('commentary', "Take a page from Billie Holiday and believe you can do the impossible. It can make all the difference."),
    
    # More outros
    ('song_outro', "That song is just so timeless. Feels like it's been around forever, doesn't it?"),
    ('song_outro', "Did you crack open a Nuka Cola for that? I sure did. Also, I am running super low on Nuka Cola. Donations are appreciated."),
    
    # More personality/other
    ('other', "You know, it is hard to find ballistic fiber. Oh my gosh."),
    ('other', "Okay, everyone. Here it comes. Grab your pals, maybe a banjo and belt it out along with the radio. I know you've been waiting for this one."),
    ('other', "I hate to break it to you all, but if you see an orange colored sky, grab the radex and lots of it, because that ain't love out there."),
    ('other', "Remember, friends, you're not alone out there. The world is filled with people and you share the same goals with at least some of them. Take care of yourselves and each other."),
]

with open(OUT,'w',encoding='utf8') as f:
    f.write('# Validation samples for julie\n\n')
    for i,(cat,s) in enumerate(samples,1):
        f.write(f'## Sample {i}  (category: {cat})\n{s}\n\n')
print('Wrote',OUT,'with',len(samples),'samples')
