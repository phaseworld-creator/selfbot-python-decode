import discord, platform, psutil, time, random, asyncio, base64

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
            await client._plugin_handler(message); return
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
                (f"{prefix}spoiler","||spoiler||"),
                ("FUN",""), (f"{prefix}coinflip","Heads/tails"), (f"{prefix}8ball","8-ball"),
                (f"{prefix}roll","Roll dice"), (f"{prefix}choose","Pick option"),
                (f"{prefix}rate","Rate /10"), (f"{prefix}roast","Roast"), (f"{prefix}compliment","Compliment"),
                (f"{prefix}fact","Random fact"), (f"{prefix}ship","Ship users"),
                (f"{prefix}iq","Random IQ"), (f"{prefix}pp","pp size"),
                ("ACCOUNT",""), (f"{prefix}avatar","Avatar URL"), (f"{prefix}serverinfo","Server info"),
                (f"{prefix}userinfo","User info"), (f"{prefix}servers","List servers"),
                ("SPAM",""), (f"{prefix}spam","Spam N times"), (f"{prefix}tts","TTS message"),
                ("UTIL",""), (f"{prefix}calc","Calculator"), (f"{prefix}b64enc","B64 encode"),
                (f"{prefix}b64dec","B64 decode"), (f"{prefix}color","Hex color info"),
            ]
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
            if rest.lower() == "jayden":
                await message.channel.send(ansi(f"{CYAN}{BOLD}⭐ Jayden{RESET}\n{GREEN}██████████ ∞/10{RESET}"))
            if rest.lower() == "nighty":
                await message.channel.send(ansi(f"{CYAN}{BOLD}⭐ Nighty{RESET}\n{GREEN}██████████ ∞/10{RESET}"))
            if rest.lower() == "adam":
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
            if rest.lower() == "jayden":
                await message.channel.send(ansi(f"{YELLOW}{BOLD}📏 Jayden pp:{RESET}\n{WHITE}8{"="*100}D{RESET}"))
            else:
                sz=random.randint(0,20)
                await message.channel.send(ansi(f"{YELLOW}{BOLD}📏 {rest or 'Your'} pp:{RESET}\n{WHITE}8{'='*sz}D{RESET}"))

        elif cmd=="avatar":
            t=message.mentions[0] if message.mentions else message.author
            await message.channel.send(ansi(f"{CYAN}{BOLD}🖼 {t}'s Avatar{RESET}\n{WHITE}{t.display_avatar.url}{RESET}"))

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
            guilds=sorted(client.guilds,key=lambda g:g.member_count,reverse=True)[:15]
            body=f"{CYAN}{BOLD}🌐 Servers ({len(client.guilds)}){RESET}\n{CYAN}{'─'*36}{RESET}\n"
            for g in guilds: body+=f"  {WHITE}{g.name:<28}{YELLOW}{g.member_count}{RESET}\n"
            await message.channel.send(ansi(body))

        elif cmd=="spam":
            p=rest.split(" ",1)
            if len(p)==2 and p[0].isdigit():
                for _ in range(min(int(p[0]),8)):
                    await message.channel.send(p[1]); await asyncio.sleep(0.7)

        elif cmd=="tts": await message.channel.send(rest,tts=True)

        elif cmd=="calc":
            try:
                r=eval(rest,{"__builtins__":{}},{})
                await message.channel.send(ansi(f"{CYAN}{BOLD}🧮{RESET} {WHITE}{rest}{RESET} = {GREEN}{r}{RESET}"))
            except: await message.channel.send(ansi(f"{RED}Invalid expression.{RESET}"))

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
