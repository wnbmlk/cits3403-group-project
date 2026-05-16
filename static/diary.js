const timelineTrack = document.getElementById("timelineTrack");
const movieModal = document.getElementById("movieModal");
const closeMovieModal = document.getElementById("closeMovieModal");
const movieSearch = document.getElementById("movieSearch");
const searchResults = document.getElementById("searchResults");
const manualAddSection = document.getElementById("manualAddSection");
const manualTitleInput = document.getElementById("manualTitleInput");
const manualGenreInput = document.getElementById("manualGenreInput");
const manualPhotoInput = document.getElementById("manualPhotoInput");
const manualAddSubmit = document.getElementById("manualAddSubmit");
const manualAddError = document.getElementById("manualAddError");
const statusPrompt = document.getElementById("statusPrompt");
const statusPromptMovieTitle = document.getElementById("statusPromptMovieTitle");
const confirmAddMovie = document.getElementById("confirmAddMovie");
const cancelStatusPrompt = document.getElementById("cancelStatusPrompt");
const movieTemplate = document.getElementById("timelineMovieTemplate");
const addTemplate = document.getElementById("timelineAddTemplate");
const categoryButtons = document.querySelectorAll("[data-category]");
const watchedDateRange = document.getElementById("watchedDateRange");
const applyWatchedRange = document.getElementById("applyWatchedRange");
const clearWatchedRange = document.getElementById("clearWatchedRange");
const movieCatalogData = document.getElementById("movie-catalog-data");
const watchDateSingleInput = document.getElementById("watchDateSingle");
const watchDateStartInput = document.getElementById("watchDateStart");
const watchDateEndInput = document.getElementById("watchDateEnd");
const singleDatePickerDiv = document.getElementById("singleDatePicker");
const rangeDatePickerDiv = document.getElementById("rangeDatePicker");
const dateModeSingleRadio = document.querySelector('input[name="dateMode"][value="single"]');
const dateModeRangeRadio = document.querySelector('input[name="dateMode"][value="range"]');
const manualWatchDateSingleInput = document.getElementById("manualWatchDateSingle");
const manualWatchDateStartInput = document.getElementById("manualWatchDateStart");
const manualWatchDateEndInput = document.getElementById("manualWatchDateEnd");
const manualSingleDatePickerDiv = document.getElementById("manualSingleDatePicker");
const manualRangeDatePickerDiv = document.getElementById("manualRangeDatePicker");
const manualDateModeSingleRadio = document.querySelector('input[name="manualDateMode"][value="single"]');
const manualDateModeRangeRadio = document.querySelector('input[name="manualDateMode"][value="range"]');
const csrfTokenMeta = document.querySelector('meta[name="csrf-token"]');
const csrfToken = csrfTokenMeta ? csrfTokenMeta.getAttribute('content') : '';

let watchedRangePicker = null;
let timelineEntries = [];
let pendingMovie = null;
let watchDateSinglePicker = null;
let watchDateStartPicker = null;
let watchDateEndPicker = null;
let manualWatchDateSinglePicker = null;
let manualWatchDateStartPicker = null;
let manualWatchDateEndPicker = null;

function buildRequestHeaders(extraHeaders = {}) {
    return {
        ...extraHeaders,
        ...(csrfToken ? { 'X-CSRFToken': csrfToken } : {}),
    };
}

function showErrorMessage(message) {
    // Display error message to user via alert and console
    console.error("Error:", message);
    alert(`Error: ${message}`);
}

function showSuccessMessage(message) {
    // Log success message to console
    console.log("Success:", message);
}

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
    media_type: movie.media_type || "",
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

function toLocalISODate(date) {
    if (!(date instanceof Date) || Number.isNaN(date.getTime())) {
        return "";
    }

    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, "0");
    const day = String(date.getDate()).padStart(2, "0");
    return `${year}-${month}-${day}`;
}

function parseLegacyDateISO(item) {
    if (item.date) {
        try {
            const date = new Date(item.date);
            if (!Number.isNaN(date.getTime())) {
                return toLocalISODate(date);
            }
        } catch (e) {}
    }

    return toLocalISODate(new Date());
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
            dateLabel: formatWatchDateLabel(entry.date, entry.date_watched_end),
            dateISO: entry.date.split("T")[0],
            dateEndISO: entry.date_watched_end ? entry.date_watched_end.split("T")[0] : entry.date.split("T")[0],
        }));
        return timelineEntries;
    } catch (error) {
        console.error("Error fetching diary entries:", error);
        timelineEntries = [];
        return [];
    }
}

async function saveTimelineEntry(title, status, genre, date, posterPath = null, dateWatchedEnd = null) {
    try {
        const body = {
            title,
            status,
            genre,
            poster_path: posterPath,
            date: date + "T00:00:00Z",
        };
        if (dateWatchedEnd) {
            body.date_watched_end = dateWatchedEnd + "T00:00:00Z";
        }
        const response = await fetch("/api/diary/entries", {
            method: "POST",
            headers: buildRequestHeaders({ "Content-Type": "application/json" }),
            body: JSON.stringify(body),
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            const errorMsg = errorData.error || "Failed to save diary entry";
            throw new Error(errorMsg);
        }

        return await response.json();
    } catch (error) {
        console.error("Error saving diary entry:", error);
        showErrorMessage(error.message || "Failed to save diary entry");
        return null;
    }
}

async function updateTimelineEntry(id, title, status, genre, date, posterPath = null, dateWatchedEnd = null) {
    try {
        const body = {
            title,
            status,
            genre,
            poster_path: posterPath,
            date: date + "T00:00:00Z",
        };
        if (dateWatchedEnd) {
            body.date_watched_end = dateWatchedEnd + "T00:00:00Z";
        }
        const response = await fetch(`/api/diary/entries/${id}`, {
            method: "PUT",
            headers: buildRequestHeaders({ "Content-Type": "application/json" }),
            body: JSON.stringify(body),
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            const errorMsg = errorData.error || "Failed to update diary entry";
            throw new Error(errorMsg);
        }

        return await response.json();
    } catch (error) {
        console.error("Error updating diary entry:", error);
        showErrorMessage(error.message || "Failed to update diary entry");
        return null;
    }
}

async function removeTimelineEntry(id) {
    try {
        const response = await fetch(`/api/diary/entries/${id}`, {
            method: "DELETE",
            headers: buildRequestHeaders({ "Content-Type": "application/json" }),
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            const errorMsg = errorData.error || "Failed to delete diary entry";
            throw new Error(errorMsg);
        }

        return true;
    } catch (error) {
        console.error("Error deleting diary entry:", error);
        showErrorMessage(error.message || "Failed to delete diary entry");
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
    if (!filterState.useCustomRange) {
        return true;
    }

    if (!isWatched(item)) {
        return false;
    }

    const itemStart = item.dateISO;
    const itemEnd = item.dateEndISO || item.dateISO;

    if (filterState.dateFrom && itemEnd < filterState.dateFrom) {
        return false;
    }

    if (filterState.dateTo && itemStart > filterState.dateTo) {
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
        const image = movieNode.querySelector("img");
        const title = movieNode.querySelector("h3");
        const watchDate = movieNode.querySelector(".watch-date");
        const status = movieNode.querySelector(".movie-meta p:last-of-type");
        const removeButton = movieNode.querySelector(".remove-card");

        article.dataset.id = item.id;
        image.src = item.poster || "/static/images/posters/placeholder.svg";
        image.alt = `${item.title} poster`;
        title.textContent = item.title;
        if (watchDate) {
            watchDate.textContent = item.dateLabel || "Watched date not set";
        }
        status.textContent = `${item.status}${item.media_type ? ` • ${item.media_type}` : ""}${item.genre ? ` • ${item.genre}` : ""}`;
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
    pendingMovie = null;
    hideStatusPrompt();
    hideManualAddSection();
    renderResults(catalog);
    movieSearch.focus();
}

function closeModal() {
    pendingMovie = null;
    hideStatusPrompt();
    hideManualAddSection();
    movieModal.hidden = true;
}

function renderResults(results) {
    searchResults.innerHTML = "";

    if (results.length === 0) {
        searchResults.innerHTML = '<p class="empty-search">No matches found.</p>';
        showManualAddSection(movieSearch.value.trim());
        return;
    }

    hideManualAddSection();

    results.forEach((movie) => {
        const button = document.createElement("button");
        button.type = "button";
        button.className = "search-result";
        const genreText = movie.genre ? `${movie.media_type ? `${movie.media_type} • ` : ""}${movie.genre}` : (movie.media_type || "Genre not set");
        button.innerHTML = `
            <img src="${movie.poster}" alt="${movie.title} poster">
            <div>
                <h3>${movie.title}</h3>
                <p>${genreText}</p>
            </div>
        `;
        button.addEventListener("click", () => addMovieToTimeline(movie, button));
        searchResults.appendChild(button);
    });
}

function showManualError(message) {
    if (!manualAddError) {
        return;
    }

    if (!message) {
        manualAddError.hidden = true;
        manualAddError.textContent = "";
        return;
    }

    manualAddError.hidden = false;
    manualAddError.textContent = message;
}

function resetManualStatuses() {
    document.querySelectorAll(".manual-status-checkbox").forEach((checkbox) => {
        checkbox.checked = false;
    });
    const defaultStatus = document.querySelector('.manual-status-checkbox[value="Watched"]');
    if (defaultStatus) {
        defaultStatus.checked = true;
    }
}

function showManualAddSection(prefillTitle = "") {
    if (!manualAddSection) {
        return;
    }

    manualAddSection.hidden = false;
    if (manualTitleInput) {
        manualTitleInput.value = prefillTitle;
    }
    if (manualGenreInput) {
        manualGenreInput.value = "";
    }
    if (manualPhotoInput) {
        manualPhotoInput.value = "";
    }
    showManualError("");
    resetManualStatuses();
    resetManualDatePickers();
}

function hideManualAddSection() {
    if (!manualAddSection) {
        return;
    }

    manualAddSection.hidden = true;
    showManualError("");
}

function getSelectedManualStatuses() {
    return Array.from(document.querySelectorAll(".manual-status-checkbox:checked")).map(
        (checkbox) => checkbox.value
    );
}

async function saveManualTimelineEntry(formData) {
    try {
        const response = await fetch("/api/diary/manual-entry", {
            method: "POST",
            headers: buildRequestHeaders(),
            body: formData,
        });

        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.error || "Failed to save manual entry");
        }

        return data;
    } catch (error) {
        showManualError(error.message || "Failed to save manual entry");
        return null;
    }
}

async function addManualMovieEntry() {
    const title = (manualTitleInput?.value || "").trim();
    const genre = (manualGenreInput?.value || "").trim();
    const selectedStatuses = getSelectedManualStatuses();

    const formData = new FormData();
    formData.append("title", title);
    if (genre) {
        formData.append("genre", genre);
    }
    selectedStatuses.forEach((status) => {
        formData.append("statuses", status);
    });
    
    const watchDates = getManualWatchDate();
    const dateISO = toLocalISODate(watchDates.date);
    formData.append("date", dateISO + "T00:00:00Z");
    if (watchDates.date_watched_end) {
        const dateEndISO = toLocalISODate(watchDates.date_watched_end);
        formData.append("date_watched_end", dateEndISO + "T00:00:00Z");
    }

    if (manualPhotoInput?.files && manualPhotoInput.files[0]) {
        formData.append("photo", manualPhotoInput.files[0]);
    }

    const entry = await saveManualTimelineEntry(formData);
    if (!entry) {
        return;
    }

    catalog.push({
        title: entry.title,
        genre: entry.genre || "",
        poster: entry.poster_path || "/static/images/posters/placeholder.svg",
    });

    await fetchTimelineEntries();
    await renderTimeline();
    closeModal();
}

function getSelectedStatuses() {
    const selected = Array.from(document.querySelectorAll(".status-checkbox:checked")).map(
        (checkbox) => checkbox.value
    );
    return selected;
}

function resetStatusCheckboxes() {
    document.querySelectorAll(".status-checkbox").forEach((checkbox) => {
        checkbox.checked = false;
    });
}

function showStatusPrompt(movie, selectedButton) {
    pendingMovie = movie;
    if (statusPromptMovieTitle) {
        statusPromptMovieTitle.textContent = movie.title;
    }
    resetStatusCheckboxes();
    const watchedCheckbox = document.querySelector('.status-checkbox[value="Watched"]');
    if (watchedCheckbox) {
        watchedCheckbox.checked = true;
    }
    resetDatePickers();
    if (statusPrompt && selectedButton) {
        selectedButton.insertAdjacentElement("afterend", statusPrompt);
        statusPrompt.hidden = false;
        statusPrompt.scrollIntoView({ block: "nearest", behavior: "smooth" });
        watchedCheckbox?.focus();
    }
}

function hideStatusPrompt() {
    if (statusPrompt) {
        statusPrompt.hidden = true;
    }
    resetStatusCheckboxes();
}

async function addMovieToTimeline(movie, selectedButton) {
    showStatusPrompt(movie, selectedButton);
}

async function confirmAddMovieToTimeline() {
    if (!pendingMovie) {
        return;
    }

    const selectedStatuses = getSelectedStatuses();
    if (selectedStatuses.length === 0) {
        alert("Please choose at least one status.");
        return;
    }

    const watchDates = getWatchDate();
    const dateISO = toLocalISODate(watchDates.date);
    const dateEndISO = watchDates.date_watched_end ? toLocalISODate(watchDates.date_watched_end) : null;
    const status = selectedStatuses.join(", ");

    const entry = await saveTimelineEntry(
        pendingMovie.title,
        status,
        pendingMovie.genre || "",
        dateISO,
        pendingMovie.poster || null,
        dateEndISO
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

function formatWatchDateLabel(startISO, endISO) {
    const startDate = new Date(startISO);
    if (Number.isNaN(startDate.getTime())) {
        return "Watched date not set";
    }

    const formatOptions = {
        month: "short",
        day: "2-digit",
        year: "numeric",
    };

    const startLabel = startDate.toLocaleDateString("en-US", formatOptions);
    if (!endISO) {
        return `Watched: ${startLabel}`;
    }

    const endDate = new Date(endISO);
    if (Number.isNaN(endDate.getTime())) {
        return `Watched: ${startLabel}`;
    }

    const endLabel = endDate.toLocaleDateString("en-US", formatOptions);
    if (startLabel === endLabel) {
        return `Watched: ${startLabel}`;
    }

    return `Watched: ${startLabel} - ${endLabel}`;
}

function initializeWatchDatePickers() {
    if (!window.flatpickr) {
        return;
    }

    // Single date picker for status prompt
    if (watchDateSingleInput) {
        watchDateSinglePicker = window.flatpickr(watchDateSingleInput, {
            mode: "single",
            dateFormat: "Y-m-d",
            altInput: true,
            altFormat: "d/m/Y",
            allowInput: false,
            disableMobile: true,
            monthSelectorType: "dropdown",
            defaultDate: new Date(),
        });
    }

    // Start date picker for status prompt
    if (watchDateStartInput) {
        watchDateStartPicker = window.flatpickr(watchDateStartInput, {
            mode: "single",
            dateFormat: "Y-m-d",
            altInput: true,
            altFormat: "d/m/Y",
            allowInput: false,
            disableMobile: true,
            monthSelectorType: "dropdown",
        });
    }

    // End date picker for status prompt
    if (watchDateEndInput) {
        watchDateEndPicker = window.flatpickr(watchDateEndInput, {
            mode: "single",
            dateFormat: "Y-m-d",
            altInput: true,
            altFormat: "d/m/Y",
            allowInput: false,
            disableMobile: true,
            monthSelectorType: "dropdown",
        });
    }

    // Single date picker for manual add
    if (manualWatchDateSingleInput) {
        manualWatchDateSinglePicker = window.flatpickr(manualWatchDateSingleInput, {
            mode: "single",
            dateFormat: "Y-m-d",
            altInput: true,
            altFormat: "d/m/Y",
            allowInput: false,
            disableMobile: true,
            monthSelectorType: "dropdown",
            defaultDate: new Date(),
        });
    }

    // Start date picker for manual add
    if (manualWatchDateStartInput) {
        manualWatchDateStartPicker = window.flatpickr(manualWatchDateStartInput, {
            mode: "single",
            dateFormat: "Y-m-d",
            altInput: true,
            altFormat: "d/m/Y",
            allowInput: false,
            disableMobile: true,
            monthSelectorType: "dropdown",
        });
    }

    // End date picker for manual add
    if (manualWatchDateEndInput) {
        manualWatchDateEndPicker = window.flatpickr(manualWatchDateEndInput, {
            mode: "single",
            dateFormat: "Y-m-d",
            altInput: true,
            altFormat: "d/m/Y",
            allowInput: false,
            disableMobile: true,
            monthSelectorType: "dropdown",
        });
    }
}

function resetDatePickers() {
    if (watchDateSinglePicker) {
        watchDateSinglePicker.setDate(new Date());
    }
    if (watchDateStartPicker) {
        watchDateStartPicker.clear(false);
    }
    if (watchDateEndPicker) {
        watchDateEndPicker.clear(false);
    }
    if (dateModeSingleRadio) {
        dateModeSingleRadio.checked = true;
    }
    if (dateModeRangeRadio) {
        dateModeRangeRadio.checked = false;
    }
    if (singleDatePickerDiv) {
        singleDatePickerDiv.hidden = false;
    }
    if (rangeDatePickerDiv) {
        rangeDatePickerDiv.hidden = true;
    }
}

function resetManualDatePickers() {
    if (manualWatchDateSinglePicker) {
        manualWatchDateSinglePicker.setDate(new Date());
    }
    if (manualWatchDateStartPicker) {
        manualWatchDateStartPicker.clear(false);
    }
    if (manualWatchDateEndPicker) {
        manualWatchDateEndPicker.clear(false);
    }
    if (manualDateModeSingleRadio) {
        manualDateModeSingleRadio.checked = true;
    }
    if (manualDateModeRangeRadio) {
        manualDateModeRangeRadio.checked = false;
    }
    if (manualSingleDatePickerDiv) {
        manualSingleDatePickerDiv.hidden = false;
    }
    if (manualRangeDatePickerDiv) {
        manualRangeDatePickerDiv.hidden = true;
    }
}

function getWatchDate() {
    const isRange = dateModeRangeRadio?.checked;
    if (isRange) {
        return {
            date: watchDateStartPicker?.selectedDates[0] || new Date(),
            date_watched_end: watchDateEndPicker?.selectedDates[0] || new Date(),
        };
    }
    return {
        date: watchDateSinglePicker?.selectedDates[0] || new Date(),
        date_watched_end: null,
    };
}

function getManualWatchDate() {
    const isRange = manualDateModeRangeRadio?.checked;
    if (isRange) {
        return {
            date: manualWatchDateStartPicker?.selectedDates[0] || new Date(),
            date_watched_end: manualWatchDateEndPicker?.selectedDates[0] || new Date(),
        };
    }
    return {
        date: manualWatchDateSinglePicker?.selectedDates[0] || new Date(),
        date_watched_end: null,
    };
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
        onChange() {},
    });
}

function syncRangeControls() {
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

clearWatchedRange.addEventListener("click", async () => {
    filterState.useCustomRange = false;
    filterState.dateFrom = "";
    filterState.dateTo = "";
    syncRangeControls();
    await renderTimeline();
});

if (applyWatchedRange) {
    applyWatchedRange.addEventListener("click", async () => {
        if (!watchedRangePicker) {
            return;
        }

        const selectedDates = watchedRangePicker.selectedDates || [];
        if (selectedDates.length === 0) {
            alert("Please pick at least one watched date.");
            return;
        }

        const fromDate = toLocalISODate(selectedDates[0]);
        const toDate = toLocalISODate(selectedDates[1] || selectedDates[0]);

        filterState.useCustomRange = true;
        filterState.category = "watched";
        filterState.dateFrom = fromDate;
        filterState.dateTo = toDate;
        setActiveButton(categoryButtons, "watched", "category");
        syncRangeControls();
        await renderTimeline();
    });
}

movieSearch.addEventListener("input", () => {
    pendingMovie = null;
    hideStatusPrompt();
    const term = movieSearch.value.trim().toLowerCase();
    const filtered = catalog.filter((movie) => movie.title.toLowerCase().includes(term));
    renderResults(filtered);
});

if (manualAddSubmit) {
    manualAddSubmit.addEventListener("click", addManualMovieEntry);
}

if (confirmAddMovie) {
    confirmAddMovie.addEventListener("click", confirmAddMovieToTimeline);
}

if (cancelStatusPrompt) {
    cancelStatusPrompt.addEventListener("click", () => {
        pendingMovie = null;
        hideStatusPrompt();
    });
}

if (dateModeSingleRadio) {
    dateModeSingleRadio.addEventListener("change", () => {
        if (singleDatePickerDiv) {
            singleDatePickerDiv.hidden = false;
        }
        if (rangeDatePickerDiv) {
            rangeDatePickerDiv.hidden = true;
        }
    });
}

if (dateModeRangeRadio) {
    dateModeRangeRadio.addEventListener("change", () => {
        if (singleDatePickerDiv) {
            singleDatePickerDiv.hidden = true;
        }
        if (rangeDatePickerDiv) {
            rangeDatePickerDiv.hidden = false;
        }
    });
}

if (manualDateModeSingleRadio) {
    manualDateModeSingleRadio.addEventListener("change", () => {
        if (manualSingleDatePickerDiv) {
            manualSingleDatePickerDiv.hidden = false;
        }
        if (manualRangeDatePickerDiv) {
            manualRangeDatePickerDiv.hidden = true;
        }
    });
}

if (manualDateModeRangeRadio) {
    manualDateModeRangeRadio.addEventListener("change", () => {
        if (manualSingleDatePickerDiv) {
            manualSingleDatePickerDiv.hidden = true;
        }
        if (manualRangeDatePickerDiv) {
            manualRangeDatePickerDiv.hidden = false;
        }
    });
}

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
initializeWatchDatePickers();
syncRangeControls();

// Initialize the diary page
(async () => {
    await fetchTimelineEntries();
    await renderTimeline();
})();
