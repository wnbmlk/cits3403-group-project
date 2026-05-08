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
const movieCatalogData = document.getElementById("movie-catalog-data");

let watchedRangePicker = null;
let timelineEntries = [];

function loadCatalog() {
    if (!movieCatalogData) {
        return [];
    }

    try {
        return JSON.parse(movieCatalogData.textContent || "[]");
    } catch (error) {
        console.error("Error loading movie catalog:", error);
        return [];
    }
}

const catalog = loadCatalog().map((movie) => ({
    title: movie.title,
    status: movie.status || "Watched",
    genre: movie.genre || "",
    poster: movie.poster_path || "/static/images/posters/placeholder.svg",
}));

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
    if (item.date) {
        try {
            const date = new Date(item.date);
            if (!Number.isNaN(date.getTime())) {
                return date.toISOString().slice(0, 10);
            }
        } catch (e) {}
    }

    return new Date().toISOString().slice(0, 10);
}

async function fetchTimelineEntries() {
    try {
        const response = await fetch("/api/diary/entries", {
            method: "GET",
            headers: { "Content-Type": "application/json" },
        });

        if (!response.ok) {
            throw new Error("Failed to fetch diary entries");
        }

        const data = await response.json();
        timelineEntries = (data.entries || []).map((entry) => ({
            id: entry.id,
            title: entry.title,
            status: entry.status,
            genre: entry.genre || "",
            poster: entry.poster_path || null,
            date: new Date(entry.date).toLocaleDateString("en-US", {
                month: "short",
                day: "2-digit",
                year: "numeric",
            }),
            dateISO: entry.date.split("T")[0],
        }));
        return timelineEntries;
    } catch (error) {
        console.error("Error fetching diary entries:", error);
        timelineEntries = [];
        return [];
    }
}

async function saveTimelineEntry(title, status, genre, date, posterPath = null) {
    try {
        const response = await fetch("/api/diary/entries", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                title,
                status,
                genre,
                poster_path: posterPath,
                date: date + "T00:00:00Z",
            }),
        });

        if (!response.ok) {
            throw new Error("Failed to save diary entry");
        }

        return await response.json();
    } catch (error) {
        console.error("Error saving diary entry:", error);
        return null;
    }
}

async function updateTimelineEntry(id, title, status, genre, date, posterPath = null) {
    try {
        const response = await fetch(`/api/diary/entries/${id}`, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                title,
                status,
                genre,
                poster_path: posterPath,
                date: date + "T00:00:00Z",
            }),
        });

        if (!response.ok) {
            throw new Error("Failed to update diary entry");
        }

        return await response.json();
    } catch (error) {
        console.error("Error updating diary entry:", error);
        return null;
    }
}

async function removeTimelineEntry(id) {
    try {
        const response = await fetch(`/api/diary/entries/${id}`, {
            method: "DELETE",
            headers: { "Content-Type": "application/json" },
        });

        if (!response.ok) {
            throw new Error("Failed to delete diary entry");
        }

        return true;
    } catch (error) {
        console.error("Error deleting diary entry:", error);
        return false;
    }
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
    return timelineEntries.filter((item) => matchesCategory(item) && matchesRange(item));
}

async function renderTimeline() {
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
        image.src = item.poster || "/static/images/posters/placeholder.svg";
        image.alt = `${item.title} poster`;
        title.textContent = item.title;
        status.textContent = `${item.status}${item.genre ? ` • ${item.genre}` : ""}`;
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
                <p>${movie.status}${movie.genre ? ` • ${movie.genre}` : ""}</p>
            </div>
        `;
        button.addEventListener("click", () => addMovieToTimeline(movie));
        searchResults.appendChild(button);
    });
}

async function addMovieToTimeline(movie) {
    const now = new Date();
    const dateISO = now.toISOString().split("T")[0];
    const status = movie.status || "Watched";

    const entry = await saveTimelineEntry(
        movie.title,
        status,
        movie.genre || "",
        dateISO,
        movie.poster || null
    );

    if (entry) {
        await fetchTimelineEntries();
        await renderTimeline();
        closeModal();
    }
}

async function removeMovieFromTimeline(id) {
    const success = await removeTimelineEntry(id);
    if (success) {
        await fetchTimelineEntries();
        await renderTimeline();
    }
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
    button.addEventListener("click", async () => {
        filterState.category = button.dataset.category;
        setActiveButton(categoryButtons, filterState.category, "category");
        await renderTimeline();
    });
});

watchedRangeToggle.addEventListener("change", async () => {
    filterState.useCustomRange = watchedRangeToggle.checked;
    filterState.category = "watched";
    if (!filterState.useCustomRange) {
        filterState.dateFrom = "";
        filterState.dateTo = "";
    }
    setActiveButton(categoryButtons, "watched", "category");
    syncRangeControls();
    await renderTimeline();
});

clearWatchedRange.addEventListener("click", async () => {
    filterState.useCustomRange = false;
    filterState.dateFrom = "";
    filterState.dateTo = "";
    syncRangeControls();
    await renderTimeline();
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

// Initialize the diary page
(async () => {
    await fetchTimelineEntries();
    await renderTimeline();
})();
