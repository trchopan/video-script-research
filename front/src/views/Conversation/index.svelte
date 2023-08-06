<script lang="ts">
    import {ConversationRepo, SystemPromptRepo} from '@/repositories/inject';
    import {onMount, tick} from 'svelte';
    import {
        ConversationChatToolEnum,
        type Conversation,
        type ConversationChatToolsRecord,
    } from '@/repositories/types';
    import {cloneDeep, debounce} from 'lodash';
    import Loading from '@/components/Loading.svelte';
    import ConversationContent from './ConversationContent.svelte';
    import TextToParagraph from '@/components/TextToParagraph.svelte';
    import {popup} from '@skeletonlabs/skeleton';
    import Speak from '@/components/Speak.svelte';

    let chatRef: HTMLElement;
    let loadingName = false;
    let name = '';
    let loadingChat = false;
    let prefix = '';
    let chat = '';
    let localSystemPrompt = '';
    let selectedConversation: Conversation | null = null;
    let conversations = [];
    let templates = [];

    const loadConversation = async () => {
        conversations = await ConversationRepo.list();
    };

    const loadTemplates = async () => {
        templates = await SystemPromptRepo.list();
    };

    const conversationScrollIntoView = () => {
        chatRef.children.item(chatRef.children.length - 2)?.scrollIntoView({behavior: 'smooth'});
    };

    onMount(async () => {
        await loadConversation();
        await loadTemplates();
    });

    const onResetFieldsForCreate = () => {
        selectedConversation = null;
        name = '';
    };

    const onCreateConversation = async () => {
        await ConversationRepo.create(name);
        await loadConversation();
        name = '';
    };

    const onSaveConversation = async () => {
        selectedConversation = await ConversationRepo.saveName(
            selectedConversation.conversation_id,
            name
        );
        const index = conversations.findIndex(
            c => c.conversation_id === selectedConversation.conversation_id
        );
        conversations[index] = cloneDeep(selectedConversation);
    };

    const onDeleteConversation = async () => {
        await ConversationRepo.delete(selectedConversation.conversation_id);
        if (selectedConversation.conversation_id === selectedConversation.conversation_id) {
            selectedConversation = null;
        }
        await loadConversation();
    };

    const onSelectConversation = async (conversation_id: string) => {
        selectedConversation = await ConversationRepo.get(conversation_id);
        localSystemPrompt = selectedConversation.system_prompt;
        name = selectedConversation.name;
        await tick();
        conversationScrollIntoView();
    };

    $: isSystemPromptChanged = localSystemPrompt !== selectedConversation?.system_prompt;

    const onSaveSystemPrompt = async () => {
        selectedConversation = await ConversationRepo.saveSystemPrompt(
            selectedConversation.conversation_id,
            localSystemPrompt
        );
    };

    const onUndoSystemPrompt = async () => {
        localSystemPrompt = selectedConversation.system_prompt;
    };

    const onSelectTemplate = async (template: string) => {
        localSystemPrompt = template;
    };

    let tools: ConversationChatToolEnum[] = [
        ConversationChatToolEnum.Wikipedia,
        ConversationChatToolEnum.DuckduckGo,
        ConversationChatToolEnum.Youtube,
    ];

    interface ToolOption {
        name: string;
        value: ConversationChatToolEnum;
    }
    const toolOptions: ToolOption[] = [
        {name: 'Wikipedia', value: ConversationChatToolEnum.Wikipedia},
        {name: 'Duckduck Go', value: ConversationChatToolEnum.DuckduckGo},
        {name: 'Youtube', value: ConversationChatToolEnum.Youtube},
    ];

    const onSelectToolOption = (opt: ToolOption) => {
        if (tools.includes(opt.value)) {
            tools = tools.filter(t => t !== opt.value);
        } else {
            tools = tools.concat(opt.value);
        }
    };

    const onChat = async () => {
        loadingChat = true;
        const _tools = tools.reduce((acc, cur) => {
            acc[cur] = {};
            return acc;
        }, {} as ConversationChatToolsRecord);
        try {
            const _prefix = prefix ? prefix + '\n' : '';
            selectedConversation = await ConversationRepo.chat(
                selectedConversation.conversation_id,
                _prefix + chat,
                _tools
            );
            await tick();
            conversationScrollIntoView();
            chat = '';
        } finally {
            loadingChat = false;
        }
    };

    const onDeleteMemory = async (index: number) => {
        const newMemory = cloneDeep(selectedConversation.memory);
        newMemory.splice(index, 2);
        selectedConversation.memory = newMemory;
        selectedConversation = await ConversationRepo.saveMemory(
            selectedConversation.conversation_id,
            selectedConversation.memory
        );
    };

    const onCopyContent = async (index: number) => {
        console.log('>>>', selectedConversation.memory[index].data.content);
    };

    const onTranscript = (transcript: string) => {
        chat += '\n---\n' + transcript;
    };

    let reorder = false;

    const swapConversation = (curIndex: number, swapIndex: number) => {
        const temp_conv = conversations[curIndex];
        conversations[curIndex] = conversations[swapIndex];
        conversations[swapIndex] = temp_conv;
    };
    const onMoveConversationUp = (index: number) => {
        if (index === 0) return;
        swapConversation(index, index - 1);
        debouncedUpdateOrders();
    };

    const onMoveConversationDown = (index: number) => {
        if (index === conversations.length - 1) return;
        swapConversation(index, index + 1);
        debouncedUpdateOrders();
    };

    const debouncedUpdateOrders = debounce(async () => {
        conversations = await ConversationRepo.updateOrders(
            conversations.map((conv, index) => ({
                conversation_id: conv.conversation_id,
                order: conversations.length - 1 - index,
            }))
        );
    }, 500);
</script>

<div class="grid grid-cols-[1fr,1.5fr] gap-5 h-[95vh] overflow-y-hidden">
    <div class="flex flex-col gap-5 overflow-y-scroll">
        <Loading loading={loadingName}>
            <div class="flex gap-3">
                <button on:click={() => onResetFieldsForCreate()} class="btn btn-icon">
                    <span class="text-sm material-icons">add</span>
                </button>
                <button
                    on:click={() => (reorder = !reorder)}
                    class="btn btn-icon"
                    class:text-orange-400={reorder}
                >
                    <span class="text-sm material-icons">reorder</span>
                </button>
            </div>
            <div class="flex gap-1 items-center">
                <div class="w-full">
                    <input
                        bind:value={name}
                        class="input w-full"
                        type="text"
                        placeholder="New Conversation"
                    />
                </div>
                <div class="flex gap-1">
                    {#if selectedConversation === null}
                        <button
                            on:click={() => onCreateConversation()}
                            class="btn variant-filled-primary"
                        >
                            New
                        </button>
                    {:else}
                        <button
                            on:click={() => onSaveConversation()}
                            class="btn btn-icon text-orange-400"
                        >
                            <span class="text-sm material-icons">save</span>
                        </button>
                        <button
                            on:click={() => onDeleteConversation()}
                            class="btn btn-icon text-red-400"
                        >
                            <span class="text-sm material-icons">delete</span>
                        </button>
                    {/if}
                </div>
            </div>
        </Loading>
        <ul class="list max-h-[8rem] min-h-[6rem] overflow-y-scroll">
            {#each conversations as conversation, i}
                <li
                    class="flex px-5 hover:bg-primary-200/[0.1]"
                    class:selected={selectedConversation?.conversation_id ===
                        conversation.conversation_id}
                >
                    <!-- svelte-ignore a11y-interactive-supports-focus -->
                    <!-- svelte-ignore a11y-click-events-have-key-events -->
                    <div
                        role="button"
                        class="py-1 cursor-pointer w-full"
                        on:click={() => onSelectConversation(conversation.conversation_id)}
                    >
                        <span class="flex-auto">{conversation.name}</span>
                    </div>
                    {#if reorder}
                        <div class="flex gap-1">
                            {#if i > 0}
                                <button
                                    class="btn btn-icon btn-xs w-5"
                                    class:text-orange-400={reorder}
                                    on:click={() => onMoveConversationUp(i)}
                                >
                                    <span class="text-xs material-icons">keyboard_arrow_up</span>
                                </button>
                            {:else}
                                <div class="w-5" />
                            {/if}
                            {#if i < conversations.length - 1}
                                <button
                                    class="btn btn-icon btn-xs w-5"
                                    class:text-orange-400={reorder}
                                    on:click={() => onMoveConversationDown(i)}
                                >
                                    <span class="text-xs material-icons">keyboard_arrow_down</span>
                                </button>
                            {:else}
                                <div class="w-5" />
                            {/if}
                        </div>
                    {/if}
                </li>
            {/each}
        </ul>

        <hr />

        {#if selectedConversation}
            <div class="flex flex-wrap gap-3">
                {#each toolOptions as tOpt}
                    <button
                        type="button"
                        class="btn btn-sm"
                        class:variant-filled-primary={tools.includes(tOpt.value)}
                        on:click={() => onSelectToolOption(tOpt)}
                    >
                        {tOpt.name}
                    </button>
                {/each}
            </div>
            <hr />
            <div class="flex flex-col gap-5">
                <div>
                    <textarea
                        bind:value={localSystemPrompt}
                        class="textarea leading-7"
                        rows="4"
                        placeholder="System Prompt"
                    />
                    <div class="flex gap-3 items-start place-content-between">
                        <button
                            class="btn btn-sm variant-filled-primary"
                            use:popup={{
                                event: 'click',
                                target: 'popupFeatured',
                                placement: 'right',
                            }}
                        >
                            Template
                        </button>
                        <div
                            class="card p-5 shadow-xl z-10 max-h-[10rem] overflow-y-scroll"
                            data-popup="popupFeatured"
                        >
                            <ul class="list">
                                {#each templates as template}
                                    <li>
                                        <button
                                            type="button"
                                            class="btn btn-sm variant-ringed-primary"
                                            on:click={() => onSelectTemplate(template.template)}
                                        >
                                            {template.name}
                                        </button>
                                    </li>
                                {/each}
                            </ul>
                        </div>

                        {#if isSystemPromptChanged}
                            <div class="flex gap-3">
                                <button
                                    type="button"
                                    class="btn-icon btn-icon-sm-red-400"
                                    on:click={() => onUndoSystemPrompt()}
                                >
                                    <span class="text-sm material-icons">undo</span>
                                </button>
                                <button
                                    type="button"
                                    class="btn-icon btn-icon-sm text-red-400"
                                    on:click={() => onSaveSystemPrompt()}
                                >
                                    <span class="text-sm material-icons">save</span>
                                </button>
                            </div>
                        {/if}
                    </div>
                </div>
                <input
                    bind:value={prefix}
                    class="input"
                    type="text"
                    placeholder="Template ex: PARAGRAPH, CONTEXT"
                />
                <textarea
                    bind:value={chat}
                    class="textarea leading-7"
                    rows="5"
                    placeholder="New Chat"
                />
                <div class="flex gap-5">
                    <Speak transcriptCb={onTranscript} />
                    <button
                        on:click={() => onChat()}
                        class="btn variant-filled-primary w-full"
                        disabled={loadingChat}
                    >
                        Chat
                    </button>
                </div>
            </div>
        {/if}
    </div>
    <div class="relative h-full">
        <div class="absolute top-0 left-0 right-0 bottom-0 overflow-y-scroll flex flex-col gap-5">
            {#if selectedConversation}
                <div bind:this={chatRef} class="flex flex-col gap-3 text-md leading-7">
                    {#each selectedConversation.memory as memory, i}
                        {#if i % 2 == 0}
                            <hr />
                        {/if}
                        {#if memory.type == 'human'}
                            <div class="flex gap-2 place-content-between items-start text-pink-400">
                                <div class="conversation-content">
                                    <TextToParagraph text={memory.data.content} />
                                </div>
                                <button
                                    type="button"
                                    class="btn-icon btn-icon-sm text-orange-400"
                                    on:click={() => onDeleteMemory(i)}
                                >
                                    <span class="text-sm material-icons">delete</span>
                                </button>
                            </div>
                        {:else if memory.type == 'ai'}
                            <div class="text-blue-400 relative">
                                <div class="absolute right-0 top-[-1rem]">
                                    <button
                                        type="button"
                                        class="btn-icon btn-icon-sm text-green-400 hover:opacity-100 opacity-50"
                                        on:click={() => onCopyContent(i)}
                                    >
                                        <span class="text-sm material-icons">content_copy</span>
                                    </button>
                                </div>
                                <ConversationContent content={memory.data.content} />
                            </div>
                        {/if}
                    {/each}
                </div>
            {/if}
        </div>
    </div>
</div>

<style>
    .selected {
        @apply text-red-400;
    }
</style>
