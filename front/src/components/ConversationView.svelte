<script lang="ts">
    import {ConversationRepo} from '@/repositories/inject';
    import {onMount, tick} from 'svelte';
    import Loading from './Loading.svelte';
    import {
        ConversationChatToolEnum,
        type Conversation,
        type ConversationChatToolsRecord,
    } from '@/repositories/types';
    import {cloneDeep, noop} from 'lodash';
    import ConversationContent from './ConversationContent.svelte';

    let chatRef: HTMLElement;
    let loadingName = false;
    let name = '';
    let loadingChat = false;
    let chat = '';
    let localSystemPrompt = '';
    let selectedConversation: Conversation | null = null;
    let conversations = [];
    let templates = [];

    const loadConversation = async () => {
        conversations = await ConversationRepo.list();
    };

    const loadTemplates = async () => {
        templates = await ConversationRepo.templates();
    };

    const conversationScrollIntoView = () => {
        chatRef.children.item(chatRef.children.length - 2)?.scrollIntoView({behavior: 'smooth'});
    };

    onMount(async () => {
        await loadConversation();
        await loadTemplates();
    });

    const onCreateConversation = async () => {
        await ConversationRepo.create(name);
        await loadConversation();
        name = '';
    };

    const onDeleteConversation = async (conversation_id: string) => {
        await ConversationRepo.delete(conversation_id);
        await loadConversation();
        selectedConversation = null;
    };

    const onSelectConversation = async (conversation_id: string) => {
        selectedConversation = await ConversationRepo.get(conversation_id);
        selectedConversation.memory.forEach((m, i) =>
            i % 2 === 1 ? console.log(m.data.content) : console.log('-')
        );
        localSystemPrompt = selectedConversation.system_prompt;
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

    const onSelectTemplate = async (template: string) => {
        localSystemPrompt = template;
    };

    interface ToolOption {
        name: string;
        value: ConversationChatToolEnum;
    }
    let tools: ToolOption[] = [];
    const toolOptions: ToolOption[] = [
        {name: 'Wikipedia', value: ConversationChatToolEnum.Wikipedia},
        {name: 'DuckduckGo', value: ConversationChatToolEnum.DuckduckGo},
    ];

    const onSelectToolOption = (opt: ToolOption) => {
        if (tools.map(t => t.name).includes(opt.name)) {
            tools = tools.filter(t => t.name !== opt.name);
        } else {
            tools = tools.concat(opt);
        }
    };

    const onChat = async () => {
        loadingChat = true;
        const _tools = tools.reduce((acc, cur) => {
            acc[cur.value] = {};
            return acc;
        }, {} as ConversationChatToolsRecord);
        try {
            selectedConversation = await ConversationRepo.chat(
                selectedConversation.conversation_id,
                chat,
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
</script>

<div class="grid grid-cols-[1fr,1fr] gap-5 h-[95vh] overflow-y-hidden">
    <div class="flex flex-col gap-5 overflow-y-scroll">
        <Loading loading={loadingName}>
            <div class="flex gap-5 items-center">
                <input bind:value={name} class="input" type="text" placeholder="New Conversation" />
                <button on:click={() => onCreateConversation()} class="btn variant-filled-primary">
                    New
                </button>
            </div>
        </Loading>
        <ul class="list max-h-[8rem] min-h-[6rem] overflow-y-scroll">
            {#each conversations as conversation}
                <!-- svelte-ignore a11y-click-events-have-key-events -->
                <li class:selected={Math.random() > 0.8}>
                    <!-- svelte-ignore a11y-interactive-supports-focus -->
                    <div
                        class="cursor-pointer w-full flex gap-3 items-center"
                        role="button"
                        on:click={() => onSelectConversation(conversation.conversation_id)}
                    >
                        <div class="w-full">
                            <span class="flex-auto">{conversation.name}</span>
                        </div>
                    </div>
                    <button
                        type="button"
                        class="btn-icon btn-icon-sm"
                        on:click={() => onDeleteConversation(conversation.conversation_id)}
                    >
                        <span class="text-sm material-icons">delete</span>
                    </button>
                </li>
            {/each}
        </ul>

        <hr />

        {#if selectedConversation}
            <div>
                <select
                    class="select"
                    multiple
                    bind:value={tools}
                    on:click|preventDefault={() => noop()}
                >
                    {#each toolOptions as tOpt}
                        <option
                            value={tOpt}
                            on:mousedown|preventDefault={() => onSelectToolOption(tOpt)}
                        >
                            {tOpt.name}
                        </option>
                    {/each}
                </select>
            </div>
            <div class="flex flex-col gap-5">
                <textarea
                    bind:value={chat}
                    class="textarea leading-7"
                    rows="3"
                    placeholder="New Chat"
                />
                <button on:click={() => onChat()} class="btn variant-filled-primary"> Chat </button>
            </div>
        {/if}
    </div>
    <div class="relative h-full">
        <div class="absolute top-0 left-0 right-0 bottom-0 overflow-y-scroll flex flex-col gap-5">
            {#if selectedConversation}
                <div>
                    <textarea
                        bind:value={localSystemPrompt}
                        class="textarea leading-7"
                        rows="4"
                        placeholder="System Prompt"
                    />
                    <div class="flex gap-3">
                        {#each templates as template}
                            <button
                                type="button"
                                class="btn btn-sm variant-ringed-primary"
                                on:click={() => onSelectTemplate(template.template)}
                            >
                                {template.name}
                            </button>
                        {/each}
                        {#if isSystemPromptChanged}
                            <button
                                type="button"
                                class="btn-icon btn-icon-sm"
                                on:click={() => onSaveSystemPrompt()}
                            >
                                <span class="text-sm material-icons">save</span>
                            </button>
                        {/if}
                    </div>
                </div>
                <div bind:this={chatRef} class="flex flex-col gap-3 text-md leading-7">
                    {#each selectedConversation.memory as memory, i}
                        {#if i % 2 == 0}
                            <hr />
                        {/if}
                        {#if memory.type == 'human'}
                            <div class="flex gap-2 place-content-between text-pink-400">
                                <div>{memory.data.content}</div>
                                <button
                                    type="button"
                                    class="btn-icon btn-icon-sm text-orange-400"
                                    on:click={() => onDeleteMemory(i)}
                                >
                                    <span class="text-sm material-icons">delete</span>
                                </button>
                            </div>
                        {:else if memory.type == 'ai'}
                            <ConversationContent content={memory.data.content} />
                        {/if}
                    {/each}
                </div>
            {/if}
        </div>
    </div>
</div>
