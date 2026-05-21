document.addEventListener("DOMContentLoaded", () => {

    let draggedCard = null;

    document.querySelectorAll(".card").forEach(card => {

        card.addEventListener("dragstart", function(e) {

            draggedCard = this;
            e.stopPropagation();

        });

    });


    document.querySelectorAll(".column").forEach(column => {

        column.addEventListener("dragover", function(e) {

            e.preventDefault();

        });


        column.addEventListener("drop", function() {

            let cardId = draggedCard.dataset.cardId;
            let newColumnId = this.dataset.columnId;

            fetch("/move_card", {

                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({

                    card_id: cardId,
                    column_id: newColumnId

                })

            })
            .then(response => response.json())
            .then(data => {

                location.reload();

            });

        });

    });

});