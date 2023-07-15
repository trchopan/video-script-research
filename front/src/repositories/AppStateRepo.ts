import type {AxiosInstance} from 'axios';
import type {AppState} from './types';

export class _AppStateRepo {
    constructor(private api: AxiosInstance) {}

    async list() {
        const {data} = await this.api.get('/app_state_list');
        return data.app_states as AppState[];
    }

    async create(name: string, data: object) {
        await this.api.post('/app_state', {name, data});
    }

    async get(app_id: string) {
        const {data} = await this.api.get(`/app_state/${app_id}`);
        return data.app_state as AppState;
    }

    async save(app_id: string, data: object) {
        await this.api.post(`/app_state/${app_id}`, {data});
    }

    async delte(app_id: string) {
        await this.api.delete(`/app_state/${app_id}`);
    }
}
