import type {AxiosInstance} from 'axios';
import type {Conversation, ConversationChatToolsRecord} from './types';

export class _ConversationRepo {
    constructor(private api: AxiosInstance) {}

    async list() {
        const {data} = await this.api.get('/conversation_list');
        return data.conversations as Conversation[];
    }

    async create(name: string) {
        await this.api.post('/conversation', {name});
    }

    async get(conversation_id: string) {
        const {data} = await this.api.get(`/conversation/${conversation_id}`);
        return data.conversation as Conversation;
    }

    async saveSystemPrompt(conversation_id: string, system_prompt: string) {
        const {data} = await this.api.post(`/conversation/${conversation_id}/system_prompt`, {
            system_prompt,
        });
        return data.conversation as Conversation;
    }

    async saveMemory(conversation_id: string, memory: object[]) {
        const {data} = await this.api.post(`/conversation/${conversation_id}/memory`, {memory});
        return data.conversation as Conversation;
    }

    async saveName(conversation_id: string, name: string) {
        const {data} = await this.api.post(`/conversation/${conversation_id}/name`, {name});
        return data.conversation as Conversation;
    }

    async delete(conversation_id: string) {
        await this.api.delete(`/conversation/${conversation_id}`);
    }

    async templates() {
        const {data} = await this.api.get('/conversation_templates');
        return data.templates as any[];
    }

    async chat(conversation_id: string, chat: string, tools: ConversationChatToolsRecord) {
        const {data} = await this.api.post(`/conversation/${conversation_id}/chat`, {chat, tools});
        return data.conversation as Conversation;
    }
}