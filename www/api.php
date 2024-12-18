<?php
// Set header to JSON
header('Content-Type: application/json');

// Database credentials
$servername = "ID453154_messages.db.webhosting.be";
$username = "ID453154_messages";
$password = "V!q665599l";
$dbname = "ID453154_messages";

// Create a connection
$conn = new mysqli($servername, $username, $password, $dbname);

// Check connection
if ($conn->connect_error) {
    die(json_encode(['status' => 'error', 'message' => 'Connection failed: ' . $conn->connect_error]));
}

// Check if it's a GET request (for fetching messages)
if ($_SERVER['REQUEST_METHOD'] == 'GET') {
    $sql = "SELECT user, message, FROM_UNIXTIME(dateTime) AS dateTime FROM messages ORDER BY dateTime DESC LIMIT 10"; // Fetch latest 10 messages
    $result = $conn->query($sql);

    if ($result->num_rows > 0) {
        $messages = [];
        while ($row = $result->fetch_assoc()) {
            $messages[] = [
                'user' => $row['user'],
                'message' => $row['message'],
                'dateTime' => $row['dateTime'] // DateTime is now in human-readable format
            ];
        }
        echo json_encode(['status' => 'success', 'messages' => $messages]);
    } else {
        echo json_encode(['status' => 'error', 'message' => 'No messages found']);
    }
} else {
    // Handle POST requests (for inserting new messages)
    $inputData = json_decode(file_get_contents('php://input'), true);

    if ($inputData && isset($inputData['message']) && isset($inputData['user'])) {
        $user = $inputData['user'];
        $message = $inputData['message'];
        $dateTime = time();

        // Prepare SQL to insert the data into the database
        $stmt = $conn->prepare("INSERT INTO messages (user, message, dateTime) VALUES (?, ?, ?)");
        $stmt->bind_param("ssi", $user, $message, $dateTime);

        if ($stmt->execute()) {
            echo json_encode(['status' => 'success', 'message' => 'Data received and saved successfully']);
        } else {
            echo json_encode(['status' => 'error', 'message' => 'Failed to save data']);
        }

        $stmt->close();
    } else {
        echo json_encode(['status' => 'error', 'message' => 'Invalid data received']);
    }
}

// Close the connection
$conn->close();
?>
