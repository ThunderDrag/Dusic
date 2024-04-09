const {Client, IntentsBitField, SlashCommandBuilder, ActivityType, ChannelType} = require("discord.js")
const youtubesearchapi = require("youtube-search-api");
const ytdl = require("@distube/ytdl-core");
const {  createAudioPlayer, createAudioResource, joinVoiceChannel } = require("@discordjs/voice");
require("dotenv").config()


const global_queue = new Map();


// Client Login
const client = new Client({
    intents: [IntentsBitField.Flags.GuildMembers, IntentsBitField.Flags.GuildPresences, IntentsBitField.Flags.GuildVoiceStates],
})
client.login(process.env.TOKEN)



// On the client ready event
client.on("ready", () => {
    console.log("Client is ready")
    client.user.setPresence({
        activities: [{ name: `The Best Music`, type: ActivityType.Playing }],
        status: 'online',
      });
    client.guilds.cache.get('1162381824497037493').commands.create(data);
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
    if (interaction.isCommand() && interaction.commandName === 'play') {
        play_command_ran({ interaction });
        return;
    }
    
    if(!interaction.isAutocomplete()) return;
    if(interaction.commandName !== "play") return;

    const name = interaction.options.getString("name")
    let music_names = []

    await youtubesearchapi.GetListByKeyword(name, false).then((result) => {
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
async function play_command_ran({interaction}) {
    const name = interaction.options.getString("name")

    // Ensure this is the correct voice channel ID and the bot has access to it
    const voiceChannelId = '1162381825461731442'; // Replace with your actual voice channel ID

    try {
        const player = createAudioPlayer();
        const connection = joinVoiceChannel({
            channelId: voiceChannelId,
            guildId: interaction.guildId,
            adapterCreator: interaction.guild.voiceAdapterCreator,
        })
        
        ytdl.getInfo(name).then(info => {
            let audioFormats = ytdl.filterFormats(info.formats, 'audioonly');
            let audioFormat;
            let size = Infinity
            audioFormats.forEach(element => {
                if (element.contentLength < size) {
                    audioFormat = element;
                    size = element.contentLength;
                }
            });
        
            if (audioFormat) {
                const stream = ytdl.downloadFromInfo(info, { format: audioFormat });
                const resource = createAudioResource(stream);
                player.play(resource);
                connection.subscribe(player);
            }
        });
    } catch (error) {
        console.error(`Could not join the voice channel: ${error}`);
    }
}


function queue_task_executor()
{

}