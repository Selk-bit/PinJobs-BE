document.addEventListener("DOMContentLoaded", function () {
    function updateAnswerOptions() {
        let questionField = document.querySelector("#id_question");
        let selectedOptionField = document.querySelector("#id_selected_option");
        let selectedOptionsField = document.querySelector("#id_selected_options");
        let textAnswerField = document.querySelector("#id_text_answer");

        if (!questionField || !selectedOptionField || !selectedOptionsField || !textAnswerField) {
            return;
        }

        questionField.addEventListener("change", function () {
            let questionId = questionField.value;

            if (!questionId) {
                clearFields();
                return;
            }

            fetch(`/api/admin/get_answer_options/${questionId}/`)
                .then(response => response.json())
                .then(data => {
                    clearFields();

                    let questionType = data.question_type;  // 🔹 Now using the question type
                    enforceFieldRestrictions(questionType); // 🔹 Apply field restrictions

                    if (data.options.length > 0) {
                        data.options.forEach(option => {
                            let optionElement = new Option(option.text, option.id);
                            if (questionType === "radio") {
                                selectedOptionField.appendChild(optionElement);
                            } else if (questionType === "checkbox") {
                                selectedOptionsField.appendChild(optionElement);
                            }
                        });
                    }
                })
                .catch(error => console.error("Error fetching answer options:", error));
        });

        function clearFields() {
            selectedOptionField.innerHTML = "<option value=''>---------</option>";
            selectedOptionsField.innerHTML = "";
            textAnswerField.value = "";
        }

        function enforceFieldRestrictions(questionType) {
            // Disable all fields initially
            selectedOptionField.disabled = true;
            selectedOptionsField.disabled = true;
            textAnswerField.disabled = true;

            // Enable only the correct field
            if (questionType === "radio") {
                selectedOptionField.disabled = false;
            } else if (questionType === "checkbox") {
                selectedOptionsField.disabled = false;
            } else if (questionType === "text") {
                textAnswerField.disabled = false;
            }
        }
    }

    updateAnswerOptions();
});
