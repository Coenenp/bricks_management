document.addEventListener("DOMContentLoaded", function() {
    const toggleAggregatedViewButton = document.getElementById("toggleAggregatedViewButton");
    const toggleAggregatedViewUrl = toggleAggregatedViewButton.getAttribute("data-url");
    const csrfToken = toggleAggregatedViewButton.getAttribute("data-csrf-token");
    let currentViewMode = toggleAggregatedViewButton.getAttribute("data-view-mode");

    function refreshPage() {
        // Reload the current page
        window.location.reload();
    }

    toggleAggregatedViewButton.addEventListener("click", function() {
        // Send an AJAX request to update the view mode
        fetch(toggleAggregatedViewUrl, {
            method: "POST",
            headers: {
                "X-CSRFToken": csrfToken,
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ view_mode: currentViewMode }),
        })
        .then(response => response.json())
        .then(data => {
            // Update the view mode on the client side
            currentViewMode = data.new_mode;
            toggleAggregatedViewButton.setAttribute("data-view-mode", currentViewMode);
            toggleAggregatedViewButton.innerHTML = currentViewMode === "aggregated_view" ?
                '<i class="fas fa-square-plus"></i>' : '<i class="fas fa-square-minus"></i>';
            
            // Refresh the page
            refreshPage();
        })
        .catch(error => {
            console.error("Failed to toggle aggregated view mode", error);
        });
    });
});
