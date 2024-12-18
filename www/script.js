// Ensure code runs only after the page loads
document.addEventListener('DOMContentLoaded', () => {
    // Add a click event listener to the button
    document.getElementById('getDataBtn').addEventListener('click', () => {
        // Fetch messages from the API
        fetch('http://chatforumaiprogramming.be/api.php', {
            method: 'GET'
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            const responseContainer = document.getElementById('responseContainer');
            responseContainer.innerHTML = ''; // Clear previous content

            // Check if the response was successful
            if (data.status === 'success') {
                const messages = data.messages;

                // Loop through each message and add it as a row in the table
                messages.forEach(msg => {
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td>${msg.user}</td>
                        <td>${new Date(msg.dateTime).toLocaleString()}</td>
                        <td>${msg.message}</td>
                    `;
                    responseContainer.appendChild(row);
                });
            } else {
                // Display a message if no messages are found
                responseContainer.innerHTML = '<tr><td colspan="3">Geen berichten gevonden</td></tr>';
            }
        })
        .catch(error => {
            console.error('Error:', error);
            document.getElementById('responseContainer').innerHTML = '<tr><td colspan="3">Er is een fout opgetreden bij het ophalen van berichten.</td></tr>';
        });
    });
});
``
