<script lang="ts">
    import {YoutubeRepo} from '@/repositories/inject';
    import {researchVideoIds, selectedVideoId, transcripts, videos} from '@/store';
    import ChunkInfo from '@/components/ChunkInfo.svelte';
    import TextToParagraph from '@/components/TextToParagraph.svelte';
    import {isEmpty} from 'lodash';
    import LearnJapaneseItem from './LearnJapaneseItem.svelte';

    $: localVideos = $researchVideoIds
        .map(video_id => $videos.find(v => v.video_id === video_id))
        .filter(Boolean);

    const onSelectVideo = async (video_id: string) => {
        selectedVideoId.set(video_id);
        transcripts.set(await YoutubeRepo.getVideoTranscript(video_id));
    };
</script>

<div class="flex flex-col gap-5">
    <ul class="list h-[5rem] overflow-y-scroll">
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

    <div class="overflow-y-scroll" style="height: calc(100vh - 17rem)">
        {#each $transcripts as transcript}
            <div class="pb-8 flex flex-col gap-3">
                <div class="bg-slate-600">
                    <ChunkInfo chunk={{video_id: $selectedVideoId, ...transcript}} />
                </div>
                <div class="text-md leading-7">
                    {#if isEmpty(transcript.learn_japanese)}
                        <TextToParagraph text={transcript.text} />
                    {:else}
                        {#each transcript.learn_japanese as learn, i}
                            <LearnJapaneseItem item={learn} />
                            {#if i < transcript.learn_japanese.length - 1}
                                <hr class="my-3"/>
                            {/if}
                        {/each}
                    {/if}
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
