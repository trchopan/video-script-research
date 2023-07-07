<script lang="ts">
    import {YoutubeRepo} from '@/repositories/inject';
    import {researchVideoIds, selectedVideoId, transcripts, videos} from '@/store';
    import TextToParagraph from './TextToParagraph.svelte';
    import ChunkInfo from './ChunkInfo.svelte';

    $: localVideos = $researchVideoIds
        .map(video_id => $videos.find(v => v.video_id === video_id))
        .filter(Boolean);

    const onSelectVideo = async (video_id: string) => {
        selectedVideoId.set(video_id);
        transcripts.set(await YoutubeRepo.getVideoTranscript(video_id));
    };
</script>

<div class="flex flex-col gap-5">
    <ul class="list h-[20vh] overflow-y-scroll">
        {#each localVideos as video}
            <!-- svelte-ignore a11y-click-events-have-key-events -->
            <li class:selected={$selectedVideoId === video.video_id}>
                <div
                    class="cursor-pointer w-full flex gap-3 items-center"
                    on:click={() => onSelectVideo(video.video_id)}
                >
                    <div class="w-32 h-20 flex items-center pl-3">
                        <img src={video.thumbnail} class="object-cover" alt={video.title} />
                    </div>
                    <div class="w-full">
                        <span class="flex-auto">{video.title}</span>
                    </div>
                </div>
                <div class="w-7 pr-3">
                    <a href={`https://www.youtube.com/watch?v=${video.video_id}`} target="_blank">
                        <span class="text-sm material-icons"> open_in_new </span>
                    </a>
                </div>
            </li>
        {/each}
    </ul>

    <hr />

    <div class="h-[70vh] overflow-y-scroll">
        {#each $transcripts as transcript}
            <div class="pb-8 flex flex-col gap-3">
                <ChunkInfo chunk={{video_id: $selectedVideoId, ...transcript}} />
                <div class="text-md leading-7">
                    <TextToParagraph text={transcript.text} />
                </div>
                <hr />
            </div>
        {/each}
    </div>
</div>

<style>
    .selected {
        @apply bg-red-500;
    }
</style>
