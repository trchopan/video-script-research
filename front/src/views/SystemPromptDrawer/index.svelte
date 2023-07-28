<script lang="ts">
    import Loading from '@/components/Loading.svelte';
    import {SystemPromptRepo} from '@/repositories/inject';
    import type {SystemPrompt} from '@/repositories/types';
    import {onMount} from 'svelte';

    let loading: boolean = false;
    let name: string = '';
    let template: string = '';
    let systemPrompts: SystemPrompt[] = [];
    let editingPromptId: number | null = null;

    const loadSystemPrompts = async () => {
        systemPrompts = await SystemPromptRepo.list();
    };

    const onCreate = async () => {
        await SystemPromptRepo.create(name, template);
        await loadSystemPrompts();
    };

    const onSelectSystemPrompt = async (id: number) => {
        editingPromptId = id;
        const found = systemPrompts.find(p => p._id === id);
        if (!found) return;
        name = found.name;
        template = found.template;
    };

    const onDelete = async () => {
        await SystemPromptRepo.delete(editingPromptId);
        name = '';
        template = '';
        editingPromptId = null;
        await loadSystemPrompts();
    };

    const onSave = async () => {
        await SystemPromptRepo.save(editingPromptId, name, template);
        name = '';
        template = '';
        editingPromptId = null;
        loadSystemPrompts();
    };

    onMount(() => {
        loadSystemPrompts();
    });
</script>

<div>
    <Loading {loading}>
        <div class="flex flex-col gap-3">
            <div class="flex gap-5 items-center">
                <input
                    bind:value={name}
                    class="input"
                    type="text"
                    placeholder="System Prompt Name"
                />
                {#if editingPromptId === null}
                    <button on:click={() => onCreate()} class="btn variant-filled-primary"
                        >New</button
                    >
                {:else}
                    <button on:click={() => onSave()} class="btn variant-ringed-primary">
                        Save
                    </button>
                    <button on:click={() => onDelete()} class="btn variant-ringed-warning">
                        Delete
                    </button>
                {/if}
            </div>
            <textarea
                bind:value={template}
                class="textarea"
                placeholder="System Prompt Template"
                rows="5"
            />
        </div>
    </Loading>
    <ul class="list-nav max-h-[10rem]">
        {#each systemPrompts as prompt}
            <!-- svelte-ignore a11y-no-noninteractive-element-to-interactive-role -->
            <!-- svelte-ignore a11y-click-events-have-key-events -->
            <li
                class="px-3 py-2 flex place-content-between items-center"
                role="button"
                on:click={() => onSelectSystemPrompt(prompt._id)}
            >
                <div class="cursor-pointer" class:selected={editingPromptId === prompt._id}>
                    {prompt.name || '<Empty Name>'}
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
