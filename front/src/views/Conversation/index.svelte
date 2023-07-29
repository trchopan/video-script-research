<script lang="ts">
    import {ConversationRepo, SpeechRepo, SystemPromptRepo} from '@/repositories/inject';
    import {onMount, tick} from 'svelte';
    import {
        ConversationChatToolEnum,
        type Conversation,
        type ConversationChatToolsRecord,
    } from '@/repositories/types';
    import {cloneDeep, noop} from 'lodash';
    import Loading from '@/components/Loading.svelte';
    import ConversationContent from './ConversationContent.svelte';
    import TextToParagraph from '@/components/TextToParagraph.svelte';
    import {mediaRecorderSvc} from '@/store';

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

    const onCreateConversation = async () => {
        await ConversationRepo.create(name);
        await loadConversation();
        name = '';
    };

    const onDeleteConversation = async (conversation_id: string) => {
        await ConversationRepo.delete(conversation_id);
        if (selectedConversation.conversation_id === conversation_id) {
            selectedConversation = null;
        }
        await loadConversation();
    };

    const onSelectConversation = async (conversation_id: string) => {
        selectedConversation = await ConversationRepo.get(conversation_id);
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
        {name: 'Duckduck Go', value: ConversationChatToolEnum.DuckduckGo},
        {name: 'Youtube', value: ConversationChatToolEnum.Youtube},
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

    let isRecording = false;
    let stopRecording: () => Promise<Blob[]>;

    const onSpeak = async () => {
        isRecording = true;
        stopRecording = await mediaRecorderSvc.startRecord();
    };

    let audioRef: any;
    const onStopRecord = async () => {
        isRecording = false;
        if (!stopRecording) return;
        const chunks = await stopRecording();
        const blob = new Blob(chunks, {type: 'audio/ogg; codecs=opus'});
        const audioURL = window.URL.createObjectURL(blob);
        audioRef.src = audioURL;
        console.log('>>src', audioRef.src);
        const transcriptResp = await SpeechRepo.transcript(blob);
        chat += '\n---\n' + transcriptResp;
    };
</script>

<div class="grid grid-cols-[1fr,1.5fr] gap-5 h-[95vh] overflow-y-hidden">
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
                <li
                    class:selected={selectedConversation?.conversation_id ===
                        conversation.conversation_id}
                >
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
            <div class="flex flex-wrap gap-3">
                {#each toolOptions as tOpt}
                    <button
                        type="button"
                        class="btn btn-sm"
                        class:variant-filled-primary={tools.includes(tOpt)}
                        on:click={() => onSelectToolOption(tOpt)}
                    >
                        {tOpt.name}
                    </button>
                {/each}
            </div>
            <hr />
            <div class="flex flex-col gap-5">
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
                    {#if !isRecording}
                        <button
                            type="button"
                            class="btn variant-ringed-primary btn-sm"
                            on:click={() => onSpeak()}
                        >
                            Speak
                        </button>
                        {#if audioRef?.src.length > 0}
                            <button
                                type="button"
                                class="btn-icon btn-icon-sm"
                                on:click={() => audioRef.play()}
                            >
                                <span class="text-sm material-icons">play_circle_filled</span>
                            </button>
                        {/if}
                    {:else}
                        <button
                            type="button"
                            class="btn variant-ringed-error btn-sm"
                            on:click={() => onStopRecord()}
                        >
                            Stop
                        </button>
                    {/if}
                    <audio bind:this={audioRef} />
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
                <div>
                    <textarea
                        bind:value={localSystemPrompt}
                        class="textarea leading-7"
                        rows="4"
                        placeholder="System Prompt"
                    />
                    <div class="flex gap-3 items-start place-content-between">
                        <div class="flex flex-wrap gap-3">
                            {#each templates as template}
                                <button
                                    type="button"
                                    class="btn btn-sm variant-ringed-primary"
                                    on:click={() => onSelectTemplate(template.template)}
                                >
                                    {template.name}
                                </button>
                            {/each}
                        </div>
                        {#if isSystemPromptChanged}
                            <button
                                type="button"
                                class="btn-icon btn-icon-sm text-red-400"
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
                            <div class="text-blue-400">
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
