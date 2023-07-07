<script lang="ts">
    import {AppRail, AppRailTile, AppShell, Modal, drawerStore} from '@skeletonlabs/skeleton';
    import {onMount} from 'svelte';
    import SimilarityView from './components/SimilarityView.svelte';
    import LeftDrawer from './components/LeftDrawer.svelte';
    import {
        currentTile,
        getVideos,
        loadLocalStorage,
        researchVideoIds,
        showYtPlayer,
        tileOptions,
        ytVideoShow,
    } from '@/store';
    import TranscriptView from './components/TranscriptView.svelte';
    import ScratchpadView from './components/ScratchpadView.svelte';
    import DraftingView from './components/DraftingView.svelte';
    import {Tile} from './repositories/types';
    import YoutubeView from './components/YoutubeView.svelte';
    import GeneralKnowledgeView from './components/GeneralKnowledgeView.svelte';

    onMount(async () => {
        loadLocalStorage();
        getVideos();
    });

    const openLeftDrawer = () => {
        drawerStore.open({id: 'left-drawer'});
    };
</script>

<Modal />
<LeftDrawer />

<AppShell>
    <svelte:fragment slot="sidebarLeft">
        <AppRail>
            <svelte:fragment slot="lead">
                <div />
            </svelte:fragment>
            {#each tileOptions as tile}
                <AppRailTile
                    bind:group={$currentTile}
                    name={tile}
                    value={tile}
                    title={tile}
                    active={tile === Tile.Extend ? 'bg-secondary-active-token' : undefined}
                >
                    <span>{tile}</span>
                </AppRailTile>
            {/each}
            <svelte:fragment slot="trail">
                <AppRailTile
                    active="select-videos"
                    group="select-videos"
                    name="select-videos"
                    value="select-video"
                    title="Videos"
                    on:click={() => openLeftDrawer()}
                >
                    <span>Videos</span>
                </AppRailTile>
            </svelte:fragment>
        </AppRail>
    </svelte:fragment>

    <div class="container mx-auto p-5 min-h-screen">
        <div class="grid grid-cols-[1fr,1fr] gap-5">
            {#if [Tile.Transcripts, Tile.Similarity].includes($currentTile)}
                {#if $researchVideoIds.length === 0}
                    <div>
                        <h5>Select some Videos (bottom left) to start Research</h5>
                    </div>
                {:else}
                    <div>
                        {#if $currentTile == Tile.Transcripts}
                            <TranscriptView />
                        {:else if $currentTile == Tile.Similarity}
                            <SimilarityView />
                        {/if}
                    </div>
                {/if}
            {/if}
            {#if $currentTile == Tile.GeneralKnowledge}
                <div>
                    <GeneralKnowledgeView />
                </div>
            {/if}
            <div>
                <ScratchpadView />
            </div>
            {#if $currentTile == Tile.Extend}
                <div>
                    <DraftingView />
                </div>
            {/if}
        </div>
    </div>
    <div class="fixed bottom-3 right-3" class:invisible={$ytVideoShow === false}>
        <YoutubeView />
    </div>
    {#if $ytVideoShow === false}
        <div class="fixed bottom-3 right-3">
            <button on:click={() => showYtPlayer()}>Show Yt</button>
        </div>
    {/if}
</AppShell>
