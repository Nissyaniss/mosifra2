//script pour afficher la prévisualisation du logo avant l'upload
//utilise l'api filereader pour lire le fichier localement sans envoyer au serveur

document.addEventListener("DOMContentLoaded", () => {
    //on cherche l'input file du logo
    const input = document.getElementById("id_organisation_logo");
    const nameSpan = document.getElementById("logo-file-name");
    const previewWrapper = document.getElementById("logo-preview-wrapper");
    const previewImage = document.getElementById("logo-preview-image");
    const previewName = document.getElementById("logo-preview-name");

    if (!input) {
        return;
    }

    input.addEventListener("change", () => {
        const file = input.files && input.files[0];
        if (file) {
            //on affiche le nom du fichier
            nameSpan.textContent = file.name;
            previewName.textContent = file.name;

            //on lit le fichier en base64 pour l'afficher
            const reader = new FileReader();
            reader.onload = (event) => {
                previewImage.src = event.target.result;
                previewWrapper.classList.remove("hidden");
            };
            reader.readAsDataURL(file);
        } else {
            //si on désélectionne le fichier on remet à zéro
            nameSpan.textContent = "Aucun fichier";
            previewWrapper.classList.add("hidden");
            previewImage.src = "";
            previewName.textContent = "";
        }
    });
});
