import type {AxiosInstance} from 'axios';
import type {SystemPrompt} from './types';

export class _SystemPromptRepo {
    constructor(private api: AxiosInstance) {}

    async list() {
        const {data} = await this.api.get('/system_prompts');
        return data.system_prompts.map((d: any) => ({_id: d.id, ...d.data})) as SystemPrompt[];
    }

    async create(name: string, template: string) {
        await this.api.post('/system_prompt', {name, template});
    }

    async save(id: number, name: string, template: string) {
        await this.api.post(`/system_prompt/${id}`, {name, template});
    }

    async delete(id: number) {
        await this.api.delete(`/system_prompt/${id}`);
    }
}
