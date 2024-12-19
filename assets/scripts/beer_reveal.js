document.addEventListener("DOMContentLoaded", function () {
    const popup = document.querySelector('.popup-container');

    function showPopup() {
        popup.classList.add('show'); // Add class to show popup
    }

    function closePopup() {
        popup.classList.remove('show'); // Remove class to hide popup
    }

    // Expose functions globally for button event handlers
    window.showPopup = showPopup;
    window.closePopup = closePopup;
});