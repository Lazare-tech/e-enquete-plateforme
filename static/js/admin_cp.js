function copyToClipboard(id, btn) {
    const copyText = document.getElementById(id);
    if (!copyText) return;

    navigator.clipboard.writeText(copyText.value).then(() => {
        const originalText = btn.innerHTML;
        const originalBg = btn.style.background;
        
        btn.innerHTML = "Copié !";
        btn.style.background = "#28a745"; // Vert succès
        
        setTimeout(() => {
            btn.innerHTML = originalText;
            btn.style.background = originalBg;
        }, 1500);
    }).catch(err => {
        console.error('Erreur lors de la copie : ', err);
    });
}