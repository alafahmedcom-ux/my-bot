
ai_client = Groq(api_key=GROQ_API_KEY)

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f"Logged in as {client.user}")

@client.event
async def on_message(message):
    if message.author.bot:
        return

    bot = client.user

    content = message.content

    # =========================
    # FIX: detect ALL mention types
    # =========================

    real_mention = bot in message.mentions
    raw_mention = f"<@{bot.id}>" in content or f"<@!{bot.id}>" in content

    # 🔥 NEW FIX: detect "fake mention" (text only)
    text_mention = bot.name.lower() in content.lower()

    is_dm = isinstance(message.channel, discord.DMChannel)

    if not (is_dm or real_mention or raw_mention or text_mention):
        return

    # =========================
    # CLEAN PROMPT
    # =========================
    prompt = content
    prompt = prompt.replace(f"<@{bot.id}>", "")
    prompt = prompt.replace(f"<@!{bot.id}>", "")

    for m in message.mentions:
        prompt = prompt.replace(m.mention, "")

    # also remove name mention
    prompt = prompt.replace(bot.name, "")

    prompt = prompt.strip()

    if not prompt:
        await message.reply("Ask me something 🙂")
        return

    # randomness so it doesn't repeat
    seed = random.randint(1, 999999)
    prompt = f"(seed {seed}) {prompt}"

    async with message.channel.typing():
        try:
            completion = ai_client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant. Always vary responses and never repeat wording."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=1.2,
                top_p=0.95,
                max_tokens=1024
            )

            answer = completion.choices[0].message.content

            await message.reply(answer or "No response.")

        except Exception as e:
            print("ERROR:", repr(e))
            await message.reply("Error generating response.")

client.run(DISCORD_TOKEN)
