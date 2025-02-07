document.addEventListener("DOMContentLoaded", function () {
    document.body.addEventListener("click", function (event) {
        const addRelatedLink = event.target.closest(".related-widget-wrapper-link.add-related");
        if (!addRelatedLink) return;

        // The normal Django admin "Add another" link
        let popupUrl = addRelatedLink.getAttribute("href");
        if (!popupUrl.includes("_popup=1")) return;

        // Read values from the Question form
        const groupIdentifier = document.querySelector("#id_group_identifier")?.value || "";
        const name = document.querySelector("#id_name")?.value || "";
        const language = document.querySelector("#id_language")?.value || "";

        // Build a new URL with extra GET params
        const urlObj = new URL(popupUrl, window.location.origin);
        if (groupIdentifier) urlObj.searchParams.set("prefill_group_identifier", groupIdentifier);
        if (name) urlObj.searchParams.set("prefill_name", name);
        if (language) urlObj.searchParams.set("prefill_language", language);

        // Update the link and let Django open its normal popup
        addRelatedLink.setAttribute("href", urlObj.toString());
    });
});
