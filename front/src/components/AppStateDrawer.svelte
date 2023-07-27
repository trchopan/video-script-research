<script lang="ts">
    import Loading from './Loading.svelte';
    import {AppStateRepo} from '@/repositories/inject';
    import type {AppState} from '@/repositories/types';
    import {currentAppId} from '@/store';
    import {onMount} from 'svelte';

    let loading: boolean = false;
    let name: string = '';
    let appStates: AppState[] = [];

    const loadAppStates = async () => {
        appStates = await AppStateRepo.list();
    };

    const onCreateAppState = async () => {
        await AppStateRepo.create(name, {});
        await loadAppStates();
    };

    const onSelectAppState = async (app_id: string) => {
        currentAppId.set(app_id);
    };

    const onDeleteAppState = async (app_id: string) => {
        await AppStateRepo.delete(app_id);
        await loadAppStates();
    };

    let editingAppId = '';
    let editName = '';
    const onEdit = (app_id: string, appState: AppState) => {
        editingAppId = app_id;
        editName = appState.name;
    };
    const onSave = async (app_id: string) => {
        await AppStateRepo.saveName(app_id, editName);
        editName = '';
        editingAppId = '';
        loadAppStates();
    };

    onMount(() => {
        loadAppStates();
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
            <!-- svelte-ignore a11y-no-noninteractive-element-to-interactive-role -->
            <li
                class="px-3 flex place-content-between items-center"
                role="button"
                on:click={() => onSelectAppState(appState.app_id)}
            >
                {#if editingAppId === appState.app_id}
                    <input
                        bind:value={editName}
                        class="input"
                        type="text"
                        placeholder={appState.name}
                    />
                {:else}
                    <div class="cursor-pointer" class:selected={$currentAppId === appState.app_id}>
                        {appState.name || '<Empty Name>'}
                    </div>
                {/if}
                <div class="flex gap-3">
                    {#if editingAppId === appState.app_id}
                        <button
                            type="button"
                            class="btn-icon btn-icon-sm"
                            on:click={() => onSave(appState.app_id)}
                        >
                            <span class="text-sm material-icons">save</span>
                        </button>
                    {:else}
                        <button
                            type="button"
                            class="btn-icon btn-icon-sm"
                            on:click={() => onEdit(appState.app_id, appState)}
                        >
                            <span class="text-sm material-icons">edit</span>
                        </button>
                    {/if}
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
