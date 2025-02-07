document.addEventListener("DOMContentLoaded", function () {
    function generateRandomIdentifier(prefix, nameValue) {
        const randomStr = Math.random().toString(36).substring(2, 10); // Generate random alphanumeric string
        const namePart = nameValue.trim().replace(/\s+/g, "_") || ""; // Replace spaces with underscores, default if empty
        return `${prefix}_${namePart}_${randomStr}`;
    }

    function addRandomizationButton(inputField, prefix) {
        const button = document.createElement("button");
        button.type = "button";
        button.textContent = "🔄";
        button.style.marginLeft = "8px";
        button.style.cursor = "pointer";
        button.title = "Generate a random identifier";

        button.addEventListener("click", function () {
            const nameField = document.querySelector("#id_name");
            const nameValue = nameField ? nameField.value : "";
            inputField.value = generateRandomIdentifier(prefix, nameValue);
        });

        inputField.parentNode.appendChild(button);
    }

    const groupIdentifierField = document.querySelector("#id_group_identifier");

    if (groupIdentifierField) {
        addRandomizationButton(groupIdentifierField, "group");
    }
});
