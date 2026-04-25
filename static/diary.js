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
const categoryButtons = document.querySelectorAll("[data-category]");
const watchedRangeToggle = document.getElementById("watchedRangeToggle");
const watchedDateRange = document.getElementById("watchedDateRange");
const clearWatchedRange = document.getElementById("clearWatchedRange");

let watchedRangePicker = null;

const filterState = {
    category: "all",
    useCustomRange: false,
    dateFrom: "",
    dateTo: "",
};

function slugify(text) {
    return String(text || "movie")
        .toLowerCase()
        .replace(/[^a-z0-9]+/g, "-")
        .replace(/^-+|-+$/g, "");
}

function parseLegacyDateISO(item) {
    if (item.dateISO) {
        return item.dateISO;
    }

    if (item.date) {
        const datePart = item.date.split("•")[0].trim();
        const parsed = new Date(datePart);
        if (!Number.isNaN(parsed.getTime())) {
            return parsed.toISOString().slice(0, 10);
        }
    }

    if (item.year) {
        return `${item.year}-01-01`;
    }

    return new Date().toISOString().slice(0, 10);
}

function createStableId(item) {
    const titlePart = slugify(item.title);
    const datePart = (item.dateISO || parseLegacyDateISO(item)).replace(/[^0-9]/g, "");
    const statusPart = slugify(item.status);
    return `movie-${titlePart}-${statusPart}-${datePart}`;
}

function getTimelineItems() {
    try {
        const saved = JSON.parse(localStorage.getItem(storageKey));
        if (Array.isArray(saved)) {
            const normalized = saved.map(normalizeTimelineItem);
            if (JSON.stringify(saved) !== JSON.stringify(normalized)) {
                saveTimelineItems(normalized);
            }
            return normalized;
        }
    } catch (error) {
        console.warn("Could not load saved timeline", error);
    }

    return [
        {
            id: "seed-1",
            title: "Parasite",
            status: "Watched",
            year: "2026",
            date: "Apr 02, 2024 • 20:10",
            dateISO: "2024-04-02",
            poster: "https://image.tmdb.org/t/p/w342/7IiTTgloJzvGI1TAYymCfbfl3vT.jpg",
        },
        {
            id: "seed-2",
            title: "Interstellar",
            status: "Rewatch",
            year: "2026",
            date: "Apr 05, 2024 • 22:00",
            dateISO: "2024-04-05",
            poster: "https://image.tmdb.org/t/p/w342/gEU2QniE6E77NI6lCU6MxlNBvIx.jpg",
        },
        {
            id: "seed-3",
            title: "The Dark Knight",
            status: "Favourite",
            year: "2026",
            date: "Apr 09, 2025 • 19:30",
            dateISO: "2025-04-09",
            poster: "https://image.tmdb.org/t/p/w342/8UlWHLMpgZm9bx6QYh0NFoq67TZ.jpg",
        },
        {
            id: "seed-4",
            title: "Dune: Part Two",
            status: "Watched",
            year: "2024",
            date: "Feb 20, 2025 • 18:15",
            dateISO: "2025-02-20",
            poster: "https://image.tmdb.org/t/p/w342/6izwzX3K8mLrZQ9y3FMhFjJw3k.jpg",
        },
    ];
}

function normalizeTimelineItem(item) {
    const dateISO = parseLegacyDateISO(item);
    return {
        id: item.id || createStableId(item),
        title: item.title,
        status: item.status,
        year: item.year,
        date: item.date,
        dateISO,
        poster: item.poster,
    };
}

function getStoreItems() {
    return getTimelineItems().map(normalizeTimelineItem);
}

function saveTimelineItems(items) {
    localStorage.setItem(storageKey, JSON.stringify(items));
}

function isWatched(item) {
    const status = item.status.toLowerCase();
    return status.includes("watch") || status.includes("rewatch");
}

function isFavourite(item) {
    const status = item.status.toLowerCase();
    return status.includes("favourite") || status.includes("favorite");
}

function matchesCategory(item) {
    if (filterState.category === "all") {
        return true;
    }

    if (filterState.category === "watched") {
        return isWatched(item);
    }

    if (filterState.category === "favorites") {
        return isFavourite(item);
    }

    if (filterState.category === "watching") {
        return item.status.toLowerCase().includes("watching");
    }

    if (filterState.category === "watchlist") {
        return item.status.toLowerCase().includes("watchlist") || item.status.toLowerCase().includes("want to watch");
    }

    return true;
}

function matchesRange(item) {
    if (filterState.category !== "watched" || !filterState.useCustomRange) {
        return true;
    }

    if (filterState.dateFrom && item.dateISO < filterState.dateFrom) {
        return false;
    }

    if (filterState.dateTo && item.dateISO > filterState.dateTo) {
        return false;
    }

    return true;
}

function getVisibleItems() {
    return getStoreItems().filter((item) => matchesCategory(item) && matchesRange(item));
}

function renderTimeline() {
    const items = getVisibleItems();
    timelineTrack.innerHTML = "";

    if (items.length === 0) {
        const emptyNode = document.createElement("div");
        emptyNode.className = "empty-timeline";
        emptyNode.textContent = "No movies match this view yet.";
        timelineTrack.appendChild(emptyNode);
    }

    items.forEach((item, index) => {
        const movieNode = movieTemplate.content.cloneNode(true);
        const article = movieNode.querySelector(".timeline-item");
        const timeStamp = movieNode.querySelector(".time-stamp");
        const image = movieNode.querySelector("img");
        const title = movieNode.querySelector("h3");
        const status = movieNode.querySelector("p");
        const removeButton = movieNode.querySelector(".remove-card");

        article.dataset.id = item.id;
        timeStamp.textContent = item.date || "New entry";
        image.src = item.poster;
        image.alt = `${item.title} poster`;
        title.textContent = item.title;
        status.textContent = `${item.status}${item.year ? ` • ${item.year}` : ""}`;
        removeButton.addEventListener("click", () => removeMovieFromTimeline(item.id));

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
    const items = getStoreItems();
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
        id: createStableId({ title: movie.title, status: movie.status, dateISO: now.toISOString().slice(0, 10) }),
        title: movie.title,
        status: movie.status,
        year: movie.year,
        date: `${dateLabel} • ${timeLabel}`,
        dateISO: now.toISOString().slice(0, 10),
        poster: movie.poster,
    });

    saveTimelineItems(items);
    renderTimeline();
    closeModal();
}

function removeMovieFromTimeline(id) {
    const items = getStoreItems().filter((item) => item.id !== id);
    saveTimelineItems(items);
    renderTimeline();
}

function setActiveButton(buttons, activeValue, dataKey) {
    buttons.forEach((button) => {
        const value = button.dataset[dataKey];
        button.classList.toggle("active", value === activeValue);
    });
}

function initializeRangePicker() {
    if (!window.flatpickr || !watchedDateRange) {
        return;
    }

    watchedRangePicker = window.flatpickr(watchedDateRange, {
        mode: "range",
        dateFormat: "Y-m-d",
        altInput: true,
        altFormat: "d/m/Y",
        allowInput: false,
        disableMobile: true,
        monthSelectorType: "dropdown",
        onOpen() {
            if (!filterState.useCustomRange) {
                filterState.useCustomRange = true;
                filterState.category = "watched";
                setActiveButton(categoryButtons, "watched", "category");
                syncRangeControls();
                renderTimeline();
            }
        },
        onChange(selectedDates) {
            if (selectedDates.length === 2) {
                filterState.useCustomRange = true;
                filterState.category = "watched";
                filterState.dateFrom = selectedDates[0].toISOString().slice(0, 10);
                filterState.dateTo = selectedDates[1].toISOString().slice(0, 10);
                setActiveButton(categoryButtons, "watched", "category");
                syncRangeControls();
                renderTimeline();
            }
        },
    });
}

function syncRangeControls() {
    watchedRangeToggle.checked = filterState.useCustomRange;

    if (watchedRangePicker) {
        if (filterState.useCustomRange && filterState.dateFrom && filterState.dateTo) {
            watchedRangePicker.setDate([filterState.dateFrom, filterState.dateTo], false, "Y-m-d");
        } else {
            watchedRangePicker.clear(false);
        }
    }
}

categoryButtons.forEach((button) => {
    button.addEventListener("click", () => {
        filterState.category = button.dataset.category;
        setActiveButton(categoryButtons, filterState.category, "category");
        renderTimeline();
    });
});

watchedRangeToggle.addEventListener("change", () => {
    filterState.useCustomRange = watchedRangeToggle.checked;
    filterState.category = "watched";
    if (!filterState.useCustomRange) {
        filterState.dateFrom = "";
        filterState.dateTo = "";
    }
    setActiveButton(categoryButtons, "watched", "category");
    syncRangeControls();
    renderTimeline();
});

clearWatchedRange.addEventListener("click", () => {
    filterState.useCustomRange = false;
    filterState.dateFrom = "";
    filterState.dateTo = "";
    syncRangeControls();
    renderTimeline();
});

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

initializeRangePicker();
syncRangeControls();
renderTimeline();