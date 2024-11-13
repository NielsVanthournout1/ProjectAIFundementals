// Zorg ervoor dat de code pas uitvoert nadat de pagina is geladen
document.addEventListener('DOMContentLoaded', () => {
    // Voeg een click-eventlistener toe aan de knop
    document.getElementById('getDataBtn').addEventListener('click', () => {
        // Fetch-aanroep naar de API om berichten op te halen
        fetch('http://chatforumaiprogramming.be/api.php', {
            method: 'GET'
        })
        .then(response => response.json()) // Parse de JSON respons
        .then(data => {
            // Controleer of de respons succesvol is
            if (data.status === 'success') {
                const messages = data.messages;
                const responseContainer = document.getElementById('responseContainer');
                responseContainer.innerHTML = ''; // Verwijder eerdere content

                // Loop door de berichten en voeg elk bericht toe aan de container
                messages.forEach(msg => {
                    const messageElement = document.createElement('div');
                    messageElement.classList.add('message');
                    messageElement.innerHTML = `
                        <div class="user">${msg.user}</div>
                        <div class="dateTime">${new Date(msg.dateTime * 1000).toLocaleString()}</div>
                        <div class="text">${msg.message}</div>
                    `;
                    responseContainer.appendChild(messageElement);
                });
            } else {
                // Geef een foutmelding weer als er geen berichten zijn
                document.getElementById('responseContainer').innerHTML = 'Geen berichten gevonden';
            }
        })
        .catch(error => console.error('Error:', error)); // Toon eventuele fouten in de console
    });
});
