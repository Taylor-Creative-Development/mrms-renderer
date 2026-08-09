async function loadManifest() {
    const response = await fetch("frames.json");
    if (!response.ok) {
        throw new Error(`Failed to load frames.json (${response.status}).`);
    }
    return response.json();
}

function describe(entry) {
    return new Date(entry.valid_time + "Z").toLocaleString();
}

async function main() {
    const manifest = await loadManifest();
    const frames = manifest.frames;
    if (!frames.length) {
        throw new Error("No frames in the manifest.");
    }

    const first = frames[0];
    const bounds = [
        [first.bounds.south, first.bounds.west],
        [first.bounds.north, first.bounds.east],
    ];

    const map = L.map("map", {
        center: [first.bounds.south, first.bounds.west],
        zoom: 4,
        minZoom: 2,
        maxZoom: 17,
        maxBounds: [[15, -150], [75, -40]],
    });

    L.tileLayer(
        "https://tile.openstreetmap.org/{z}/{x}/{y}.png",
        {
            maxZoom: 19,
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
        }
    ).addTo(map);

    const overlay = L.imageOverlay(frames[0].file, bounds, {
        opacity: 0.65,
        interactive: false,
    }).addTo(map);
    map.fitBounds(bounds);

    const playEl = document.getElementById("play");
    const timelineEl = document.getElementById("timeline");
    const speedEl = document.getElementById("speed");
    const timestampEl = document.getElementById("timestamp");

    let index = 0;
    let playing = true;
    let frameMs = 350;
    let timer = null;
    timelineEl.max = String(frames.length - 1);

    function showFrame(i) {
        index = (i + frames.length) % frames.length;
        const entry = frames[index];
        overlay.setUrl(entry.file);
        timelineEl.value = String(index);
        timestampEl.textContent = describe(entry);
    }

    function stop() {
        if (timer !== null) {
            clearTimeout(timer);
            timer = null;
        }
    }

    function step() {
        if (!playing) return;
        showFrame(index + 1);
        timer = setTimeout(step, frameMs);
    }

    function start() {
        playing = true;
        playEl.textContent = "Pause";
        step();
    }

    function pause() {
        playing = false;
        playEl.textContent = "Play";
        stop();
    }

    playEl.addEventListener("click", () => {
        if (playing) {
            pause();
        } else {
            start();
        }
    });

    timelineEl.addEventListener("input", () => {
        showFrame(Number(timelineEl.value));
    });
    timelineEl.addEventListener("change", () => {
        if (playing) step();
    });

    speedEl.addEventListener("change", () => {
        frameMs = 350 / Number(speedEl.value);
        if (playing) {
            stop();
            step();
        }
    });

    showFrame(0);
    start();
}

main().catch((error) => {
    console.error(error);
    document.getElementById("timestamp").textContent = `Error: ${error.message}`;
});