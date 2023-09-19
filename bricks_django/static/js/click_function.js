$(document).ready(function () {
// Select all elements with the 'item-clickable' class
$('.item-clickable').click(function () {
    // Handle the click event for any clickable item
    window.location.href = '/item/' + $(this).attr('data-item-id');
});
});
