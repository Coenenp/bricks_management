document.addEventListener("DOMContentLoaded", function() {
    const toggleViewButton = document.getElementById("toggleViewButton");
    const toggleViewUrl = toggleViewButton.getAttribute("data-url");
    const csrfToken = toggleViewButton.getAttribute("data-csrf-token");
    let currentViewMode = toggleViewButton.getAttribute("data-view-mode");

    function refreshPage() {
        // Reload the current page
        window.location.reload();
    }

    toggleViewButton.addEventListener("click", function() {
        // Send an AJAX request to update the view mode
        fetch(toggleViewUrl, {
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
            toggleViewButton.setAttribute("data-view-mode", currentViewMode);
            toggleViewButton.innerHTML = currentViewMode === "array" ?
                '<i class="fas fa-th-large"></i>' : '<i class="fas fa-list"></i>';
            
            // Refresh the page
            refreshPage();
        })
        .catch(error => {
            console.error("Failed to toggle view mode", error);
        });
    });
});
