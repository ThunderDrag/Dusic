const {Client, IntentsBitField, SlashCommandBuilder, ActivityType, ChannelType} = require("discord.js")
const youtubesearchapi = require("youtube-search-api");
const ytdl = require("@distube/ytdl-core");
const {  createAudioPlayer, createAudioResource, joinVoiceChannel } = require("@discordjs/voice");
require("dotenv").config()


// Intents
const intents = [IntentsBitField.Flags.GuildMembers, IntentsBitField.Flags.GuildPresences, IntentsBitField.Flags.GuildVoiceStates]

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

async function download_music(music_name)
{
    const info = await ytdl.getInfo(music_name)
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

    return {music_title, audioFormat, info, streamOptions}
}

// Command Executed
client.on("interactionCreate", async (interaction) => {
    if (!interaction.isCommand() || interaction.commandName !== 'play') return;

    const music_name = interaction.options.getString("name")

    // Join the voice channel
    const {player, connection} = await join_voice(interaction)
    if (!player || !connection) return;

    // Search the music
    const {music_title, audioFormat, info, streamOptions} = await download_music(music_name)
    if (!music_title || !audioFormat) interaction.reply("Music not found");

    const stream = ytdl.downloadFromInfo(info, streamOptions);
    const resource = createAudioResource(stream);
    player.play(resource);
    connection.subscribe(player);

    interaction.reply(`Playing ${music_title}`)

})