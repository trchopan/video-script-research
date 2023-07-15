<script lang="ts">
    import Loading from './Loading.svelte';
    import {AppStateRepo} from '@/repositories/inject';
    import type {AppState} from '@/repositories/types';
    import {currentAppId} from '@/store';
    import {onMount} from 'svelte';

    let loading: boolean = false;
    let name: string = '';
    let appStates: AppState[] = [];

    const onCreateAppState = async () => {
        await AppStateRepo.create(name, {});
        await onLoadAppStates();
    };

    const onSelectAppState = async (app_id: string) => {
        currentAppId.set(app_id);
    };

    const onLoadAppStates = async () => {
        appStates = await AppStateRepo.list();
    };

    const onDeleteAppState = async (app_id: string) => {
        await AppStateRepo.delte(app_id);
        await onLoadAppStates();
    };

    onMount(() => {
        onLoadAppStates();
    });
</script>

<div>
    <Loading {loading}>
        <div class="flex gap-5 items-center">
            <input bind:value={name} class="input" type="text" placeholder="App State Name" />
            <button on:click={() => onCreateAppState()} class="btn variant-filled-primary">
                New
            </button>
        </div>
    </Loading>
    <ul class="list-nav max-h-[10rem]">
        {#each appStates as appState}
            <!-- svelte-ignore a11y-click-events-have-key-events -->
            <li
                class="px-3 flex place-content-between items-center"
                on:click={() => onSelectAppState(appState.app_id)}
            >
                <div class="cursor-pointer" class:selected={$currentAppId === appState.app_id}>
                    {appState.name || '<Empty Name>'}
                </div>
                <div>
                    <button
                        type="button"
                        class="btn-icon btn-icon-sm"
                        on:click={() => onDeleteAppState(appState.app_id)}
                    >
                        <span class="text-sm material-icons">delete</span>
                    </button>
                </div>
            </li>
        {/each}
    </ul>
</div>

<style>
    .selected {
        @apply text-red-400;
    }
</style>
