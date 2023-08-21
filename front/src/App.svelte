<script lang="ts">
    import {
        AppRail,
        AppRailAnchor,
        AppRailTile,
        AppShell,
        Drawer,
        Modal,
        drawerStore,
    } from '@skeletonlabs/skeleton';
    import {onMount} from 'svelte';
    import SimilarityView from './components/SimilarityView.svelte';
    import VideosDrawer from './components/VideosDrawer.svelte';
    import {
        currentAppId,
        currentTile,
        getVideos,
        loadAppState,
        researchVideoIds,
        showYtPlayer,
        tileOptions,
        ytVideoShow,
    } from '@/store';
    import TranscriptView from './components/TranscriptView.svelte';
    import ScratchpadView from './components/ScratchpadView.svelte';
    import WriteScriptView from './components/WriteScriptView.svelte';
    import {Tile} from './repositories/types';
    import YoutubeView from './components/YoutubeView.svelte';
    import AppStateDrawer from './components/AppStateDrawer.svelte';
    import GeneralKnowledgeView from './views/GeneralKnowledge/index.svelte';
    import ConversationView from './views/Conversation/index.svelte';
    import LearnJapaneseView from './views/LearnJapanese/index.svelte';
    import SystemPromptDrawer from './views/SystemPromptDrawer/index.svelte';

    onMount(async () => {
        loadAppState();
        getVideos();
    });
    let drawer = '';
    drawerStore.subscribe(s => {
        drawer = s.id;
    });
</script>

<Modal />
<Drawer width="w-[600px]">
    {#if drawer === 'videos-drawer'}
        <VideosDrawer />
    {:else if drawer === 'app-state-drawer'}
        <AppStateDrawer />
    {:else if drawer === 'system-prompt-drawer'}
        <SystemPromptDrawer />
    {/if}
</Drawer>

<AppShell>
    <svelte:fragment slot="sidebarLeft">
        <AppRail>
            <svelte:fragment slot="lead">
                <AppRailAnchor
                    class="cursor-pointer"
                    on:click={() => drawerStore.open({id: 'app-state-drawer'})}
                >
                    <span>App State</span>
                </AppRailAnchor>
            </svelte:fragment>
            {#if $currentAppId}
                {#each tileOptions as tile}
                    <AppRailTile bind:group={$currentTile} name={tile} value={tile} title={tile}>
                        <span>{tile}</span>
                    </AppRailTile>
                {/each}
            {/if}
            <svelte:fragment slot="trail">
                {#if $currentAppId}
                    <AppRailAnchor
                        class="cursor-pointer"
                        on:click={() => drawerStore.open({id: 'system-prompt-drawer'})}
                    >
                        <span>System Prompts</span>
                    </AppRailAnchor>
                    <AppRailAnchor
                        class="cursor-pointer"
                        on:click={() => drawerStore.open({id: 'videos-drawer'})}
                    >
                        <span>Videos</span>
                    </AppRailAnchor>
                {/if}
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
            {#if [Tile.Transcripts, Tile.Similarity, Tile.GeneralKnowledge, Tile.WriteScript].includes($currentTile)}
                <div>
                    <ScratchpadView />
                </div>
            {/if}
            {#if $currentTile == Tile.WriteScript}
                <div>
                    <WriteScriptView />
                </div>
            {/if}
            {#if $currentTile == Tile.Conversation}
                <div class="col-span-2">
                    <ConversationView />
                </div>
            {/if}
            {#if $currentTile == Tile.LearnJapanese}
                <div class="col-span-2">
                    <LearnJapaneseView />
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
