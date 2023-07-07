<script>
    import {hideYtPlayer, initYtPlayer} from '@/store';

    var tag = document.createElement('script');

    tag.src = 'https://www.youtube.com/iframe_api';
    var firstScriptTag = document.getElementsByTagName('script')[0];
    firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);

    // @ts-ignore
    window.onYouTubeIframeAPIReady = () => {
        initYtPlayer()
    };

    const onHideYtPlayer = () => {
        hideYtPlayer();
    };
</script>

<div class="inline">
    <div>
        <button
            type="button"
            class="btn-icon btn-icon-sm variant-filled"
            on:click={() => onHideYtPlayer()}
        >
            <span class="text-sm material-icons">close</span>
        </button>
    </div>
    <div id="yt-player" />
</div>
