const {Client, IntentsBitField, SlashCommandBuilder, ActivityType, ChannelType, EmbedBuilder} = require("discord.js")
const youtubesearchapi = require("youtube-search-api");
const ytdl = require("@distube/ytdl-core");
const {  createAudioPlayer, createAudioResource, joinVoiceChannel } = require("@discordjs/voice");
const embeds = require('./embeds.js');
require("dotenv").config()


// Intents
const intents = [IntentsBitField.Flags.GuildMembers, IntentsBitField.Flags.GuildPresences, IntentsBitField.Flags.GuildVoiceStates]


// Queue
const queue = new Map();


// Client Login
const client = new Client({
    intents: intents
})
client.login(process.env.TOKEN)


// On the client ready event
client.on("ready", () => {
    console.log("Client is ready")
    client.user.setPresence({
        activities: [{ name: `The Best Music`, type: ActivityType.Playing}],
        status: 'online',
      });
    setInterval(check_queue, 1000);
})


// Slash Command Setup
const data = new SlashCommandBuilder()
    .setName('play')
    .setDescription('Plays any music from music name or URL')
    .addStringOption((option) =>
    option
        .setName('name')
        .setDescription('Name or URL of Music to play')
        .setRequired(true)
        .setAutocomplete(true)
);


// Command AutoComplete
client.on("interactionCreate", async (interaction) => {
    if(!interaction.isAutocomplete() || interaction.commandName !== "play") return;

    const music_name = interaction.options.getString("name")
    let music_names = []


    await youtubesearchapi.GetListByKeyword(music_name, false).then((result) => {
        for (let i = 0; i < result.items.length; i++) {
            if (result.items[i].type !== "video") continue
            if (music_names.length >= 10) break

            music_names.push({
                name: result.items[i].title,
                value: result.items[i].id
            })
        }
    });

    interaction.respond(music_names).catch(() => {})
})



// Command Executed
client.on("interactionCreate", async (interaction) => {
    if (!interaction.isCommand() || interaction.commandName !== 'play') return;
    await interaction.deferReply()

    const {music_title, audioFormat, info, streamOptions} = await prepare_music(interaction);

    // Add the music to the queue
    if (queue.has(interaction.guildId) === false)
    {
        queue.set(interaction.guildId, [{"interaction": interaction, "playing": false, "music_title": music_title, "audioFormat": audioFormat, "info": info, "streamOptions": streamOptions}])
    }
    else
    {
        queue.get(interaction.guildId).push({"interaction": interaction, "playing": false, "music_title": music_title, "audioFormat": audioFormat, "info": info, "streamOptions": streamOptions})

        let embed = new EmbedBuilder()
        .setAuthor({
            name: "ADDED TO QUEUE"
        })
        .setTitle(info.videoDetails.title)
        .setURL(info.videoDetails.video_url)
        .setDescription(`\`\`\`${info.videoDetails.title} has been added in queue.\`\`\`\`\`\`Requested By: ${interaction.user.displayName}\`\`\`\`\`\`Queue No: ${queue.get(interaction.guildId).length}\`\`\``)
        .setThumbnail(info.videoDetails.thumbnails[0].url)
        .setColor("#00b0f4")
        .setFooter({
            text: "Dusic - The Ultimate Discord Music Bot",
            iconURL: client.user.avatarURL(),
        })
        .setTimestamp();
        
        interaction.followUp({embeds: [embed]}).catch(() => {})
    }
})


// We prepare the music details here like title, download info etc to speed up the queue
async function prepare_music(interaction)
{
    const music_name = interaction.options.getString("name");
    const {music_title, audioFormat, info, streamOptions} = await download_music(music_name);
    return {music_title, audioFormat, info, streamOptions}
}

// Download details of music
async function download_music(music_name)
{
    let info; // Declare info here

    // If the music name isn't full then we search and select the top result
    try {
        info = await ytdl.getInfo(music_name) // Assign value to info here
    } catch (error) {
        const result = await youtubesearchapi.GetListByKeyword(music_name, false)
        for (let i = 0; i < result.items.length; i++) {
            if (result.items[i].type !== "video") continue
    
            return await download_music(result.items[i].id)
        }
    }

    const music_title = info.videoDetails.title

    let audioFormats = ytdl.filterFormats(info.formats, 'audioonly');
    let audioFormat;
    let size = Infinity

    audioFormats.forEach(element => {
        if (element.contentLength < size) {
            audioFormat = element;
            size = element.contentLength;
        }
    })
    if (!audioFormat) return;

    const bufferSize = Math.floor(audioFormat.contentLength / 3);  // 1/3rd of the file size

    const streamOptions = { 
        format: audioFormat,
        highWaterMark: bufferSize
    };

    info.videoDetails

    return {music_title, audioFormat, info, streamOptions}
}

async function check_queue()
{
    for (const [guildId, queue_data] of queue.entries())
    {
        if (queue_data.length === 0)
        {
            queue.delete(guildId)
            continue
        }

        const data = queue_data[0]
        if (data.playing === true) continue

        data.playing = true
        play_music(data.interaction)
    }
}


async function play_music(interaction)
{
    // Join the voice channel
    const {player, connection} = await join_voice(interaction);
    if (!player || !connection) return;

    // Search the music
    const music_title = queue.get(interaction.guildId)[0]["music_title"];
    const audioFormat = queue.get(interaction.guildId)[0]["audioFormat"];
    const info = queue.get(interaction.guildId)[0]["info"];
    const streamOptions = queue.get(interaction.guildId)[0]["streamOptions"];

    if (!music_title || !audioFormat) interaction.followUp("Music not found");


    // Send embed
    let embed = new EmbedBuilder()
    .setAuthor({
        name: "NOW PLAYING"
    })
    .setTitle(music_title)
    .setURL(info.videoDetails.video_url)
    .setDescription(`\`\`\`${info.videoDetails.title} is being played now.\`\`\`\`\`\`Requested By: ${interaction.user.displayName}\`\`\``)
    .setThumbnail(info.videoDetails.thumbnails[0].url)
    .setColor("#00b0f4")
    .setFooter({
        text: "Dusic - The Ultimate Discord Music Bot",
        iconURL: client.user.avatarURL(),
    })
    .setTimestamp();
    
    interaction.followUp({embeds: [embed]}).catch(() => {})

    const stream = ytdl.downloadFromInfo(info, streamOptions);
    const resource = createAudioResource(stream);
    player.play(resource);
    connection.subscribe(player);

    

    player.on("idle", () => {
        queue.get(interaction.guildId).shift()
        let embed = new EmbedBuilder()
        .setAuthor({
            name: "FINISHED PLAYING"
        })
        .setTitle(music_title)
        .setURL(info.videoDetails.video_url)
        .setDescription(`\`\`\`${info.videoDetails.title} has finished playing.\`\`\``)
        .setThumbnail(info.videoDetails.thumbnails[0].url)
        .setColor("#00b0f4")
        .setFooter({
            text: "Dusic - The Ultimate Discord Music Bot",
            iconURL: client.user.avatarURL(),
        })
    });
}


async function join_voice(interaction)
{
    let guild = client.guilds.cache.get(interaction.guildId)
    if (!guild) guild = await client.guilds.fetch(interaction.guildId)
    if (!guild.channels.cache.size) await guild.channels.fetch()

    const voice_channel = guild.channels.cache.find(channel => channel.type === ChannelType.GuildVoice && channel.members.has(interaction.user.id))

    if (!voice_channel) return interaction.reply("You need to be in a voice channel to play music")

    const player = createAudioPlayer()
    const connection = joinVoiceChannel({
        channelId: voice_channel.id,
        guildId: voice_channel.guild.id,
        adapterCreator: voice_channel.guild.voiceAdapterCreator
    })

    return {player, connection}
}
