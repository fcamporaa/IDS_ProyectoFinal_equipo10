/* Filtros en vivo por título e ID de género, sin peticiones al backend. */
document.addEventListener('DOMContentLoaded', function () {
    const searchInput = document.getElementById('movieSearchInput');
    const genreFilterBar = document.getElementById('genreFilterBar');
    const movieCards = document.querySelectorAll('.movie-card');
    let selectedGenreId = genreFilterBar
        ? genreFilterBar.querySelector('.genre-chip.active')?.dataset.genreId || ''
        : '';

    function applyFilters() {
        const query = searchInput ? searchInput.value.toLowerCase().trim() : '';
        movieCards.forEach(function (card) {
            const title = card.getAttribute('data-title') || '';
            const genreIds = (card.getAttribute('data-genre-ids') || '').split(',');
            const matchesGenre = !selectedGenreId || genreIds.includes(selectedGenreId);
            const matchesTitle = !query || title.includes(query);
            card.classList.toggle('hidden', !matchesGenre || !matchesTitle);
        });
    }

    if (searchInput) {
        searchInput.addEventListener('input', applyFilters);
    }

    if (genreFilterBar) {
        genreFilterBar.querySelectorAll('.genre-chip').forEach(function (button) {
            button.addEventListener('click', function () {
                selectedGenreId = button.dataset.genreId || '';
                genreFilterBar.querySelectorAll('.genre-chip').forEach(function (chip) {
                    const isActive = chip === button;
                    chip.classList.toggle('active', isActive);
                    chip.setAttribute('aria-pressed', String(isActive));
                });
                applyFilters();
            });
        });
    }

    applyFilters();
});
