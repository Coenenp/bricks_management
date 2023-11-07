document.addEventListener('DOMContentLoaded', function() {
    const typeSelect = document.getElementById('id_TypeID');
    const subtypeSelect = document.getElementById('id_SubtypeID');

    typeSelect.addEventListener('change', async function() {
        const selectedType = this.value;

        if (selectedType) {
            try {
                const response = await fetch(`/get-subtypes/?type=${selectedType}`);
                const data = await response.json();

                subtypeSelect.innerHTML = '';
                data.forEach(subtype => {
                    const option = new Option(subtype.Name, subtype.TypeID.toString());
                    if (subtype.TypeID === parseInt(subtypeSelect.value)) {
                        option.selected = true;
                        subtypeSelect.selectedIndex = subtypeSelect.options.length - 1;
                    }
                    subtypeSelect.appendChild(option);
                    subtypeSelect.appendChild(document.createElement("br"));
                });
            } catch (error) {
                console.error('Error fetching subtype data:', error);
            }
        } else {
            subtypeSelect.innerHTML = '';
        }
    });
    subtypeSelect.addEventListener('change', function() {
        const selectedSubtype = this.value;

        if (selectedSubtype) {

            subtypeSelect.value = selectedSubtype;
        }
    });
});
