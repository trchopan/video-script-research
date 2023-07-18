export class MediaRecorderService {
    chunks: Blob[] = [];
    mediaRecorder: MediaRecorder;

    async setMediaRecorder() {
        if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
            console.log('getUserMedia supported.');
            const stream = (await navigator.mediaDevices
                .getUserMedia({
                    audio: true,
                })
                .catch(err => {
                    console.error(`The following getUserMedia error occurred: ${err}`);
                })) as MediaStream;
            this.mediaRecorder = new MediaRecorder(stream);
        } else {
            console.log('getUserMedia not supported on your browser!');
        }
    }

    async startRecord(): Promise<() => Promise<Blob[]>> {
        if (!this.mediaRecorder) {
            await this.setMediaRecorder();
        }
        this.mediaRecorder.start();
        console.log(this.mediaRecorder.state);
        console.log('recorder started');
        this.mediaRecorder.ondataavailable = e => {
            this.chunks.push(e.data);
        };

        let timeout: any;
        const cb = () => {
            timeout?.close?.();
            if (!this.mediaRecorder) return;

            this.mediaRecorder.stop();
            return new Promise<Blob[]>(resolve => {
                this.mediaRecorder.onstop = () => {
                    console.log(this.mediaRecorder.state);
                    console.log('recorder stopped');
                    console.log('>>>', this.chunks);
                    this.mediaRecorder.stream.getTracks().forEach(track => {
                        track.stop();
                        track.enabled = false;
                    });
                    resolve(this.chunks);
                    this.chunks = [];
                    this.mediaRecorder = null;
                };
            });
        };

        timeout = setTimeout(() => {
            if (!this.mediaRecorder) return;
            console.error('Timeout mediaRecorder still active after start');
            cb();
        }, 30 * 1000); // Max 30 seconds recording

        return cb;
    }
}
