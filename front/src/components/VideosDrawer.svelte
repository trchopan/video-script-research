<script lang="ts">
    import {
        pullNewVideoTranscript,
        loadingNewVideoTranscript,
        researchVideoIds,
        videos,
        getVideos,
    } from '@/store';
    import Loading from './Loading.svelte';
    import {YoutubeRepo} from '@/repositories/inject';

    let youtubeUrl: string = '';
    let language: string = 'en';

    const onToggleResearchVideoIds = (video_id: string) => {
        if ($researchVideoIds.includes(video_id)) {
            researchVideoIds.set($researchVideoIds.filter(v => v != video_id));
        } else {
            researchVideoIds.set($researchVideoIds.concat(video_id));
        }
    };

    const onAddNewVideoTranscript = () => {
        pullNewVideoTranscript(youtubeUrl, language);
        youtubeUrl = '';
    };

    const onDeleteVideo = async (video_id: string) => {
        await YoutubeRepo.deleteVideo(video_id);
        await getVideos();
    };
</script>

<div>
    <Loading loading={$loadingNewVideoTranscript}>
        <div class="flex gap-5 items-center">
            <input bind:value={youtubeUrl} class="input" type="text" placeholder="Input" />
            <select bind:value={language} class="select w-[12rem]">
                <option value="en">English</option>
                <option value="ja">Japanese</option>
            </select>
            <button on:click={() => onAddNewVideoTranscript()} class="btn variant-ringed-secondary">
                Add
            </button>
        </div>
    </Loading>
    <ul class="list max-h-[10rem]">
        {#each $videos as video}
            <li class:selected={$researchVideoIds.includes(video.video_id)} class="flex gap-5">
                <!-- svelte-ignore a11y-click-events-have-key-events -->
                <div
                    on:click={() => onToggleResearchVideoIds(video.video_id)}
                    class="flex items-center gap-3 grow"
                >
                    <div class="w-32 h-20 flex items-center pl-3">
                        <img src={video.thumbnail} class="object-cover" alt={video.title} />
                    </div>
                    <div class="w-full">
                        <span class="flex-auto">{video.title}</span>
                    </div>
                </div>
                <button
                    on:click={() => onDeleteVideo(video.video_id)}
                    class="btn btn-icon text-red-400"
                >
                    <span class="text-sm material-icons">delete</span>
                </button>
            </li>
        {/each}
    </ul>
</div>

<style>
    .selected {
        @apply text-red-400;
    }
</style>
