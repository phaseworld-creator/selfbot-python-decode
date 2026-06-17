import discord, platform, psutil, time, random, asyncio, base64, hashlib, math, os, json, sys, datetime


START_TIME = time.time()
RESET="\u001b[0m"; BOLD="\u001b[1m"; RED="\u001b[31m"; GREEN="\u001b[32m"
YELLOW="\u001b[33m"; BLUE="\u001b[34m"; PURPLE="\u001b[35m"; CYAN="\u001b[36m"; WHITE="\u001b[37m"

def ansi(t): return f"```ansi\n{t}{RESET}\n```"
def box(title,lines,c=CYAN):
    b=f"{c}{BOLD}{title}{RESET}\n{CYAN}{'─'*36}{RESET}\n"
    for k,v in lines: b+=f"{YELLOW}{k:<14}{RESET}{WHITE}{v}{RESET}\n"
    return ansi(b)

def setup_selfbot_commands(client, config):
    prefix = config.get("prefix",".")

    @client.event
    async def on_message(message):
        if message.author != client.user:
            # Option B: Safely check for external plugin handler before execution
            if hasattr(client, "_plugin_handler"):
                await client._plugin_handler(message)
            return
        if not message.content.startswith(prefix): return
        args = message.content[len(prefix):].strip().split()
        if not args: return
        cmd = args[0].lower(); rest = " ".join(args[1:])
        try: await message.delete()
        except: pass

        if cmd == "help":
            cmds = [
                ("GENERAL",""),  (f"{prefix}ping","Latency"), (f"{prefix}info","System info"),
                (f"{prefix}uptime","Uptime"), (f"{prefix}whoami","Account info"),
                ("STATUS",""), (f"{prefix}status","Set status"), (f"{prefix}clearstatus","Clear status"),
                (f"{prefix}rotator","on/off rotator"),
                ("AFK",""), (f"{prefix}afk","Enable AFK"), (f"{prefix}unafk","Disable AFK"),
                ("TEXT",""), (f"{prefix}say","Send message"), (f"{prefix}mock","MoCkIfY"),
                (f"{prefix}reverse","Reverse"), (f"{prefix}big","🅱 big letters"),
                (f"{prefix}clap","clap👏text"), (f"{prefix}aesthetic","ａｅｓｔｈｅｔｉｃ"),
                (f"{prefix}zalgo","Z̷a̸l̷g̸o̴"), (f"{prefix}repeat","Repeat N times"),
                (f"{prefix}upper","UPPERCASE"), (f"{prefix}lower","lowercase"),
                (f"{prefix}spoiler","||spoiler||"), (f"{prefix}leet","l33tspeak"),
                (f"{prefix}scramble","Mix text"), (f"{prefix}binary","To Binary"),
                (f"{prefix}hex","To Hex string"), (f"{prefix}morse","To Morse code"),
                (f"{prefix}vapor","ＶＡＰＯＲＷＡＶＥ"), (f"{prefix}anonymize","Scramble vowels"),
                (f"{prefix}stacked","S t a c k e d"),
                ("FUN",""), (f"{prefix}coinflip","Heads/tails"), (f"{prefix}8ball","8-ball"),
                (f"{prefix}roll","Roll dice"), (f"{prefix}choose","Pick option"),
                (f"{prefix}rate","Rate /10"), (f"{prefix}roast","Roast"), (f"{prefix}compliment","Compliment"),
                (f"{prefix}fact","Random fact"), (f"{prefix}ship","Ship users"),
                (f"{prefix}iq","Random IQ"), (f"{prefix}pp","pp size"),
                (f"{prefix}dadjoke","Dad joke"), (f"{prefix}pickup","Pickup lines"),
                (f"{prefix}clown","Clown meter"), (f"{prefix}cooldog","Cool dog rating"),
                (f"{prefix}hack","Fake hack user"), (f"{prefix}token","Fake token puller"),
                (f"{prefix}catfact","Cat facts"), (f"{prefix}fortune","Fortune cookie"),
                (f"{prefix}percent","Random percentage"), (f"{prefix}slap","Slap user"),
                ("GAMES",""), (f"{prefix}rps","Rock Paper Scissors"), (f"{prefix}slots","Slot machine"),
                (f"{prefix}blackjack","Draw card values"),
                ("CRYPTO",""), (f"{prefix}btc","Simulated Bitcoin ticker"), (f"{prefix}eth","Simulated Ethereum ticker"),
                (f"{prefix}sol","Simulated Solana ticker"),
                ("ACCOUNT",""), (f"{prefix}avatar","Avatar URL"), (f"{prefix}serverinfo","Server info"),
                (f"{prefix}userinfo","User info"), (f"{prefix}servers","List servers"),
                (f"{prefix}randomuser","Pick random member"), (f"{prefix}rollcall","Online counts"),
                (f"{prefix}permissions","Show your perms"),
                ("IMAGE",""), (f"{prefix}wanted","Wanted asset link"), (f"{prefix}rip","Grave asset link"),
                (f"{prefix}affect","Affect template link"), (f"{prefix}trash","Trash asset link"),
                (f"{prefix}blur","Blur avatar template"), (f"{prefix}jail","Jail asset template"),
                ("SPAM",""), (f"{prefix}spam","Spam N times"), (f"{prefix}tts","TTS message"),
                (f"{prefix}ghostspam","Quick delete spam"),
                ("UTIL",""), (f"{prefix}calc","Calculator"), (f"{prefix}b64enc","B64 encode"),
                (f"{prefix}b64dec","B64 decode"), (f"{prefix}color","Hex color info"),
                (f"{prefix}hash","MD5/SHA256 generation"), (f"{prefix}math","Advanced math values"),
                (f"{prefix}pwdgen","Secure password gen"), (f"{prefix}charcount","Character count"),
                ("MOD (PRANK)",""), (f"{prefix}fakepurge","Simulate clear messages"), (f"{prefix}fakelock","Simulate lockdown channel"),
                (f"{prefix}fakeslow","Simulate slowmode modification"),
                ("MOD (REAL)",""), (f"{prefix}r-kick","Real kick target member"), (f"{prefix}r-ban","Real ban target member"),
                (f"{prefix}r-unban","Real unban past target user"), (f"{prefix}r-mute","Real native user timeout"),
                (f"{prefix}r-unmute","Real native timeout removal"), (f"{prefix}r-purge","Real dynamic message purge"),
            ]
            
            # Start forming chunks to avoid the 4000 char threshold
            header = f"{PURPLE}{BOLD}⬡ PhaseWorld SelfBot Dev{RESET}\n{CYAN}{'─'*36}{RESET}\n"
            current_body = header
            chunks = []

            for k, v in cmds:
                if v == "": line = f"\n{YELLOW}{BOLD}━━ {k} {'━'*(30-len(k))}{RESET}\n"
                else: line = f"  {CYAN}{k:<18}{RESET}{WHITE}{v}{RESET}\n"
                
                # Check length limit before adding (accounting for the ansi block wraps)
                if len(ansi(current_body + line)) > 1900:
                    chunks.append(current_body)
                    current_body = header + line
                else:
                    current_body += line
            
            if current_body:
                chunks.append(current_body)

            for part in chunks:
                await message.channel.send(ansi(part))
                await asyncio.sleep(0.3) # Avoid hitting message rate limits

        elif cmd=="ping":
            ms=round(client.latency*1000); c=GREEN if ms<100 else YELLOW if ms<200 else RED
            await message.channel.send(ansi(f"{c}{BOLD}🏓 Pong!{RESET}  {c}{ms}ms{RESET}"))

        elif cmd=="info":
            mem=psutil.virtual_memory(); cpu=psutil.cpu_percent(interval=0.1)
            await message.channel.send(box("⚙️ System Info",[
                ("OS",platform.system()+" "+platform.release()),("CPU",f"{cpu}%"),
                ("RAM",f"{mem.percent}% ({round(mem.used/1024**3,1)}GB/{round(mem.total/1024**3,1)}GB)"),
                ("Python",platform.python_version()),("Account",str(client.user)),("ID",str(client.user.id))]))

        elif cmd=="uptime":
            e=int(time.time()-START_TIME); h,r=divmod(e,3600); m,s=divmod(r,60)
            await message.channel.send(ansi(f"{CYAN}{BOLD}⏱ Uptime{RESET}  {GREEN}{h}h {m}m {s}s{RESET}"))

        elif cmd=="whoami":
            u=client.user
            await message.channel.send(box("👤 Who Am I",[("Tag",str(u)),("ID",str(u.id)),("Bot",str(u.bot))]))

        elif cmd=="status":
            if rest:
                await client.change_presence(activity=discord.CustomActivity(name=rest))
                await message.channel.send(ansi(f"{GREEN}{BOLD}✓ Status:{RESET} {WHITE}{rest}{RESET}"))
            else: await message.channel.send(ansi(f"{RED}Usage: {prefix}status <text>{RESET}"))

        elif cmd=="clearstatus":
            await client.change_presence(activity=None)
            await message.channel.send(ansi(f"{GREEN}{BOLD}✓ Status cleared.{RESET}"))

        elif cmd=="rotator":
            if rest=="on": await client._rotator.start(); await message.channel.send(ansi(f"{GREEN}{BOLD}✓ Rotator on.{RESET}"))
            elif rest=="off": await client._rotator.stop(); await message.channel.send(ansi(f"{YELLOW}⏹ Rotator off.{RESET}"))

        elif cmd=="afk":
            msg=rest or "I'm AFK."; client._afk.set(True,msg)
            await message.channel.send(ansi(f"{YELLOW}{BOLD}💤 AFK:{RESET} {WHITE}{msg}{RESET}"))

        elif cmd=="unafk":
            client._afk.set(False); await message.channel.send(ansi(f"{GREEN}{BOLD}✓ AFK off.{RESET}"))

        elif cmd=="say": await message.channel.send(rest)
        elif cmd=="mock": await message.channel.send("".join(c.upper() if i%2==0 else c.lower() for i,c in enumerate(rest)))
        elif cmd=="reverse": await message.channel.send(rest[::-1])
        elif cmd=="upper": await message.channel.send(rest.upper())
        elif cmd=="lower": await message.channel.send(rest.lower())
        elif cmd=="spoiler": await message.channel.send(f"||{rest}||")
        elif cmd=="clap": await message.channel.send("👏".join(rest.split()))
        
        elif cmd=="leet":
            m={'a':'4','e':'3','g':'6','l':'1','o':'0','s':'5','t':'7'}
            await message.channel.send("".join(m.get(c.lower(),c) for c in rest))

        elif cmd=="scramble":
            out=[]
            for w in rest.split():
                if len(w)>3:
                    mid=list(w[1:-1]); random.shuffle(mid)
                    out.append(w[0]+"".join(mid)+w[-1])
                else: out.append(w)
            await message.channel.send(" ".join(out))

        elif cmd=="binary":
            await message.channel.send(" ".join(format(ord(c),'08b') for c in rest)[:1900])

        elif cmd=="hex":
            await message.channel.send(" ".join(hex(ord(c))[2:] for c in rest)[:1900])

        elif cmd=="anonymize":
            vow = str.maketrans("aeiouAEIOU", "xxxxxXXXXX")
            await message.channel.send(rest.translate(vow))

        elif cmd=="stacked":
            await message.channel.send("\n".join(list(rest)))

        elif cmd=="morse":
            cd={'a': '.-', 'b': '-...', 'c': '-.-.', 'd': '-..', 'e': '.', 'f': '..-.', 'g': '--.', 'h': '....', 'i': '..', 'j': '.---', 'k': '-.-', 'l': '.-..', 'm': '--', 'n': '-.', 'o': '---', 'p': '.--.', 'q': '--.-', 'r': '.-.', 's': '...', 't': '-', 'u': '..-', 'v': '...-', 'w': '.--', 'x': '-..-', 'y': '-.--', 'z': '--..', '1': '.----', '2': '..---', '3': '...--', '4': '....-', '5': '.....', '6': '-....', '7': '--...', '8': '---..', '9': '----.', '0': '-----', ' ': '/'}
            await message.channel.send(" ".join(cd.get(c.lower(),'?') for c in rest)[:1900])

        elif cmd=="vapor":
            await message.channel.send("  ".join(rest.upper()))

        elif cmd=="big":
            reg={c:chr(0x1F1E0+ord(c)-ord('a')) for c in 'abcdefghijklmnopqrstuvwxyz'}; reg[' ']='   '
            await message.channel.send(" ".join(reg.get(c.lower(),c) for c in rest))

        elif cmd=="aesthetic":
            full={c:chr(0xFF01+ord(c)-ord('!')) for c in '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'}
            await message.channel.send("".join(full.get(c,c) for c in rest))

        elif cmd=="zalgo":
            zc=[chr(x) for x in range(0x0300,0x036F)]
            await message.channel.send("".join(c+"".join(random.choice(zc) for _ in range(random.randint(1,4))) for c in rest)[:1900])

        elif cmd=="repeat":
            p=rest.split(" ",1)
            if len(p)==2 and p[0].isdigit(): await message.channel.send(("\n".join([p[1]]*min(int(p[0]),10)))[:1900])

        elif cmd=="coinflip":
            r=random.choice(["Heads","Tails"]); c=GREEN if r=="Heads" else YELLOW
            await message.channel.send(ansi(f"{c}{BOLD}🪙 {r}!{RESET}"))

        elif cmd=="8ball":
            answers=[(GREEN,["It is certain.","Without a doubt.","Yes definitely.","Most likely.","Signs point to yes."]),
                     (YELLOW,["Reply hazy.","Ask again later.","Cannot predict now."]),
                     (RED,["Don't count on it.","My reply is no.","Very doubtful."])]
            c,g=random.choice(answers)
            await message.channel.send(ansi(f"{CYAN}{BOLD}🎱 8Ball{RESET}\n{WHITE}{rest}{RESET}\n{c}{random.choice(g)}{RESET}"))

        elif cmd=="roll":
            p=rest.split("d") if "d" in rest else [None,rest]
            count=min(int(p[0]) if p[0] and p[0].isdigit() else 1,20)
            sides=int(p[1]) if p[1] and p[1].isdigit() else 6
            rolls=[random.randint(1,sides) for _ in range(count)]
            r=f"{GREEN}{BOLD}🎲 {count}d{sides}{RESET}\n{WHITE}"+"  ".join(str(x) for x in rolls)
            if count>1: r+=f"\n{YELLOW}Total: {sum(rolls)}{RESET}"
            await message.channel.send(ansi(r))

        elif cmd=="choose":
            opts=[o.strip() for o in rest.split(",") if o.strip()]
            if opts: await message.channel.send(ansi(f"{CYAN}{BOLD}🎯 Chose:{RESET} {GREEN}{random.choice(opts)}{RESET}"))

        elif cmd=="rate":
            if rest.lower() == "phaseworld":
                await message.channel.send(ansi(f"{CYAN}{BOLD}⭐ PhaseWorld{RESET}\n{GREEN}██████████ ∞/10{RESET}"))
            elif rest.lower() == "jayden":
                await message.channel.send(ansi(f"{CYAN}{BOLD}⭐ Jayden{RESET}\n{GREEN}██████████ ∞/10{RESET}"))
            elif rest.lower() == "nighty":
                await message.channel.send(ansi(f"{CYAN}{BOLD}⭐ Nighty{RESET}\n{GREEN}██████████ ∞/10{RESET}"))
            elif rest.lower() == "adam":
                await message.channel.send(ansi(f"{CYAN}{BOLD}⭐ Adam{RESET}\n{RED}░░░░░░░░░░ -100/10{RESET}"))
            else:
                sc=random.randint(0,10); bar="█"*sc+"░"*(10-sc); c=RED if sc<4 else YELLOW if sc<7 else GREEN
                await message.channel.send(ansi(f"{CYAN}{BOLD}⭐ {rest}{RESET}\n{c}{bar} {sc}/10{RESET}"))

        elif cmd=="roast":
            roasts=["You're the human equivalent of a participation trophy.",
                "I'd roast you but I'm not allowed to burn trash.",
                "You have your entire life to be an idiot. Take today off.",
                "Some day you'll go far. I hope you stay there.",
                "I'd call you a tool but tools are useful.",
                "You're proof evolution can go in reverse."]
            await message.channel.send(ansi(f"{RED}{BOLD}🔥 Roast for {rest or 'you'}:{RESET}\n{WHITE}{random.choice(roasts)}{RESET}"))

        elif cmd=="compliment":
            comp=["You light up every room you walk into.","You're more fun than bubble wrap.",
                "You could survive a zombie apocalypse.","You're like a ray of sunshine on a cloudy day."]
            await message.channel.send(ansi(f"{GREEN}{BOLD}💚 {rest or 'You'}:{RESET}\n{WHITE}{random.choice(comp)}{RESET}"))

        elif cmd=="dadjoke":
            jk=["I'm reading a book on anti-gravity. I just can't put it down!","What do you call a factory that makes okay products? A satisfactory.",
                "Why did the scarecrow win an award? Because he was outstanding in his field.","Dear Math, grow up and solve your own problems."]
            await message.channel.send(ansi(f"{PURPLE}{BOLD}👨 Dad Joke:{RESET}\n{WHITE}{random.choice(jk)}{RESET}"))

        elif cmd=="pickup":
            pu=["Are you a keyboard? Because you're just my type.","Are you a parking ticket? 'Cause you've got fine written all over you.",
                "Do you like Star Wars? Because Yoda only one for me.","Is your name Google? Because you have everything I've been searching for."]
            await message.channel.send(ansi(f"{GREEN}{BOLD}💞 Pickup Line:{RESET}\n{WHITE}{random.choice(pu)}{RESET}"))

        elif cmd=="clown":
            sc=random.randint(0,100); bar="█"*(sc//10)+"░"*(10-sc//10)
            await message.channel.send(ansi(f"{RED}{BOLD}🤡 Clown Meter for {rest or 'you'}:{RESET}\n{RED}{bar} {sc}%{RESET}"))

        elif cmd=="cooldog":
            sc=random.randint(5,10); bar="🦴"*sc
            await message.channel.send(ansi(f"{BLUE}{BOLD}🕶️ Cool Dog Rating for {rest or 'you'}:{RESET}\n{WHITE}{bar} {sc}/10{RESET}"))

        elif cmd=="hack":
            t=rest or "system"
            m=await message.channel.send(ansi(f"{GREEN}💻 Accessing bypass node for target: {t}...{RESET}"))
            await asyncio.sleep(1.5); await m.edit(content=ansi(f"{GREEN}💾 Decrypting firewalls... [■■■░░░░░░░] 30%{RESET}"))
            await asyncio.sleep(1.5); await m.edit(content=ansi(f"{GREEN}📡 Extracting authentication tokens... [■■■■■■■░░░] 70%{RESET}"))
            await asyncio.sleep(1.5); await m.edit(content=ansi(f"{GREEN}💉 Injection complete. Target footprint permanently logged!{RESET}"))

        elif cmd=="token":
            tok=f"NzM{random.choice('XYZabc')}"+".".join("".join(random.choices("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-",k=n)) for n in [21,6,27])
            await message.channel.send(ansi(f"{RED}{BOLD}⚠️ Token Extraction Target: {rest or 'Self'}{RESET}\n{WHITE}{tok}{RESET}"))

        elif cmd=="catfact":
            cf=["Cats sleep 70% of their lives.","A house cat can run up to 30mph.","Cats have 32 muscles in each ear.","A cat's nose print is completely unique."]
            await message.channel.send(ansi(f"{CYAN}{BOLD}🐱 Cat Fact:{RESET}\n{WHITE}{random.choice(cf)}{RESET}"))

        elif cmd=="fortune":
            ft=["An exciting opportunity lies ahead.","A small investment today yields great returns tomorrow.","Avoid conflicts; step back to observe.","Your hard work will pay off very soon."]
            await message.channel.send(ansi(f"{YELLOW}{BOLD}🥠 Fortune Cookie:{RESET}\n{WHITE}{random.choice(ft)}{RESET}"))

        elif cmd=="percent":
            await message.channel.send(ansi(f"{CYAN}{BOLD}📊 Percentage Match for {rest or 'Idea'}:{RESET}\n{GREEN}{random.randint(0,100)}%{RESET}"))

        elif cmd=="slap":
            t = message.mentions[0].mention if message.mentions else (rest or "themselves")
            await message.channel.send(ansi(f"{RED}{BOLD}💥 Action Log:{RESET}\n{WHITE}PhaseWorld slapped {t} directly across the face!{RESET}"))

        elif cmd=="rps":
            choices = ["rock", "paper", "scissors"]
            user_choice = rest.lower().strip()
            if user_choice not in choices:
                await message.channel.send(ansi(f"{RED}Usage: {prefix}rps [rock/paper/scissors]{RESET}")); return
            bot_choice = random.choice(choices)
            if user_choice == bot_choice: result = f"{YELLOW}Tie game!{RESET}"
            elif (user_choice=="rock" and bot_choice=="scissors") or (user_choice=="paper" and bot_choice=="rock") or (user_choice=="scissors" and bot_choice=="paper"):
                result = f"{GREEN}You win!{RESET}"
            else: result = f"{RED}Bot wins!{RESET}"
            await message.channel.send(ansi(f"{CYAN}{BOLD}🎮 Rock-Paper-Scissors{RESET}\n{WHITE}You: {user_choice} | Bot: {bot_choice}\nResult: {result}"))

        elif cmd=="slots":
            items = ["🍒", "🍋", "🍇", "💎", "🔔"]
            s1, s2, s3 = random.choice(items), random.choice(items), random.choice(items)
            res = f"{GREEN}{BOLD}JACKPOT!{RESET}" if s1 == s2 == s3 else f"{YELLOW}Close one!{RESET}" if s1 == s2 or s2 == s3 or s1 == s3 else f"{RED}You lost!{RESET}"
            await message.channel.send(ansi(f"{PURPLE}{BOLD}🎰 Slot Machine{RESET}\n{WHITE}[ {s1} | {s2} | {s3} ]\nResult: {res}"))

        elif cmd=="blackjack":
            p1, p2 = random.randint(1, 11), random.randint(1, 11)
            await message.channel.send(box("🃏 Blackjack Draw", [("Card 1", str(p1)), ("Card 2", str(p2)), ("Total Sum", str(p1+p2))], c=YELLOW))

        elif cmd=="btc":
            val = random.randint(85000, 110000)
            await message.channel.send(box("🪙 Crypto Ticker", [("Asset", "Bitcoin (BTC)"), ("Value", f"${val:,}"), ("24H Vol", "+3.42%")], c=GREEN))

        elif cmd=="eth":
            val = random.randint(2800, 4200)
            await message.channel.send(box("🪙 Crypto Ticker", [("Asset", "Ethereum (ETH)"), ("Value", f"${val:,}"), ("24H Vol", "-1.15%")], c=BLUE))

        elif cmd=="sol":
            val = random.randint(140, 290)
            await message.channel.send(box("🪙 Crypto Ticker", [("Asset", "Solana (SOL)"), ("Value", f"${val}.84"), ("24H Vol", "+12.9%")], c=PURPLE))

        elif cmd=="fact":
            facts=["Honey never spoils — 3000-year-old honey was found in Egyptian tombs.",
                "A group of flamingos is called a flamboyance.",
                "Octopuses have three hearts and blue blood.",
                "Bananas are berries, but strawberries aren't.",
                "Sharks are older than trees.",
                "Wombats produce cube-shaped poop."]
            await message.channel.send(ansi(f"{CYAN}{BOLD}💡 Fact{RESET}\n{WHITE}{random.choice(facts)}{RESET}"))

        elif cmd=="ship":
            p=rest.split(); a=p[0] if p else "A"; b=p[1] if len(p)>1 else "B"
            sc=random.randint(0,100); bar="█"*(sc//10)+"░"*(10-sc//10)
            c=RED if sc<40 else YELLOW if sc<70 else GREEN
            await message.channel.send(ansi(f"{PURPLE}{BOLD}💘 {a} + {b}{RESET}\n{c}{bar} {sc}%{RESET}"))

        elif cmd=="iq":
            iq=random.randint(1,200); c=RED if iq<70 else YELLOW if iq<120 else GREEN
            await message.channel.send(ansi(f"{CYAN}{BOLD}🧠 {rest or 'Your'} IQ:{RESET} {c}{iq}{RESET}"))

        elif cmd=="pp":
            if rest.lower() == "phaseworld":
                await message.channel.send(ansi(f"{YELLOW}{BOLD}📏 PhaseWorld pp:{RESET}\n{WHITE}8{"="*100}D{RESET}"))
            elif rest.lower() == "jayden":
                await message.channel.send(ansi(f"{YELLOW}{BOLD}📏 Jayden pp:{RESET}\n{WHITE}8{"="*100}D{RESET}"))
            else:
                sz=random.randint(0,20)
                await message.channel.send(ansi(f"{YELLOW}{BOLD}📏 {rest or 'Your'} pp:{RESET}\n{WHITE}8{'='*sz}D{RESET}"))

        elif cmd=="avatar":
            t=message.mentions[0] if message.mentions else message.author
            await message.channel.send(ansi(f"{CYAN}{BOLD}🖼 {t}'s Avatar{RESET}\n{WHITE}{t.display_avatar.url}{RESET}"))

        elif cmd=="wanted":
            t=message.mentions[0] if message.mentions else message.author
            await message.channel.send(ansi(f"{YELLOW}{BOLD}🤠 Bounty Poster for {t.name}:{RESET}\n{WHITE}https://api.popcat.xyz/wanted?image={t.display_avatar.with_format('png').url}{RESET}"))

        elif cmd=="rip":
            t=message.mentions[0] if message.mentions else message.author
            await message.channel.send(ansi(f"{WHITE}{BOLD}🪦 Grave marker link for {t.name}:{RESET}\n{WHITE}https://api.popcat.xyz/gun?image={t.display_avatar.with_format('png').url}{RESET}"))

        elif cmd=="affect":
            t=message.mentions[0] if message.mentions else message.author
            await message.channel.send(ansi(f"{PURPLE}{BOLD}🖼️ Affect Layer template:{RESET}\n{WHITE}https://api.popcat.xyz/affect?image={t.display_avatar.with_format('png').url}{RESET}"))

        elif cmd=="trash":
            t=message.mentions[0] if message.mentions else message.author
            await message.channel.send(ansi(f"{RED}{BOLD}🗑️ Trash layer asset template:{RESET}\n{WHITE}https://api.popcat.xyz/trash?image={t.display_avatar.with_format('png').url}{RESET}"))

        elif cmd=="blur":
            t=message.mentions[0] if message.mentions else message.author
            await message.channel.send(ansi(f"{BLUE}{BOLD}💧 Blur Layer template:{RESET}\n{WHITE}https://api.popcat.xyz/blur?image={t.display_avatar.with_format('png').url}{RESET}"))

        elif cmd=="jail":
            t=message.mentions[0] if message.mentions else message.author
            await message.channel.send(ansi(f"{RED}{BOLD}🔒 Jail layer asset template:{RESET}\n{WHITE}https://api.popcat.xyz/jail?image={t.display_avatar.with_format('png').url}{RESET}"))

        elif cmd=="serverinfo":
            g=message.guild
            if not g: await message.channel.send(ansi(f"{RED}Not in a server.{RESET}")); return
            await message.channel.send(box(f"🏠 {g.name}",[("ID",str(g.id)),("Members",str(g.member_count)),
                ("Channels",str(len(g.channels))),("Roles",str(len(g.roles))),
                ("Owner",str(g.owner)),("Boost",f"Lvl {g.premium_tier}"),
                ("Created",g.created_at.strftime("%Y-%m-%d"))]))

        elif cmd=="userinfo":
            t=message.mentions[0] if message.mentions else message.author
            mem=message.guild.get_member(t.id) if message.guild else None
            await message.channel.send(box(f"👤 {t}",[("ID",str(t.id)),("Bot",str(t.bot)),
                ("Created",t.created_at.strftime("%Y-%m-%d")),
                ("Joined",mem.joined_at.strftime("%Y-%m-%d") if mem and mem.joined_at else "N/A"),
                ("Roles",str(len(mem.roles)-1) if mem else "N/A")]))

        elif cmd=="servers":
            guilds=sorted(client.guilds,key=lambda g:g.member_count,reverse=True)[:25]
            body=f"{CYAN}{BOLD}🌐 Servers ({len(client.guilds)}){RESET}\n{CYAN}{'─'*36}{RESET}\n"
            for g in guilds: body+=f"  {WHITE}{g.name:<28}{YELLOW}{g.member_count}{RESET}\n"
            await message.channel.send(ansi(body))

        elif cmd=="randomuser":
            if not message.guild: await message.channel.send(ansi(f"{RED}Not in a server.{RESET}")); return
            m=random.choice(message.guild.members)
            await message.channel.send(box("🎯 Random Choice",[("Target",str(m)),("ID",str(m.id))],c=GREEN))

        elif cmd=="rollcall":
            if not message.guild: await message.channel.send(ansi(f"{RED}Not in a server.{RESET}")); return
            g=message.guild; status=g.members
            await message.channel.send(box("📊 Server Rollcount",[("Total Users",str(g.member_count)),("Cached",str(len(status)))]))

        elif cmd=="permissions":
            if not message.guild: await message.channel.send(ansi(f"{RED}Not in a server.{RESET}")); return
            p = message.channel.permissions_for(message.guild.me)
            await message.channel.send(box("🛠 Channel Perms", [("Send Msg", str(p.send_messages)), ("Embed Link", str(p.embed_links)), ("Manage Msg", str(p.manage_messages))]))

        elif cmd=="spam":
            p=rest.split(" ",1)
            if len(p)==2 and p[0].isdigit():
                for _ in range(min(int(p[0]),8)):
                    await message.channel.send(p[1]); await asyncio.sleep(0.7)

        elif cmd=="ghostspam":
            p=rest.split(" ",1)
            if len(p)==2 and p[0].isdigit():
                for _ in range(min(int(p[0]), 5)):
                    m = await message.channel.send(p[1])
                    try: await m.delete()
                    except: pass

        elif cmd=="tts": await message.channel.send(rest,tts=True)

        elif cmd=="calc":
            try:
                r=eval(rest,{"__builtins__":{}},{})
                await message.channel.send(ansi(f"{CYAN}{BOLD}🧮{RESET} {WHITE}{rest}{RESET} = {GREEN}{r}{RESET}"))
            except: await message.channel.send(ansi(f"{RED}Invalid expression.{RESET}"))

        elif cmd=="hash":
            if not rest: await message.channel.send(ansi(f"{RED}Usage: {prefix}hash <text>{RESET}")); return
            md=hashlib.md5(rest.encode()).hexdigest()
            sh=hashlib.sha256(rest.encode()).hexdigest()[:24]+"..."
            await message.channel.send(box("🔒 Hash Block",[("MD5",md),("SHA256",sh)],c=PURPLE))

        elif cmd=="math":
            try:
                val=float(rest)
                await message.channel.send(box("📐 Math Output",[("SqRoot",str(round(math.sqrt(val),4))),("Log10",str(round(math.log10(val),4)))],c=BLUE))
            except: await message.channel.send(ansi(f"{RED}Provide a clear baseline absolute positive float.{RESET}"))

        elif cmd=="pwdgen":
            sz=int(rest) if rest.isdigit() else 14
            sz=min(max(sz,6),64)
            chars="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*"
            pwd="".join(random.choice(chars) for _ in range(sz))
            await message.channel.send(ansi(f"{GREEN}{BOLD}🔑 Generated Secure Key:{RESET}\n{WHITE}{pwd}{RESET}"))

        elif cmd=="charcount":
            await message.channel.send(ansi(f"{CYAN}{BOLD}📝 Metrics:{RESET} Text contains {GREEN}{len(rest)}{RESET} total characters."))

        elif cmd=="b64enc":
            await message.channel.send(ansi(f"{CYAN}{BOLD}🔒 B64{RESET}\n{WHITE}{base64.b64encode(rest.encode()).decode()}{RESET}"))

        elif cmd=="b64dec":
            try: await message.channel.send(ansi(f"{CYAN}{BOLD}🔓 B64{RESET}\n{WHITE}{base64.b64decode(rest.encode()).decode()}{RESET}"))
            except: await message.channel.send(ansi(f"{RED}Invalid base64.{RESET}"))

        elif cmd=="color":
            h=rest.strip("#")
            try:
                r,g,b=int(h[0:2],16),int(h[2:4],16),int(h[4:6],16)
                await message.channel.send(ansi(f"{CYAN}{BOLD}🎨 #{h.upper()}{RESET}\n{RED}R:{r}{RESET}  {GREEN}G:{g}{RESET}  {BLUE}B:{b}{RESET}"))
            except: await message.channel.send(ansi(f"{RED}Usage: {prefix}color <hex>{RESET}"))

        elif cmd=="fakepurge":
            num = rest if rest.isdigit() else "50"
            m = await message.channel.send(ansi(f"{YELLOW}⏳ Purging last {num} channel records...{RESET}"))
            await asyncio.sleep(0.8)
            await m.edit(content=ansi(f"{GREEN}✓ Action complete. successfully cleared {num} metadata frames.{RESET}"))

        elif cmd=="fakelock":
            await message.channel.send(ansi(f"{RED}{BOLD}🛑 [SYSTEM WARNING]{RESET}\nChannel has been forcefully locked to verification tier 4. Write access denied."))

        elif cmd=="fakeslow":
            sec = rest if rest.isdigit() else "5"
            await message.channel.send(ansi(f"{BLUE}⚙️ [CHANNEL ADJUST]{RESET}\nSlowmode value configuration changed to {sec} seconds."))

        # ━━━ REAL MODERATION COMMAND TIERS (r-) ━━━
        elif cmd=="r-kick":
            if not message.guild: await message.channel.send(ansi(f"{RED}Not in a server.{RESET}")); return
            if not message.guild.me.guild_permissions.kick_members:
                await message.channel.send(ansi(f"{RED}Error: Missing Account Kick Perms.{RESET}")); return
            t = message.mentions[0] if message.mentions else None
            if not t and rest.split():
                try: t = await message.guild.fetch_member(int(rest.split()[0]))
                except: pass
            if not t: await message.channel.send(ansi(f"{RED}Usage: {prefix}r-kick <@user/ID> [reason]{RESET}")); return
            reas = " ".join(rest.split()[1:]) if len(rest.split()) > 1 else "No reason provided."
            try:
                await t.kick(reason=reas)
                await message.channel.send(ansi(f"{GREEN}{BOLD}🔨 Kicked Member:{RESET} {WHITE}{t} | Reason: {reas}{RESET}"))
            except Exception as e: await message.channel.send(ansi(f"{RED}Execution Failed: {e}{RESET}"))

        elif cmd=="r-ban":
            if not message.guild: await message.channel.send(ansi(f"{RED}Not in a server.{RESET}")); return
            if not message.guild.me.guild_permissions.ban_members:
                await message.channel.send(ansi(f"{RED}Error: Missing Account Ban Perms.{RESET}")); return
            t = message.mentions[0] if message.mentions else None
            if not t and rest.split():
                try: t = await message.guild.fetch_member(int(rest.split()[0]))
                except:
                    try: t = await client.fetch_user(int(rest.split()[0]))
                    except: pass
            if not t: await message.channel.send(ansi(f"{RED}Usage: {prefix}r-ban <@user/ID> [reason]{RESET}")); return
            reas = " ".join(rest.split()[1:]) if len(rest.split()) > 1 else "No reason provided."
            try:
                await message.guild.ban(t, reason=reas)
                await message.channel.send(ansi(f"{RED}{BOLD}🛑 Banned Target:{RESET} {WHITE}{t} | Reason: {reas}{RESET}"))
            except Exception as e: await message.channel.send(ansi(f"{RED}Execution Failed: {e}{RESET}"))

        elif cmd=="r-unban":
            if not message.guild: await message.channel.send(ansi(f"{RED}Not in a server.{RESET}")); return
            if not message.guild.me.guild_permissions.ban_members:
                await message.channel.send(ansi(f"{RED}Error: Missing Account Ban Perms.{RESET}")); return
            if not rest: await message.channel.send(ansi(f"{RED}Usage: {prefix}r-unban <Name#Discrim or ID>{RESET}")); return
            ban_entries = [entry async for entry in message.guild.bans()]
            target_user = None
            for entry in ban_entries:
                u = entry.user
                if rest == str(u.id) or rest.lower() == f"{u.name.lower()}#{u.discriminator}":
                    target_user = u; break
            if not target_user: await message.channel.send(ansi(f"{RED}Target ban payload record not found.{RESET}")); return
            try:
                await message.guild.unban(target_user)
                await message.channel.send(ansi(f"{GREEN}{BOLD}✓ Unbanned Account:{RESET} {WHITE}{target_user}{RESET}"))
            except Exception as e: await message.channel.send(ansi(f"{RED}Execution Failed: {e}{RESET}"))

        elif cmd=="r-mute":
            if not message.guild: await message.channel.send(ansi(f"{RED}Not in a server.{RESET}")); return
            if not message.guild.me.guild_permissions.moderate_members:
                await message.channel.send(ansi(f"{RED}Error: Missing Timeout Perms.{RESET}")); return
            t = message.mentions[0] if message.mentions else None
            p = rest.split()
            if not t and p:
                try: t = await message.guild.fetch_member(int(p[0]))
                except: pass
            if not t: await message.channel.send(ansi(f"{RED}Usage: {prefix}r-mute <@user/ID> [minutes]{RESET}")); return
            mins = int(p[1]) if len(p) > 1 and p[1].isdigit() else 10
            try:
                dur = datetime.timedelta(minutes=mins)
                await t.timeout(dur, reason="Selfbot active mute modifier")
                await message.channel.send(ansi(f"{YELLOW}{BOLD}🔇 Native Timeout Active:{RESET} {WHITE}{t} for {mins}m{RESET}"))
            except Exception as e:
                try:
                    await t.timeout(datetime.timedelta(minutes=mins), reason="Selfbot active mute modifier")
                    await message.channel.send(ansi(f"{YELLOW}{BOLD}🔇 Native Timeout Active:{RESET} {WHITE}{t} for {mins}m{RESET}"))
                except Exception as inner_e: await message.channel.send(ansi(f"{RED}Execution Failed: {inner_e}{RESET}"))

        elif cmd=="r-unmute":
            if not message.guild: await message.channel.send(ansi(f"{RED}Not in a server.{RESET}")); return
            if not message.guild.me.guild_permissions.moderate_members:
                await message.channel.send(ansi(f"{RED}Error: Missing Timeout Perms.{RESET}")); return
            t = message.mentions[0] if message.mentions else None
            if not t and rest.strip().isdigit():
                try: t = await message.guild.fetch_member(int(rest.strip()))
                except: pass
            if not t: await message.channel.send(ansi(f"{RED}Usage: {prefix}r-unmute <@user/ID>{RESET}")); return
            try:
                await t.timeout(None, reason="Selfbot timeout lift request")
                await message.channel.send(ansi(f"{GREEN}{BOLD}🔊 Native Timeout Cleared:{RESET} {WHITE}{t}{RESET}"))
            except Exception as e: await message.channel.send(ansi(f"{RED}Execution Failed: {e}{RESET}"))

        elif cmd=="r-purge":
            if not message.guild: await message.channel.send(ansi(f"{RED}Not in a server.{RESET}")); return
            if not message.channel.permissions_for(message.guild.me).manage_messages:
                await message.channel.send(ansi(f"{RED}Error: Missing Channel Manage Messages Perms.{RESET}")); return
            count = int(rest) if rest.isdigit() else 10
            count = min(count, 100) # Safety limit capping API request rates
            try:
                deleted = await message.channel.purge(limit=count)
                m = await message.channel.send(ansi(f"{GREEN}{BOLD}🗑️ Purge Active:{RESET} Cleaned {len(deleted)} historical messages.{RESET}"))
                await asyncio.sleep(2); await m.delete()
            except Exception as e:
                # Selfbots can selectively delete individual message histories if general bulk purge methods fail
                try:
                    idx = 0
                    async for msg in message.channel.history(limit=count):
                        if msg.author == client.user or message.channel.permissions_for(message.guild.me).manage_messages:
                            await msg.delete(); idx += 1; await asyncio.sleep(0.2)
                    m = await message.channel.send(ansi(f"{GREEN}{BOLD}🗑️ Manual Purge Active:{RESET} Cleaned {idx} text entries.{RESET}"))
                    await asyncio.sleep(2); await m.delete()
                except Exception as err: await message.channel.send(ansi(f"{RED}Execution Failed: {err}{RESET}"))

if __name__ == "__main__":
    # Executable runtime integration loop matching main.py logic
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    CONF_PATH = os.path.join(BASE_DIR, "config", "config.json")
    
    if os.path.exists(CONF_PATH):
        with open(CONF_PATH) as f:
            cfg = json.load(f)
        
        user_token = cfg.get("token")
        if user_token:
            print("[Selfbot Dev] Starting async gateway loop...")
            sys.stdout.flush()
            # discord.py-self compatibility fallback
            bot_client = discord.Client()
            setup_selfbot_commands(bot_client, cfg)
            try:
                bot_client.run(user_token)
            except Exception as err:
                print(f"[Selfbot Dev] Runtime Exception Encountered: {err}")
                sys.stdout.flush()
        else:
            print("[Selfbot Dev] Missing runtime 'token' setup within config.json")
            sys.stdout.flush()
    else:
        print("[Selfbot Dev] Target config file configuration absolute path not found")
        sys.stdout.flush()