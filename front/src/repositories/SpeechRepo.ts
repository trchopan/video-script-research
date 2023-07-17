import type {AxiosInstance} from 'axios';

export class _SpeechRepo {
    constructor(private api: AxiosInstance) {}

    async transcript(blob: Blob) {
        const formData = new FormData();
        formData.append('file', blob);
        const {data} = await this.api.post('/speech', formData);
        return data.transcript as string;
    }
}
