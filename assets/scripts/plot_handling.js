document.addEventListener('DOMContentLoaded', function () {
    const selectElement = document.getElementById('beer-style-select');
    const wordCloudImage = document.getElementById('wordcloud-image');
    const loadingSpinner = document.getElementById('loading-spinner');
    
    function updateImage() {
        const selectedStyle = selectElement.value;
        //var base_url = window.location.origin
        var base_path = wordCloudImage.src.substring(0, wordCloudImage.src.lastIndexOf('/'));;
        

        // Show loading spinner and hide the current image
        wordCloudImage.style.visibility = 'hidden';
        loadingSpinner.style.display = 'block';

        // Preload the new image
        const newImage = new Image();
        newImage.src = `${base_path}/${selectedStyle}.svg`;
        // Update the image source and alt text
        wordCloudImage.src = newImage.src;
        wordCloudImage.alt = `${selectedStyle} Word Cloud`;
        newImage.onload = function () {
            // Hide the loading spinner and make the image visible
            loadingSpinner.style.display = 'none';
            wordCloudImage.style.visibility = 'visible';
        };

        // Handle errors (optional)
        newImage.onerror = function () {
            loadingSpinner.style.display = 'none';
            alert("Failed to load the word cloud image. Please try again.");
        };
    }

    // Update image when the dropdown value changes
    selectElement.addEventListener('change', updateImage);

    // Force refresh on page load
    updateImage();
});