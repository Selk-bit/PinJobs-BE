document.addEventListener("DOMContentLoaded", function () {
    const groupIdentifierInput = document.querySelector("#id_group_identifier");
    const existingIdentifierDropdown = document.querySelector("#id_existing_identifiers");

    if (groupIdentifierInput && existingIdentifierDropdown) {
        existingIdentifierDropdown.addEventListener("change", function () {
            if (this.value) {
                groupIdentifierInput.value = this.value;  // Auto-fill group identifier
            }
        });
    }
});
