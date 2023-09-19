<script>
    function showSuccessMessage() {
        // Show the success message div
        $('#success-message').show();
        
        // Delay hiding the message (you can adjust the duration as needed)
        setTimeout(function () {
            $('#success-message').hide();
        }, 3000); // 3000 milliseconds (3 seconds) in this example
    }
</script>