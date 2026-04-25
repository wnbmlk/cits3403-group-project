const catalog = [
    {
        title: "Parasite",
        status: "Watched",
        year: "2019",
        poster: "https://image.tmdb.org/t/p/w342/7IiTTgloJzvGI1TAYymCfbfl3vT.jpg",
    },
    {
        title: "Interstellar",
        status: "Want to watch",
        year: "2014",
        poster: "https://image.tmdb.org/t/p/w342/gEU2QniE6E77NI6lCU6MxlNBvIx.jpg",
    },
    {
        title: "The Dark Knight",
        status: "Favourite",
        year: "2008",
        poster: "https://image.tmdb.org/t/p/w342/8UlWHLMpgZm9bx6QYh0NFoq67TZ.jpg",
    },
    {
        title: "Inception",
        status: "Watched",
        year: "2010",
        poster: "https://image.tmdb.org/t/p/w342/9gk7adHYeDvHkCSEqAvQNLV5Uge.jpg",
    },
    {
        title: "The Lord of the Rings",
        status: "Watchlist",
        year: "2001",
        poster: "https://image.tmdb.org/t/p/w342/rCzpDGLbOoPwLjy3OAm5NUPOTrC.jpg",
    },
    {
        title: "Oppenheimer",
        status: "Watchlist",
        year: "2023",
        poster: "https://image.tmdb.org/t/p/w342/ptpr0kGAckfQkJeJIt8st5dglvd.jpg",
    },
    {
        title: "Dune: Part Two",
        status: "Watched",
        year: "2024",
        poster: "https://image.tmdb.org/t/p/w342/6izwzX3K8mLrZQ9y3FMhFjJw3k.jpg",
    },
    {
        title: "Severance",
        status: "Watching",
        year: "2022",
        poster: "https://image.tmdb.org/t/p/w342/mbXQb9Q0mVfM6R1nF8l6HfBq0d8.jpg",
    },
];

const storageKey = "movieDiaryTimeline";
const timelineTrack = document.getElementById("timelineTrack");
const movieModal = document.getElementById("movieModal");
const closeMovieModal = document.getElementById("closeMovieModal");
const movieSearch = document.getElementById("movieSearch");
const searchResults = document.getElementById("searchResults");
const movieTemplate = document.getElementById("timelineMovieTemplate");
const addTemplate = document.getElementById("timelineAddTemplate");

function getTimelineItems() {
    try {
        const saved = JSON.parse(localStorage.getItem(storageKey));
        if (Array.isArray(saved) && saved.length > 0) {
            return saved;
        }
    } catch (error) {
        console.warn("Could not load saved timeline", error);
    }

    return [
        {
            title: "Parasite",
            status: "Watched",
            year: "2026",
            date: "Apr 02, 2026 • 20:10",
            poster: "https://image.tmdb.org/t/p/w342/7IiTTgloJzvGI1TAYymCfbfl3vT.jpg",
        },
        {
            title: "Interstellar",
            status: "Rewatch",
            year: "2026",
            date: "Apr 05, 2026 • 22:00",
            poster: "https://image.tmdb.org/t/p/w342/gEU2QniE6E77NI6lCU6MxlNBvIx.jpg",
        },
        {
            title: "The Dark Knight",
            status: "Favourite",
            year: "2026",
            date: "Apr 09, 2026 • 19:30",
            poster: "https://image.tmdb.org/t/p/w342/8UlWHLMpgZm9bx6QYh0NFoq67TZ.jpg",
        },
    ];
}

function saveTimelineItems(items) {
    localStorage.setItem(storageKey, JSON.stringify(items));
}

function renderTimeline() {
    const items = getTimelineItems();
    timelineTrack.innerHTML = "";

    items.forEach((item, index) => {
        const movieNode = movieTemplate.content.cloneNode(true);
        const article = movieNode.querySelector(".timeline-item");
        const timeStamp = movieNode.querySelector(".time-stamp");
        const image = movieNode.querySelector("img");
        const title = movieNode.querySelector("h3");
        const status = movieNode.querySelector("p");

        article.dataset.index = index;
        timeStamp.textContent = item.date || "New entry";
        image.src = item.poster;
        image.alt = `${item.title} poster`;
        title.textContent = item.title;
        status.textContent = `${item.status}${item.year ? ` • ${item.year}` : ""}`;

        timelineTrack.appendChild(movieNode);
    });

    const addNode = addTemplate.content.cloneNode(true);
    const addButton = addNode.querySelector(".add-card");
    addButton.addEventListener("click", openModal);
    timelineTrack.appendChild(addNode);
}

function openModal() {
    movieModal.hidden = false;
    movieSearch.value = "";
    renderResults(catalog);
    movieSearch.focus();
}

function closeModal() {
    movieModal.hidden = true;
}

function renderResults(results) {
    searchResults.innerHTML = "";

    if (results.length === 0) {
        searchResults.innerHTML = '<p class="empty-search">No matches found.</p>';
        return;
    }

    results.forEach((movie) => {
        const button = document.createElement("button");
        button.type = "button";
        button.className = "search-result";
        button.innerHTML = `
            <img src="${movie.poster}" alt="${movie.title} poster">
            <div>
                <h3>${movie.title}</h3>
                <p>${movie.status} • ${movie.year}</p>
            </div>
        `;
        button.addEventListener("click", () => addMovieToTimeline(movie));
        searchResults.appendChild(button);
    });
}

function addMovieToTimeline(movie) {
    const items = getTimelineItems();
    const now = new Date();
    const dateLabel = now.toLocaleDateString("en-US", {
        month: "short",
        day: "2-digit",
        year: "numeric",
    });
    const timeLabel = now.toLocaleTimeString("en-US", {
        hour: "2-digit",
        minute: "2-digit",
        hour12: false,
    });

    items.push({
        title: movie.title,
        status: movie.status,
        year: movie.year,
        date: `${dateLabel} • ${timeLabel}`,
        poster: movie.poster,
    });

    saveTimelineItems(items);
    renderTimeline();
    closeModal();
}

movieSearch.addEventListener("input", () => {
    const term = movieSearch.value.trim().toLowerCase();
    const filtered = catalog.filter((movie) => movie.title.toLowerCase().includes(term));
    renderResults(filtered);
});

closeMovieModal.addEventListener("click", closeModal);
movieModal.addEventListener("click", (event) => {
    if (event.target === movieModal) {
        closeModal();
    }
});

document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && !movieModal.hidden) {
        closeModal();
    }
});

renderTimeline();